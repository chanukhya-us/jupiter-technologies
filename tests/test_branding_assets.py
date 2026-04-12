from __future__ import annotations

import base64
import json
from pathlib import Path
from urllib.error import URLError

import pytest

from app.assets import clear_asset_manifest_cache
from scripts import fetch_jupiter_assets as fetch
from tests.conftest import login


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7+2QAAAABJRU5ErkJggg=="
)


def _write_manifest(path: Path, assets: list[dict]) -> None:
    payload = {
        "generated_at": "2026-04-12T00:00:00+00:00",
        "source_site": "https://www.jupitertechnologies.net/",
        "asset_count": len(assets),
        "assets": assets,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _sample_assets() -> list[dict]:
    return [
        {
            "id": "brand/logo-light",
            "category": "brand",
            "source_url": "https://example.com/logo.png",
            "static_path": "images/brand/logo.png",
            "local_path": "app/static/images/brand/logo.png",
            "mime": "image/png",
            "width": 120,
            "height": 24,
            "bytes": 1200,
            "alt": "Jupiter Technologies logo",
            "attribution": "© Jupiter Technologies. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash1"},
        },
        {
            "id": "brand/default-avatar",
            "category": "brand",
            "source_url": "https://example.com/avatar.png",
            "static_path": "images/brand/avatar.png",
            "local_path": "app/static/images/brand/avatar.png",
            "mime": "image/png",
            "width": 32,
            "height": 32,
            "bytes": 400,
            "alt": "Default avatar icon",
            "attribution": "© Jupiter Technologies. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash2"},
        },
        {
            "id": "icon/service-web-app-development",
            "category": "icon",
            "source_url": "https://example.com/web.png",
            "static_path": "images/icons/web.png",
            "local_path": "app/static/images/icons/web.png",
            "mime": "image/png",
            "width": 32,
            "height": 32,
            "bytes": 300,
            "alt": "Web application development icon",
            "attribution": "© Jupiter Technologies. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash3"},
        },
        {
            "id": "icon/service-dotnet",
            "category": "icon",
            "source_url": "https://example.com/dotnet.png",
            "static_path": "images/icons/dotnet.png",
            "local_path": "app/static/images/icons/dotnet.png",
            "mime": "image/png",
            "width": 32,
            "height": 32,
            "bytes": 300,
            "alt": ".NET icon",
            "attribution": "© Jupiter Technologies. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash4"},
        },
        {
            "id": "icon/service-java",
            "category": "icon",
            "source_url": "https://example.com/java.png",
            "static_path": "images/icons/java.png",
            "local_path": "app/static/images/icons/java.png",
            "mime": "image/png",
            "width": 32,
            "height": 32,
            "bytes": 300,
            "alt": "Java icon",
            "attribution": "© Jupiter Technologies. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash5"},
        },
        {
            "id": "icon/service-cloud",
            "category": "icon",
            "source_url": "https://example.com/cloud.png",
            "static_path": "images/icons/cloud.png",
            "local_path": "app/static/images/icons/cloud.png",
            "mime": "image/png",
            "width": 32,
            "height": 32,
            "bytes": 300,
            "alt": "Cloud icon",
            "attribution": "© Jupiter Technologies. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash6"},
        },
        {
            "id": "partner/logo-01",
            "category": "partner",
            "source_url": "https://example.com/partner01.png",
            "static_path": "images/partners/p01.png",
            "local_path": "app/static/images/partners/p01.png",
            "mime": "image/png",
            "width": 120,
            "height": 40,
            "bytes": 700,
            "alt": "Partner logo 1",
            "attribution": "Trademark/logo of its respective owner. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash7"},
        },
        {
            "id": "partner/logo-02",
            "category": "partner",
            "source_url": "https://example.com/partner02.png",
            "static_path": "images/partners/p02.png",
            "local_path": "app/static/images/partners/p02.png",
            "mime": "image/png",
            "width": 120,
            "height": 40,
            "bytes": 700,
            "alt": "Partner logo 2",
            "attribution": "Trademark/logo of its respective owner. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash8"},
        },
        {
            "id": "partner/logo-03",
            "category": "partner",
            "source_url": "https://example.com/partner03.png",
            "static_path": "images/partners/p03.png",
            "local_path": "app/static/images/partners/p03.png",
            "mime": "image/png",
            "width": 120,
            "height": 40,
            "bytes": 700,
            "alt": "Partner logo 3",
            "attribution": "Trademark/logo of its respective owner. Used with permission.",
            "downloaded_at": "2026-04-12T00:00:00+00:00",
            "integrity": {"sha256": "hash9"},
        },
    ]


