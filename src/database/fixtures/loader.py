import importlib
import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Base

from .dto import FixtureResult
from .enums import FixtureLoadStatus
from .exceptions import FixtureError


class FixtureLoader:
    """Handles loading of fixture data into database"""

    def __init__(self, db: AsyncSession, models_module: str, logger: logging.Logger):
        """
        Initialize the fixture loader.

        Args:
            db: AsyncSession for database operations
            models_module: String path to the models module (e.g., 'myapp.models')
        """
        self.db = db
        self.models_module = models_module
        self.logger = logger
        self._models_cache: dict[str, type[Base]] = {}
        self._dependencies: dict[str, set[str]] = {}
        self.results: dict[str, FixtureResult] = {}

    def _get_model_class(self, model_name: str) -> type[Base] | None:
        """Get model class by name from the models module"""
        if model_name in self._models_cache:
            return self._models_cache[model_name]

        try:
            module = importlib.import_module(self.models_module)
            model_attr = getattr(module, model_name, None)

            if model_attr is not None and isinstance(model_attr, type) and issubclass(model_attr, Base):
                model_class: type[Base] = model_attr
                self._models_cache[model_name] = model_class
                return model_class

            self.logger.error(f"Model {model_name} not found or not a SQLAlchemy model")
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
        return None

    def _validate_fixture_data(
        self,
        model_class: type[Base],
        data: list[dict[str, Any]],
        unique_fields: list[str],
    ) -> bool:
        """Validate fixture data against model"""
        if not data:
            return False

        # Get model columns
        mapper = inspect(model_class)
        column_names = {c.key for c in mapper.columns}
        relationship_names = {r.key for r in mapper.relationships}
        valid_fields = column_names | relationship_names

        # Validate each record
        for record in data:
            # Check required fields
            missing_fields = [field for field in unique_fields if field not in record]
            if missing_fields:
                self.logger.error(f"Missing required fields {missing_fields} in record: {record}")
                return False

            # Check field validity
            invalid_fields = [field for field in record if field not in valid_fields]
            if invalid_fields:
                self.logger.error(f"Invalid fields {invalid_fields} for model {model_class.__name__}")
                return False

        return True

    async def _process_record(
        self,
        model_class: type[Base],
        record: dict[str, Any],
        unique_fields: list[str],
        result: FixtureResult,
    ) -> None:
        """Process a single record from fixture data"""
        try:
            # Create filter conditions for unique fields
            filter_conditions = [
                getattr(model_class, field) == record[field] for field in unique_fields if field in record
            ]

            if not filter_conditions:
                raise FixtureError(f"No unique fields found in record: {record}")

            # Check if record exists
            stmt = select(model_class).where(*filter_conditions)
            existing = await self.db.execute(stmt)
            obj = existing.scalar_one_or_none()

            if obj:
                # Update existing record
                for key, value in record.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                result.updated += 1
                self.logger.debug(f"Updated existing {model_class.__name__} record: {record}")
            else:
                # Create new record
                obj = model_class(**record)
                self.db.add(obj)
                result.created += 1
                self.logger.debug(f"Created new {model_class.__name__} record: {record}")

        except Exception as e:
            result.failed += 1
            result.errors.append(f"Error processing record {record}: {e!s}")
            self.logger.error(f"Error processing record: {e}")
            await self.db.rollback()
            raise

    async def load_fixture(self, fixture_path: Path) -> FixtureResult:
        """
        Load a single fixture file.

        Args:
            fixture_path: Path to the fixture file

        Returns:
            FixtureResult: Result of the loading operation
        """
        result = FixtureResult(fixture_path.name)

        try:
            with open(fixture_path, encoding="utf-8") as f:
                fixture_data = json.load(f)

            model_name = fixture_data.get("model")
            unique_fields = fixture_data.get("unique_fields", [])
            data = fixture_data.get("data", [])

            self.logger.info(f"Loading fixture: {fixture_path.name} for model {model_name}")

            # Get and validate model
            model_class = self._get_model_class(model_name)
            if not model_class:
                result.errors.append(f"Model {model_name} not found")
                return result

            # Validate data
            if not self._validate_fixture_data(model_class, data, unique_fields):
                result.errors.append("Data validation failed")
                return result

            # Process records
            for record in data:
                try:
                    await self._process_record(model_class, record, unique_fields, result)
                except Exception as e:
                    result.errors.append(str(e))

            # Commit changes
            try:
                await self.db.commit()
                if result.failed == 0:
                    result.status = FixtureLoadStatus.SUCCESS
                else:
                    result.status = FixtureLoadStatus.PARTIAL
            except SQLAlchemyError as e:
                await self.db.rollback()
                result.errors.append(f"Commit failed: {e!s}")
                result.status = FixtureLoadStatus.FAILED

        except Exception as e:
            result.errors.append(f"Fixture loading failed: {e!s}")
            self.logger.error(f"Error loading fixture {fixture_path}: {e}")

        # Log results
        self.logger.info(
            f"Processed {fixture_path.name}: "
            f"created {result.created}, "
            f"updated {result.updated}, "
            f"failed {result.failed}",
        )
        if result.errors:
            self.logger.error(f"Errors in {fixture_path.name}: {result.errors}")

        return result

    async def load_all_fixtures(self, fixtures_dir: Path, ignore_errors: bool = False) -> dict[str, FixtureResult]:
        """
        Load all fixture files from a directory.

        Args:
            fixtures_dir: Path to the fixtures directory
            ignore_errors: Whether to continue loading if a fixture fails

        Returns:
            Dict[str, FixtureResult]: Results of all loading operations
        """
        self.results = {}

        if not fixtures_dir.exists():
            self.logger.warning(f"Fixtures directory not found: {fixtures_dir}")
            return self.results

        self.logger.info(f"Starting to load all fixtures from {fixtures_dir}")

        # Load fixtures in sorted order
        fixture_files = sorted(fixtures_dir.glob("*.json"))

        for fixture_file in fixture_files:
            result = await self.load_fixture(fixture_file)
            self.results[fixture_file.name] = result

            if not result.is_successful and not ignore_errors:
                self.logger.error(f"Stopping fixture loading due to failure in {fixture_file.name}")
                break

        # Log summary
        successful = sum(1 for r in self.results.values() if r.is_successful)
        total = len(self.results)

        if total > 0:
            if successful == total:
                self.logger.info(f"Successfully loaded all {total} fixtures! 🎉")
            else:
                self.logger.warning(
                    f"Loaded {successful} out of {total} fixtures successfully. "
                    f"Failed fixtures: "
                    f"{[k for k, v in self.results.items() if not v.is_successful]}",
                )
        else:
            self.logger.info("No fixtures found to load")

        return self.results

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all fixture loading operations"""
        total_stats = {
            "created": sum(r.created for r in self.results.values()),
            "updated": sum(r.updated for r in self.results.values()),
            "failed": sum(r.failed for r in self.results.values()),
            "total_fixtures": len(self.results),
            "successful_fixtures": sum(1 for r in self.results.values() if r.is_successful),
        }

        return {"stats": total_stats, "fixtures": {name: result.to_dict() for name, result in self.results.items()}}
