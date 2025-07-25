"""move to custom schema

Revision ID: 8173f0949f2e
Revises: 00566833d2e0
Create Date: 2025-07-22 14:03:01.729742

"""
import importlib.util
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '8173f0949f2e'
down_revision = '00566833d2e0'
branch_labels = None
depends_on = None

# Configure structured logging for migration
try:
    # Add the src directory to the path so we can import auth_api modules
    current_dir = Path(__file__).parent.parent.parent
    src_dir = current_dir / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Import and setup structured logging
    from auth_api.config import _Config
    from auth_api.utils.logging import setup_logging

    # Setup structured logging using the same config as the main app
    logging_conf_path = os.path.join(_Config.PROJECT_ROOT, "logging.conf")
    setup_logging(logging_conf_path)

    # Get a logger that will use the structured format
    logger = logging.getLogger('auth_api')
except ImportError as e:
    # Fallback to basic logging if structured logging setup fails
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not setup structured logging, using basic logging: {e}")

def get_table_dependencies(conn, schema='public'):
    """Build a dependency graph of tables based on foreign keys."""
    # Get all tables in schema
    tables = conn.execute(text(f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{schema}'
        AND table_type = 'BASE TABLE'
    """)).fetchall()

    # Build dependency graph
    graph = defaultdict(set)
    tables_with_fks = conn.execute(text(f"""
        SELECT tc.table_name, ccu.table_name as referenced_table
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = '{schema}'
    """)).fetchall()

    for table, referenced_table in tables_with_fks:
        graph[table].add(referenced_table)

    return graph, [t[0] for t in tables]

def topological_sort(graph, nodes):
    """Topologically sort tables based on foreign key dependencies."""
    visited = set()
    result = []

    def visit(node):
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                visit(neighbor)
            result.append(node)

    for node in nodes:
        visit(node)

    return result

def copy_data_with_dependencies(conn, target_schema):
    """Copy data respecting foreign key constraints with row count verification."""
    # Get dependency graph for public schema
    graph, all_tables = get_table_dependencies(conn, 'public')

    # Get topological order for copying
    copy_order = topological_sort(graph, all_tables)
    logger.info(f"Determined copy order: {copy_order}")

    # Dictionary to track row counts
    row_counts = {}

    for table_name in copy_order:
        try:
            # Check if table exists in target schema
            exists_in_target = conn.execute(text(f"""
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = '{target_schema}'
                AND table_name = '{table_name}'
            """)).scalar()

            if not exists_in_target:
                logger.info(f"Skipping {table_name} - not in target schema")
                continue

            # Get source row count
            source_count = conn.execute(
                text(f"SELECT COUNT(*) FROM public.{table_name}")
            ).scalar()
            row_counts[table_name] = {'source': source_count}

            # Skip if target has data (but verify counts match)
            target_has_data = conn.execute(
                text(f"SELECT EXISTS (SELECT 1 FROM {target_schema}.{table_name} LIMIT 1)")
            ).scalar()

            if target_has_data:
                target_count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {target_schema}.{table_name}")
                ).scalar()
                if source_count != target_count:
                    logger.warning(
                        f"Table {table_name} has data but counts don't match "
                        f"(public: {source_count}, {target_schema}: {target_count}). "
                        f"Skipping this table."
                    )
                    continue
                logger.info(f"Skipping {table_name} - target already has matching data")
                continue

            # Get all columns with proper quoting
            columns = conn.execute(text(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = '{target_schema}'
                AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """)).fetchall()

            if not columns:
                logger.warning(f"No columns found for {target_schema}.{table_name}")
                continue

            # Build properly quoted column list
            quoted_columns = [f'"{col[0]}"' for col in columns]
            columns_str = ", ".join(quoted_columns)

            # Copy data
            logger.info(f"Copying data to {target_schema}.{table_name}")
            conn.execute(text(f"""
                INSERT INTO {target_schema}.{table_name} ({columns_str})
                SELECT {columns_str} FROM public.{table_name}
            """))

            # Verify target row count
            target_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {target_schema}.{table_name}")
            ).scalar()
            row_counts[table_name]['target'] = target_count

            if source_count != target_count:
                logger.error(
                    f"Row count mismatch after copy for {table_name} "
                    f"(public: {source_count}, {target_schema}: {target_count})"
                )

        except Exception as e:
            logger.error(f"Error processing table {table_name}: {str(e)}")
            # Don't explicitly ROLLBACK here - let Alembic handle the transaction
            raise  # Re-raise to ensure Alembic marks the migration as failed

    logger.info("All tables processed successfully")
    logger.debug(f"Row count verification: {row_counts}")


def get_target_schema():
    """Minimal schema name fetch with validation."""
    schema = os.getenv("DATABASE_SCHEMA", "public")
    if not re.match(r'^[a-z_][a-z0-9_]*$', schema, re.I):
        raise ValueError(f"Invalid schema name: {schema}")
    return schema

def load_migration_module(file_path):
    """Load a migration module from file."""
    spec = importlib.util.spec_from_file_location(f"migration_{file_path.stem}", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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
        
        # Create alembic_version table in new public schema
        conn.execute(text("""
            CREATE TABLE public.alembic_version (
                version_num character varying(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        
        # Insert the down_revision value (previous migration)
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

    # Skip if target schema is public
    if target_schema == 'public':
        logger.info("Target schema is public, skipping downgrade")
        return

    conn = op.get_bind()

    try:
        # Check if schema exists
        schema_exists = conn.execute(
            text(f"SELECT 1 FROM information_schema.schemata WHERE schema_name = '{target_schema}'")
        ).scalar()

        if not schema_exists:
            logger.info(f"Schema {target_schema} does not exist, nothing to downgrade")
            return

        # 1. Drop the current public schema (which is empty/minimal)
        logger.info("Dropping current public schema")
        conn.execute(text("DROP SCHEMA public CASCADE"))

        # 2. Rename the target schema back to public
        logger.info(f"Renaming {target_schema} back to public")
        conn.execute(text(f"ALTER SCHEMA {target_schema} RENAME TO public"))

        logger.info("Downgrade completed successfully")
    except Exception as e:
        logger.error(f"Downgrade failed: {str(e)}")
        raise