def test_branding_sections_render_with_manifest(client, app, tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, _sample_assets())

    app.config["ASSET_MANIFEST_PATH"] = str(manifest_path)
    app.config["SHOW_PARTNER_LOGOS"] = True
    app.config["DASHBOARD_PARTNER_LOGO_LIMIT"] = 2
    app.config["CLIENTS_PARTNER_LOGO_LIMIT"] = 3
    clear_asset_manifest_cache()

    login(client, "owner")
    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Trusted Partners" in dashboard.data
    assert dashboard.data.count(b"rt-partner-pill") == 2
    assert b"rt-action-icon" in dashboard.data
    assert b"rt-series-chart" in dashboard.data

    clients_page = client.get("/clients")
    assert clients_page.status_code == 200
    assert b"Partner Logos" in clients_page.data
    assert clients_page.data.count(b"rt-partner-card") == 3


def test_partner_logo_sections_respect_toggle(client, app, tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, _sample_assets())

    app.config["ASSET_MANIFEST_PATH"] = str(manifest_path)
    app.config["SHOW_PARTNER_LOGOS"] = False
    clear_asset_manifest_cache()

    login(client, "owner")
    dashboard = client.get("/dashboard")
    clients_page = client.get("/clients")

    assert b"Trusted Partners" not in dashboard.data
    assert b"Partner Logos" not in clients_page.data


def test_asset_pipeline_writes_manifest_with_expected_fields(tmp_path, monkeypatch):
    static_root = tmp_path / "static"
    manifest_path = static_root / "images" / "manifest.json"

    monkeypatch.setattr(fetch, "STATIC_ROOT", static_root)
    monkeypatch.setattr(fetch, "IMAGES_ROOT", static_root / "images")
    monkeypatch.setattr(fetch, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(fetch, "download_bytes", lambda *_args, **_kwargs: (PNG_1X1, "image/png"))

    source = fetch.AssetSource(
        asset_id="brand/logo-light",
        category="brand",
        source_url="https://example.com/logo.png",
        static_path="images/brand/logo.png",
        alt="Jupiter Technologies logo",
        attribution="© Jupiter Technologies. Used with permission.",
    )
    fetch.ingest_assets([source], timeout=1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["asset_count"] == 1
    entry = manifest["assets"][0]
    for required_key in (
        "id",
        "category",
        "source_url",
        "static_path",
        "local_path",
        "mime",
        "width",
        "height",
        "bytes",
        "alt",
        "attribution",
        "integrity",
        "downloaded_at",
    ):
        assert required_key in entry
    assert (static_root / entry["static_path"]).exists()
    assert entry["integrity"]["sha256"]


def test_asset_pipeline_failure_does_not_corrupt_manifest(tmp_path, monkeypatch):
    static_root = tmp_path / "static"
    manifest_path = static_root / "images" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    original_manifest = {"generated_at": "seed", "assets": []}
    manifest_path.write_text(json.dumps(original_manifest), encoding="utf-8")

    monkeypatch.setattr(fetch, "STATIC_ROOT", static_root)
    monkeypatch.setattr(fetch, "IMAGES_ROOT", static_root / "images")
    monkeypatch.setattr(fetch, "MANIFEST_PATH", manifest_path)

    call_count = {"n": 0}

    def _download_with_failure(*_args, **_kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return PNG_1X1, "image/png"
        raise URLError("network failure")

    monkeypatch.setattr(fetch, "download_bytes", _download_with_failure)

    assets = [
        fetch.AssetSource(
            asset_id="brand/logo-light",
            category="brand",
            source_url="https://example.com/logo.png",
            static_path="images/brand/logo.png",
            alt="Logo",
            attribution="© Jupiter Technologies. Used with permission.",
        ),
        fetch.AssetSource(
            asset_id="partner/logo-01",
            category="partner",
            source_url="https://example.com/p01.png",
            static_path="images/partners/p01.png",
            alt="Partner logo 1",
            attribution="Trademark/logo of its respective owner. Used with permission.",
        ),
    ]

    with pytest.raises(SystemExit):
        fetch.ingest_assets(assets, timeout=1)

    persisted = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert persisted == original_manifest
