# migrations/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# --- Start: Robust sys.path adjustment ---
# Get the absolute path to the directory containing env.py (migrations/)
current_dir = os.path.abspath(os.path.dirname(__file__))
# Get the absolute path to the project root (campaign-service/)
project_root = os.path.join(current_dir, "..")

# Add the project root to sys.path
# Insert at the beginning for priority to ensure local modules are found first
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add the 'app' directory to sys.path as well, just in case
app_dir = os.path.join(project_root, "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# --- End: Robust sys.path adjustment ---

# Import your Base and settings
try:
    from app.models.base import Base
    from app.core.config import settings
    # Import all your models so Alembic can discover them
    from app.models import campaign
    from app.models import user_enums
    # Add any other model files you create later, e.g.:
    # from app.models import some_other_campaign_related_model
except ImportError as e:
    print(f"Error importing application modules: {e}")
    print(f"sys.path: {sys.path}")
    # This print will help diagnose if the imports themselves are failing
    raise # Re-raise the error to stop execution if imports fail

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# --- Custom function to filter objects for autogenerate ---
def include_object(object, name, type_, reflected, comparable_in_diff):
    """
    Filter objects for autogenerate.
    Exclude foreign keys that reference tables outside the current schema.
    """
    if type_ == "foreign_key":
        # Debugging print: See what foreign keys Alembic is trying to process
        print(f"Alembic processing FK: {name}, type: {type_}, "
              f"referred_table: {object.referred_table.schema}.{object.referred_table.name if object.referred_table else 'N/A'}")

        # Check if the foreign key references a table outside the 'campaigns' schema
        # This assumes your campaign models are the only ones in 'campaigns' schema
        # and other schemas are managed by other services.
        if object.referred_table and object.referred_table.schema != 'campaigns':
            print(f"IGNORING foreign key {name} referencing external schema {object.referred_table.schema}.{object.referred_table.name}")
            return False # Exclude this foreign key from autogenerate
    return True # Include all other objects
# --- End custom function ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            render_as_batch=True,
            # Pass the include_object function directly here
            # This is the most critical part for filtering
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
