"""Adapters package — auto-discover all source adapters."""
from pathlib import Path
import pkgutil
import importlib

# Registry of all adapters
_REGISTRY = {}


def _auto_discover():
    """Import all adapter modules in this package."""
    package_dir = Path(__file__).parent
    for _, name, _ in pkgutil.iter_modules([str(package_dir)]):
        if name.startswith("_") or name in ("__init__", "base"):
            continue
        try:
            mod = importlib.import_module(f"oracle.adapters.{name}")
            # Find adapter class (any class with 'id' attribute)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and hasattr(attr, "id") and hasattr(attr, "discover"):
                    _REGISTRY[attr.id] = attr
        except Exception:
            pass


_auto_discover()


def get_all_adapters() -> dict:
    """Return all discovered adapters: {id: class}."""
    return dict(_REGISTRY)


def get_adapter(adapter_id: str):
    """Get a specific adapter class by ID."""
    return _REGISTRY.get(adapter_id)


def list_adapter_ids() -> list[str]:
    """List all adapter IDs."""
    return list(_REGISTRY.keys())
