from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SERVICE_ICON_BY_KEY = {
    "web_app": "icon/service-web-app-development",
    "quality_assurance": "icon/service-quality-assurance",
    "dotnet": "icon/service-dotnet",
    "java": "icon/service-java",
    "cloud": "icon/service-cloud",
    "salesforce": "icon/service-salesforce",
}

_MANIFEST_CACHE: dict[str, Any] = {
    "path": None,
    "mtime_ns": None,
    "data": {"assets": []},
}


def clear_asset_manifest_cache() -> None:
    _MANIFEST_CACHE["path"] = None
    _MANIFEST_CACHE["mtime_ns"] = None
    _MANIFEST_CACHE["data"] = {"assets": []}


def load_asset_manifest(manifest_path: str) -> dict[str, Any]:
    raw_manifest = _load_manifest_from_path(manifest_path)
    assets = raw_manifest.get("assets", [])
    assets_by_id = {asset.get("id"): asset for asset in assets if asset.get("id")}

    categories = {
        "brand": [asset for asset in assets if asset.get("category") == "brand"],
        "icon": [asset for asset in assets if asset.get("category") == "icon"],
        "partner": [asset for asset in assets if asset.get("category") == "partner"],
        "other": [asset for asset in assets if asset.get("category") not in {"brand", "icon", "partner"}],
    }

    return {
        "exists": bool(raw_manifest.get("assets")),
        "generated_at": raw_manifest.get("generated_at"),
        "assets": assets,
        "assets_by_id": assets_by_id,
        "categories": categories,
    }


def build_template_asset_pack(
    *,
    manifest_path: str,
    show_partner_logos: bool,
    dashboard_partner_logo_limit: int,
    clients_partner_logo_limit: int,
) -> dict[str, Any]:
    manifest = load_asset_manifest(manifest_path)
    assets_by_id = manifest["assets_by_id"]
    categories = manifest["categories"]

    partner_assets = categories["partner"] if show_partner_logos else []
    dashboard_partners = partner_assets[: max(dashboard_partner_logo_limit, 0)]
    clients_partners = partner_assets[: max(clients_partner_logo_limit, 0)]

    service_icons = {
        key: assets_by_id.get(asset_id) for key, asset_id in SERVICE_ICON_BY_KEY.items()
    }

    return {
        "manifest_exists": manifest["exists"],
        "assets_by_id": assets_by_id,
        "brand_logo": assets_by_id.get("brand/logo-light"),
        "avatar": assets_by_id.get("brand/default-avatar"),
        "service_icons": service_icons,
        "dashboard_partners": dashboard_partners,
        "clients_partners": clients_partners,
        "show_partner_logos": show_partner_logos,
    }


def _load_manifest_from_path(manifest_path: str) -> dict[str, Any]:
    path = Path(manifest_path)
    if not path.exists():
        return {"assets": []}

    mtime_ns = path.stat().st_mtime_ns
    if (
        _MANIFEST_CACHE["path"] == manifest_path
        and _MANIFEST_CACHE["mtime_ns"] == mtime_ns
    ):
        cached_data = _MANIFEST_CACHE["data"]
        return {
            "generated_at": cached_data.get("generated_at"),
            "assets": list(cached_data.get("assets", [])),
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"assets": []}

    assets = []
    for asset in data.get("assets", []):
        static_path = _normalize_static_path(asset.get("static_path") or asset.get("local_path", ""))
        if not static_path:
            continue
        assets.append(
            {
                "id": asset.get("id"),
                "category": asset.get("category", "other"),
                "source_url": asset.get("source_url"),
                "static_path": static_path,
                "mime": asset.get("mime"),
                "width": _to_positive_int(asset.get("width")),
                "height": _to_positive_int(asset.get("height")),
                "bytes": _to_positive_int(asset.get("bytes")),
                "alt": (asset.get("alt") or "").strip(),
                "attribution": asset.get("attribution"),
                "integrity": asset.get("integrity", {}),
                "downloaded_at": asset.get("downloaded_at"),
            }
        )

    normalized = {
        "generated_at": data.get("generated_at"),
        "assets": assets,
    }
    _MANIFEST_CACHE["path"] = manifest_path
    _MANIFEST_CACHE["mtime_ns"] = mtime_ns
    _MANIFEST_CACHE["data"] = normalized
    return {
        "generated_at": normalized.get("generated_at"),
        "assets": list(normalized.get("assets", [])),
    }


def _normalize_static_path(raw_path: str) -> str:
    value = (raw_path or "").replace("\\", "/").strip()
    if not value:
        return ""
    prefix = "app/static/"
    if value.startswith(prefix):
        value = value[len(prefix) :]
    while value.startswith("/"):
        value = value[1:]
    return value


def _to_positive_int(raw_value: Any) -> int | None:
    try:
        number = int(raw_value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    return number
