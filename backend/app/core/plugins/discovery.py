import json
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "plugins"

def discover_plugins():
    plugins = {}

    for path in PLUGIN_DIR.iterdir():
        if not path.is_dir():
            continue

        descriptor = path / "plugin.json"
        if not descriptor.exists():
            continue

        data = json.loads(descriptor.read_text())
        plugins[data["name"]] = {
            "path": path,
            "meta": data,
        }
    return plugins
