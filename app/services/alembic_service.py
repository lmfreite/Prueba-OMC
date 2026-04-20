from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from app.core.settings import settings


class AlembicService:
    """Gestiona verificacion y ejecucion de migraciones Alembic."""

    @staticmethod
    def check_and_apply_migrations() -> None:
        """Aplica migraciones pendientes si la revision actual no esta en head."""
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.ALEMBIC_DATABASE_URL)

        script = ScriptDirectory.from_config(alembic_cfg)
        engine = create_engine(settings.ALEMBIC_DATABASE_URL)

        try:
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                heads = script.get_heads()

                if current_rev in heads:
                    return

            command.upgrade(alembic_cfg, "head")
        finally:
            engine.dispose()
