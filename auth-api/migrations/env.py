from __future__ import with_statement

import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app
from sqlalchemy import text

from auth_api.config import MigrationConfig

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

def get_engine():
    try:
        return current_app.extensions["migrate"].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions["migrate"].db.engine

def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")

config.set_main_option("sqlalchemy.url", get_engine_url())
target_metadata = current_app.extensions["migrate"].db.metadata

def get_list_from_config(config, key):
    arr = config.get_main_option(key, [])
    if arr:
        arr = [token for a in arr.split("\n") for b in a.split(",") if (token := b.strip())]
    return arr

exclude_tables = get_list_from_config(config, "exclude_tables")

def include_object(object, name, type_, reflected, compare_to):
    return not (type_ == "table" and name in exclude_tables)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    connectable = get_engine()

    with connectable.connect() as connection:
        # Get existing configure args but remove compare_type if present
        configure_args = current_app.extensions["migrate"].configure_args or {}
        if 'compare_type' in configure_args:
            del configure_args['compare_type']

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            include_object=include_object,
            compare_type=True,  # Only set here explicitly
            **configure_args
        )

        with context.begin_transaction():
            owner_role = MigrationConfig.DATABASE_OWNER
            connection.execute(text(f"SET ROLE {owner_role};"))
            result = connection.execute(text("SELECT current_user, session_user;"))
            logger.info(f"User running migration is: {result.fetchone()}")
            context.run_migrations()
            connection.execute(text("RESET ROLE;"))

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()