import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

config = context.config
fileConfig(config.config_file_name)

# Read DATABASE_URL directly (bypass ConfigParser to avoid % interpolation issues)
DATABASE_URL = os.environ["DATABASE_URL"]

# Import all models so Alembic can detect them
from app.db.models import Base  # noqa: E402
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
