"""move to custom schema

Revision ID: 8173f0949f2e
Revises: 00566833d2e0
Create Date: 2025-07-22 14:03:01.729742

"""
import importlib.util
import logging
import os
import re
import subprocess
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
    postgres_bin_path = "/usr/local/Cellar/postgresql@15/15.13/bin/"

    try:
        from sqlalchemy.engine.url import make_url
        url = make_url(conn.engine.url)
        logger.info("URL is %s", url)

        import shutil
        import tempfile

        # Create temporary files
        schema_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.sql', delete=False)
        modified_schema_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.sql', delete=False)
        data_file = tempfile.NamedTemporaryFile(suffix='.dump', delete=False)  # Binary format for data
        
        try:
            # 1. Dump SCHEMA in plain text for modification
            schema_dump_cmd = [
                f"{postgres_bin_path}pg_dump",
                f"--host={url.host}" if url.host else "",
                f"--port={url.port}" if url.port else "",
                f"--username={url.username}" if url.username else "",
                f"--dbname={url.database}",
                "--format=plain",
                "--schema-only",
                "--schema=public",
                "--no-comments",
                f"--file={schema_file.name}"
            ]
            
            logger.info(f"Executing schema dump: {' '.join(schema_dump_cmd)}")
            subprocess.run(
                [arg for arg in schema_dump_cmd if arg],
                check=True,
                env={'PGPASSWORD': url.password} if url.password else None
            )

            # 2. Dump DATA in binary format for performance
            data_dump_cmd = [
                f"{postgres_bin_path}pg_dump",
                f"--host={url.host}" if url.host else "",
                f"--port={url.port}" if url.port else "",
                f"--username={url.username}" if url.username else "",
                f"--dbname={url.database}",
                "--format=custom",
                "--data-only",
                "--schema=public",
                f"--file={data_file.name}"
            ]
            
            logger.info(f"Executing data dump: {' '.join(data_dump_cmd)}")
            subprocess.run(
                [arg for arg in data_dump_cmd if arg],
                check=True,
                env={'PGPASSWORD': url.password} if url.password else None
            )

            # 3. Modify the schema file to change references
            with open(schema_file.name, 'r') as f_in, open(modified_schema_file.name, 'w') as f_out:
                content = f_in.read()

                # Show first few lines for debugging
                first_few_lines = content.split('\n')[:15]
                logger.info("Dump file starts with:\n%s", '\n'.join(first_few_lines))


                # Replace public schema references with target schema
                modified_content = content.replace('public.', f'{target_schema}.')

                # IMPORTANT: Fix UUID function references back to public schema
                modified_content = modified_content.replace(f'{target_schema}.uuid_generate_v4()', 'public.uuid_generate_v4()')

                # Remove CREATE SCHEMA statements
                modified_content = modified_content.replace('ALTER SCHEMA public OWNER TO pg_database_owner;', '')
                modified_content = modified_content.replace('CREATE SCHEMA public;', f'CREATE SCHEMA IF NOT EXISTS {target_schema};')

                logger.debug(modified_content[:500])  # Log first 500 chars for debugging

                # 4. Create debug copies
                shutil.copy2(f_out.name, "./debug_schema_modified.sql")
                logger.info("Saved modified schema to debug_schema_modified.sql")

                f_out.write(modified_content)


                # 6. Restore modified schema using psql
                schema_restore_cmd = [
                    '/usr/local/opt/libpq/bin/psql',
                    f"--host={url.host}" if url.host else "",
                    f"--port={url.port}" if url.port else "",
                    f"--username={url.username}" if url.username else "",
                    f"--dbname={url.database}",
                    "--quiet",
                    "--single-transaction",
                    f"--file={f_out.name}"
                ]
            
            logger.info(f"Executing schema restore: {' '.join(schema_restore_cmd)}")
            schema_result = subprocess.run(
                [arg for arg in schema_restore_cmd if arg],
                env={'PGPASSWORD': url.password} if url.password else None,
                capture_output=True,
                text=True
            )

            if schema_result.returncode != 0:
                logger.error(f"Schema restore failed: {schema_result.stderr}")
                raise Exception(f"Schema restore failed: {schema_result.stderr}")

            # 7. Restore data using pg_restore with binary format
            data_restore_cmd = [
                f"{postgres_bin_path}pg_restore",
                f"--host={url.host}" if url.host else "",
                f"--port={url.port}" if url.port else "",
                f"--username={url.username}" if url.username else "",
                f"--dbname={url.database}",
                "--single-transaction",
                f"--schema={target_schema}",  # This loads data into the target schema
                data_file.name
            ]
            
            logger.info(f"Executing data restore: {' '.join(data_restore_cmd)}")
            data_result = subprocess.run(
                [arg for arg in data_restore_cmd if arg],
                env={'PGPASSWORD': url.password} if url.password else None,
                capture_output=True,
                text=True
            )

            if data_result.returncode != 0:
                logger.error(f"Data restore failed: {data_result.stderr}")
                raise Exception(f"Data restore failed: {data_result.stderr}")

            logger.info("Migration completed successfully")

        finally:
            # Clean up temporary files
            for f in [schema_file, modified_schema_file, data_file]:
                try:
                    os.unlink(f.name)
                except FileNotFoundError:
                    pass

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.decode('utf-8') if e.stderr else str(e)}")
        raise Exception("Migration failed") from e
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


