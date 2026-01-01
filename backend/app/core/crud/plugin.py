import uuid
from typing import Any, List, Dict

from sqlmodel import Session, select, delete
from app.core.db.schemas.plugin import PluginDiscover, PluginMeta, PluginDownload
from app.core.db.models.plugin import Plugin
from app.core.plugins.discovery import discover_plugins

import zipfile
import aiohttp
import shutil
import asyncio
import subprocess
from pathlib import Path
import tarfile


def list_downloaded() -> List[PluginDiscover]:
    discovered = discover_plugins()
    plugins : List[PluginDiscover] = []
    for key in discovered:
        meta = discovered[key]['meta']
        plugin_meta = PluginMeta(
            name=meta["name"],
            version=meta["version"],
            description=meta["description"],
            db_schema=meta["schema"]
        )
        data = PluginDiscover(
            name=meta["name"],
            path=discovered[key]['path'].as_uri(),
            meta=plugin_meta
        )
        plugins.append(data)
    
    return plugins

def synchronize_plugins(*, session: Session) -> int:
    
    discovered_plugins: Dict[str, dict] = discover_plugins()
    if not discovered_plugins:
        return 0
    stmt = select(Plugin)
    stored_plugins = session.exec(stmt).all()
    stored_by_name = {p.name: p for p in stored_plugins}

    changed = 0

    for name, info in discovered_plugins.items():
        meta = info["meta"]
        disk_name = meta.get("name")

        # Sanity: enforce consistent naming
        if disk_name != name:
            # You can choose to raise instead of silently skipping
            raise ValueError(f"Descriptor name '{disk_name}' does not match directory key '{name}'")

        existing = stored_by_name.get(disk_name)
        update_data = {
            "name": name,
            "description": meta.get("description"),
            "version": meta.get("version", "unknown"),
            "schema": meta.get("schema", name)
        }
        if existing is None:
            # Insert new plugin, disabled by default
            plugin = Plugin(**update_data, enabled=False)
            session.add(plugin)
            changed += 1 
        else:
            # Update metadata if changed; preserve enabled flag
            for key, value in update_data.items():
                setattr(existing, key, value)
            changed += 1 

    if changed > 0:
        session.commit()

    return changed

def get_plugin_by_name(session: Session, name: str) -> Plugin | None:
    stmt = select(Plugin).where(Plugin.name == name)
    return session.exec(stmt).first()

def set_plugin_enabled(session: Session, name: str, enabled: bool) -> tuple[bool, Plugin]:
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise ValueError(f"Plugin '{name}' not found in DB")

    plugin.enabled = enabled
    session.add(plugin)
    session.commit()
    session.refresh(plugin)
    return enabled, plugin 

def delete_plugin(session: Session, name: str) -> Plugin | None:
    stmt = delete(Plugin).where(Plugin.name == name)
    session.exec(stmt)
    session.commit()
    return True

async def download_and_extract_archive(details: PluginDownload, session: Session):
    """Download ONE specific archive → extract based on type."""
    
    target_dir = Path("app/plugins") / details.id
    
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    archive_path = None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(details.archive_url) as resp:
                if resp.status != 200:
                    print(f"❌ HTTP {resp.status}: {details.archive_url}")
                    return
                
                content = await resp.read()
                archive_path = target_dir / f"temp.{details.archive_type}"
                target_dir.mkdir(parents=True, exist_ok=True)
                
                with open(archive_path, "wb") as f:
                    f.write(content)
                
                print(f"✓ Downloaded {details.archive_url}")
        
        # Extract based on EXACT type
        extract_archive(archive_path, target_dir, details.archive_type)
        
    except Exception as e:
        print(f"❌ Failed {details.archive_url}: {e}")
    finally:
        if archive_path and archive_path.exists():
            archive_path.unlink()
        synchronize_plugins(session)
        
def extract_archive(archive_path: Path, target_dir: Path, archive_type: str):
    """Extract based on catalog archive_type."""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    if archive_type == "zip":
        with zipfile.ZipFile(archive_path, 'r') as z:
            z.extractall(target_dir)
    
    elif archive_type in ("tar.gz", "tgz"):
        with tarfile.open(archive_path, 'r:gz') as t:
            t.extractall(target_dir)
    
    elif archive_type == "tar":
        with tarfile.open(archive_path, 'r') as t:
            t.extractall(target_dir)
    
    else:
        raise ValueError(f"Unknown archive_type: {archive_type}")
    
    print(f"✓ Extracted {archive_type} → {target_dir}")

def ensure_plugin_schema(session: Session, schema_name: str):
    """CREATE SCHEMA IF NOT EXISTS + idempotent grants."""
    # Schema creation (safe to run 100x)
    session.exec(f"""
        CREATE SCHEMA IF NOT EXISTS {schema_name};
    """)
    
    # Grants (safe to run 100x - no error on duplicate)
    session.exec(f"""
        GRANT ALL PRIVILEGES ON SCHEMA {schema_name} TO current_user;
        GRANT USAGE, CREATE ON SCHEMA {schema_name} TO current_user;
    """)
    
    # Default privileges (safe idempotent)
    session.exec(f"""
        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} 
        GRANT ALL PRIVILEGES ON TABLES TO current_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} 
        GRANT ALL PRIVILEGES ON SEQUENCES TO current_user;
    """)
    
    session.commit()

def drop_plugin_schema(session: Session, schema_name: str):
    """DROP SCHEMA CASCADE (uninstall only)."""
    session.exec(f"""
        DROP SCHEMA IF EXISTS {schema_name} CASCADE;
    """)
    session.commit()

def run_plugin_migrations(session: Session, plugin: Plugin):
    alembic_dir = Path("app/core/alembic")

    check_result = subprocess.run(
        ["alembic", "check"], 
        cwd=alembic_dir, 
        capture_output=True, 
        text=True
    )
    
    migration_generated = False
    
    if check_result.returncode != 0:  # Changes detected!
        # AUTO revision
        subprocess.run([
            "alembic", "revision", "--autogenerate", 
            f"-m", f"{plugin.name}: tables"
        ], cwd=alembic_dir, check=True, capture_output=True)
        migration_generated = True
        print(f"✓ Generated migration for {plugin.name}")
    else:
        print(f"✓ No schema changes for {plugin.name}")
    
    # 3. ALWAYS upgrade (safe, fast if current)
    subprocess.run([
        "alembic", "upgrade", "head"
    ], cwd=alembic_dir, check=True, capture_output=True)
    
    # 4. Enable
    plugin.enabled = True
    session.commit()