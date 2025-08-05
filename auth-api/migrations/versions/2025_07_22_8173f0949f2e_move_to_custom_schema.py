"""move to custom schema

Revision ID: 8173f0949f2e
Revises: 00566833d2e0
Create Date: 2025-07-22 14:03:01.729742

"""
import logging
import os
import re

from alembic import op
from flask import current_app
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '8173f0949f2e'
down_revision = '00566833d2e0'
branch_labels = None
depends_on = None

logger = current_app.logger if hasattr(current_app, 'logger') else logging.getLogger("auth_api")

def get_target_schema():
    """Minimal schema name fetch with validation."""
    schema = os.getenv("DATABASE_SCHEMA", "public")
    if not re.match(r'^[a-z_][a-z0-9_]*$', schema, re.I):
        raise ValueError(f"Invalid schema name: {schema}")
    return schema

def upgrade():
    target_schema = get_target_schema()
    if target_schema == 'public':
        logger.info("Target schema is public, skipping migration")
        return

    conn = op.get_bind()

    try:
        # Check if target schema already exists
        schema_exists = conn.execute(text(f"""
            SELECT 1 FROM information_schema.schemata
            WHERE schema_name = '{target_schema}'
        """)).scalar()

        if schema_exists:
            logger.info(f"Schema {target_schema} already exists, skipping migration")
            return

        conn.execute(text(f"ALTER SCHEMA public RENAME TO {target_schema};"))
        conn.execute(text("CREATE SCHEMA public;"))
        
        conn.execute(text("""
            CREATE TABLE public.alembic_version (
                version_num character varying(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        
        conn.execute(text(f"""
            INSERT INTO public.alembic_version (version_num) 
            VALUES ('{down_revision}')
        """))
        conn.commit()

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        conn.rollback()
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text(f"ALTER SCHEMA {target_schema} RENAME TO public"))
        conn.commit()
        raise


def downgrade():
    target_schema = get_target_schema()

    if target_schema == 'public':
        logger.info("Target schema is public, skipping downgrade")
        return

    conn = op.get_bind()

    try:
        schema_exists = conn.execute(
            text(f"SELECT 1 FROM information_schema.schemata WHERE schema_name = '{target_schema}'")
        ).scalar()

        if not schema_exists:
            logger.info(f"Schema {target_schema} does not exist, nothing to downgrade")
            return

        logger.info("Dropping current public schema")
        conn.execute(text("DROP SCHEMA public CASCADE"))

        logger.info(f"Renaming {target_schema} back to public")
        conn.execute(text(f"ALTER SCHEMA {target_schema} RENAME TO public"))

        logger.info("Downgrade completed successfully")
    except Exception as e:
        logger.error(f"Downgrade failed: {str(e)}")
        raise