def upgrade2():
    target_schema = get_target_schema()
    if target_schema == 'public':
        logger.info("Target schema is public, skipping migration")
        return

    conn = op.get_bind()

    try:
        # 1. Get database connection parameters
        from sqlalchemy.engine.url import make_url
        url = make_url(conn.engine.url)
        logger.info("URL is %s", url)

        # 2. Use a temporary file for more reliable transfer
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.sql', delete=False) as tmp_file:
            # 4. Build and execute pg_dump command
            dump_cmd = [
                '/usr/local/Cellar/postgresql@15/15.13/bin/pg_dump',
                f"--host={url.host}" if url.host else "",
                f"--port={url.port}" if url.port else "",
                f"--username={url.username}" if url.username else "",
                f"--dbname={url.database}",
                "--schema-only",
                "--schema=public",
                "--no-comments",
                # "--no-owner",
                # "--no-privileges",
                f"--file={tmp_file.name}"
            ]

            # Remove empty arguments
            dump_cmd = [arg for arg in dump_cmd if arg]

            # Execute pg_dump
            result = subprocess.run(
                dump_cmd,
                check=True,
                env={'PGPASSWORD': url.password} if url.password else None,
                stderr=subprocess.PIPE
            )

            logger.debug(f"pg_dump stdout: {result.stdout}")
            logger.debug(f"pg_dump stderr: {result.stderr}")

            # After pg_dump completes:
            file_size = os.path.getsize(tmp_file.name)
            logger.info(f"pg_dump file size: {file_size} bytes")

            if file_size == 0:
                logger.warning("pg_dump failed: Output file is empty!")
                return
            
            import shutil
            local_copy_path = f"./pg_dump_output_{target_schema}.sql"
            shutil.copy2(tmp_file.name, local_copy_path)
            logger.info(f"Saved pg_dump output to: {local_copy_path}")

        # 3. Modify the SQL file to use target schema (outside the with block but before deletion)
        try:
            with open(tmp_file.name, 'r') as f:
                content = f.read()

                # Show first few lines for debugging
                first_few_lines = content.split('\n')[:15]
                logger.info("Dump file starts with:\n%s", '\n'.join(first_few_lines))


                # Replace public schema references with target schema
                modified_content = content.replace('public.', f'{target_schema}.')

                # IMPORTANT: Fix UUID function references back to public schema
                modified_content = modified_content.replace(f'{target_schema}.uuid_generate_v4()', 'public.uuid_generate_v4()')

                # Fix PostgreSQL version issues
                modified_content = modified_content.replace('SET transaction_timeout = 0;', '\n')

                # Remove CREATE SCHEMA statements
                modified_content = modified_content.replace('ALTER SCHEMA public OWNER TO pg_database_owner;', '')
                modified_content = modified_content.replace('CREATE SCHEMA public;', f'CREATE SCHEMA IF NOT EXISTS {target_schema};')

                logger.debug(modified_content[:500])  # Log first 500 chars for debugging
                with open(tmp_file.name, 'w') as f:
                    f.write(modified_content)

                import shutil
                local_copy_path = f"./pg_dump_output_modified_{target_schema}.sql"
                shutil.copy2(tmp_file.name, local_copy_path)
                logger.info(f"Saved modified pg_dump output to: {local_copy_path}")

                # 4. Load the modified SQL with simplified psql command
                # TODO add to Dockerfile and figure out path
                load_cmd = [
                    '/usr/local/Cellar/postgresql@15/15.13/bin/psql',
                    f"--host={url.host}" if url.host else "",
                    f"--port={url.port}" if url.port else "",
                    f"--username={url.username}" if url.username else "",
                    f"--dbname={url.database}",
                    "--quiet",
                    "--single-transaction",
                    f"--file={tmp_file.name}"
                ]

                # Remove empty arguments
                load_cmd = [arg for arg in load_cmd if arg]

                logger.info(f"Executing psql command: {' '.join(load_cmd)}")

                # Execute psql
                result = subprocess.run(
                    load_cmd,
                    env={'PGPASSWORD': url.password} if url.password else None,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    logger.error(f"psql stderr: {result.stderr}")
                    raise Exception(f"Schema load failed: {result.stderr}")

                logger.info("Schema structure loaded successfully")

        finally:
            # Clean up the temporary file
            try:
                os.unlink(tmp_file.name)
            except FileNotFoundError:
                pass

        # 5. Copy data
        # TODO should pg_dump be also used for data?

        tables_in_target = conn.execute(text(f"""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = '{target_schema}'
        """)).fetchall()
        logger.info(f"Tables found in {target_schema} after psql: {[t[0] for t in tables_in_target]}")
        

        copy_data_with_dependencies(conn, target_schema)

        logger.info("Migration completed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.decode('utf-8') if e.stderr else str(e)}")
        raise Exception("Schema copy failed") from e
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
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

        # Then drop the schema
        logger.info(f"Dropping schema {target_schema}")
        conn.execute(text(f"DROP SCHEMA {target_schema} CASCADE"))

        logger.info("Downgrade completed successfully")
    except Exception as e:
        logger.error(f"Downgrade failed: {str(e)}")
        raise
