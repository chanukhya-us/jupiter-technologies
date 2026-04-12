from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = PROJECT_ROOT / "app" / "static"
IMAGES_ROOT = STATIC_ROOT / "images"
MANIFEST_PATH = IMAGES_ROOT / "manifest.json"

JUPITER_ATTRIBUTION = "© Jupiter Technologies. Used with permission."
PARTNER_ATTRIBUTION = "Trademark/logo of its respective owner. Used with permission."


@dataclass(frozen=True)
class AssetSource:
    asset_id: str
    category: str
    source_url: str
    static_path: str
    alt: str
    attribution: str


def build_asset_sources() -> list[AssetSource]:
    base = "https://www.jupitertechnologies.net/assets/images"
    assets = [
        AssetSource(
            asset_id="brand/logo-light",
            category="brand",
            source_url=f"{base}/light-logo.png",
            static_path="images/brand/jupiter-technologies-logo-light.png",
            alt="Jupiter Technologies logo",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="brand/default-avatar",
            category="brand",
            source_url=f"{base}/author.png",
            static_path="images/brand/default-avatar-jupiter.png",
            alt="Default avatar icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="icon/service-web-app-development",
            category="icon",
            source_url=f"{base}/services/style4/7.png",
            static_path="images/icons/jupiter-service-web-app-development.png",
            alt="Web application development icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="icon/service-quality-assurance",
            category="icon",
            source_url=f"{base}/services/style4/8.png",
            static_path="images/icons/jupiter-service-quality-assurance.png",
            alt="Quality assurance icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="icon/service-dotnet",
            category="icon",
            source_url=f"{base}/services/style4/9.png",
            static_path="images/icons/jupiter-service-dotnet.png",
            alt=".NET services icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="icon/service-java",
            category="icon",
            source_url=f"{base}/services/style4/1.png",
            static_path="images/icons/jupiter-service-java.png",
            alt="Java services icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="icon/service-cloud",
            category="icon",
            source_url=f"{base}/services/style4/2.png",
            static_path="images/icons/jupiter-service-cloud.png",
            alt="Cloud services icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
        AssetSource(
            asset_id="icon/service-salesforce",
            category="icon",
            source_url=f"{base}/services/style4/3.png",
            static_path="images/icons/jupiter-service-salesforce.png",
            alt="Salesforce services icon",
            attribution=JUPITER_ATTRIBUTION,
        ),
    ]

    partner_indices = list(range(1, 25)) + list(range(26, 32))
    for partner_index in partner_indices:
        assets.append(
            AssetSource(
                asset_id=f"partner/logo-{partner_index:02d}",
                category="partner",
                source_url=f"{base}/partner/{partner_index}.png",
                static_path=f"images/partners/partner-{partner_index:02d}.png",
                alt=f"Partner logo {partner_index}",
                attribution=PARTNER_ATTRIBUTION,
            )
        )
    return assets


def download_bytes(url: str, timeout: int) -> tuple[bytes, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "JupiterAssetFetcher/1.0 (+https://www.jupitertechnologies.net/)",
            "Accept": "image/*,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = response.read()
        mime = response.headers.get_content_type() or "application/octet-stream"
    return payload, mime


def detect_dimensions(data: bytes, mime: str) -> tuple[int | None, int | None]:
    if mime == "image/png" and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return int(width), int(height)

    if mime == "image/gif" and len(data) >= 10:
        width, height = struct.unpack("<HH", data[6:10])
        return int(width), int(height)

    if mime == "image/jpeg":
        return _read_jpeg_dimensions(data)

    if mime == "image/webp":
        return _read_webp_dimensions(data)

    return None, None


def _read_jpeg_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 4 or data[:2] != b"\xFF\xD8":
        return None, None

    index = 2
    length = len(data)
    while index < length:
        while index < length and data[index] == 0xFF:
            index += 1
        if index >= length:
            break
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > length:
            break
        segment_length = struct.unpack(">H", data[index : index + 2])[0]
        if segment_length < 2:
            return None, None
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if index + 7 > length:
                return None, None
            height = struct.unpack(">H", data[index + 3 : index + 5])[0]
            width = struct.unpack(">H", data[index + 5 : index + 7])[0]
            return int(width), int(height)
        index += segment_length
    return None, None


def _read_webp_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None, None
    chunk = data[12:16]

    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + struct.unpack("<I", data[24:27] + b"\x00")[0]
        height = 1 + struct.unpack("<I", data[27:30] + b"\x00")[0]
        return int(width), int(height)

    if chunk == b"VP8 " and len(data) >= 30:
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return int(width), int(height)

    return None, None


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_manifest_entry(asset: AssetSource, mime: str, payload: bytes) -> dict:
    width, height = detect_dimensions(payload, mime)
    now = datetime.now(tz=UTC).isoformat()
    return {
        "id": asset.asset_id,
        "category": asset.category,
        "source_url": asset.source_url,
        "static_path": asset.static_path,
        "local_path": f"app/static/{asset.static_path}",
        "mime": mime,
        "width": width,
        "height": height,
        "bytes": len(payload),
        "alt": asset.alt,
        "attribution": asset.attribution,
        "downloaded_at": now,
        "integrity": {"sha256": sha256_hex(payload)},
    }


def write_manifest(entries: list[dict]) -> None:
    ensure_parent(MANIFEST_PATH)
    content = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "source_site": "https://www.jupitertechnologies.net/",
        "asset_count": len(entries),
        "assets": entries,
    }
    tmp_manifest = MANIFEST_PATH.with_suffix(".json.tmp")
    tmp_manifest.write_text(json.dumps(content, indent=2), encoding="utf-8")
    tmp_manifest.replace(MANIFEST_PATH)


def apply_main_logo_override(entries: list[dict], main_logo_path: str) -> None:
    logo_source = Path(main_logo_path).expanduser().resolve()
    if not logo_source.exists():
        raise SystemExit(f"main logo path not found: {logo_source}")

    payload = logo_source.read_bytes()
    mime = "image/png" if logo_source.suffix.lower() == ".png" else "application/octet-stream"
    width, height = detect_dimensions(payload, mime)

    static_path = "images/brand/jupiter-main-logo.png"
    target = STATIC_ROOT / static_path
    ensure_parent(target)
    target.write_bytes(payload)

    entry = {
        "id": "brand/logo-light",
        "category": "brand",
        "source_url": str(logo_source),
        "static_path": static_path,
        "local_path": f"app/static/{static_path}",
        "mime": mime,
        "width": width,
        "height": height,
        "bytes": len(payload),
        "alt": "Jupiter Technologies logo",
        "attribution": JUPITER_ATTRIBUTION,
        "downloaded_at": datetime.now(tz=UTC).isoformat(),
        "integrity": {"sha256": sha256_hex(payload)},
    }

    for index, current in enumerate(entries):
        if current.get("id") == "brand/logo-light":
            entries[index] = entry
            print(f"main logo override applied from {logo_source}")
            return

    entries.insert(0, entry)
    print(f"main logo override inserted from {logo_source}")


def ingest_assets(assets: Iterable[AssetSource], timeout: int, main_logo_path: str | None = None) -> None:
    entries: list[dict] = []
    errors: list[str] = []

    for asset in assets:
        try:
            payload, mime = download_bytes(asset.source_url, timeout=timeout)
            if not mime.startswith("image/"):
                raise ValueError(f"unexpected mime type: {mime}")
            entry = build_manifest_entry(asset, mime, payload)
            target = STATIC_ROOT / asset.static_path
            ensure_parent(target)
            target.write_bytes(payload)
            entries.append(entry)
            print(f"downloaded {asset.asset_id} -> {asset.static_path}")
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append(f"{asset.asset_id}: {exc}")

    if errors:
        print("asset ingestion failed; manifest not updated.")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    if main_logo_path:
        apply_main_logo_override(entries, main_logo_path)

    write_manifest(entries)
    print(f"manifest written: {MANIFEST_PATH}")
    print(f"assets downloaded: {len(entries)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Jupiter assets and build manifest.")
    parser.add_argument("--timeout", type=int, default=45, help="HTTP timeout in seconds")
    parser.add_argument(
        "--main-logo",
        type=str,
        default=None,
        help="Optional local image path to force as brand/logo-light after fetch.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ingest_assets(build_asset_sources(), timeout=args.timeout, main_logo_path=args.main_logo)


if __name__ == "__main__":
    main()
