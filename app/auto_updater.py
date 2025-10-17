"""Simple auto-update utility that uses a manifest JSON file."""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from urllib.request import urlopen

import customtkinter as ctk

from .version import __version__


@dataclass
class UpdateInfo:
    """Data extracted from the update manifest."""

    version: str
    description: str
    download_url: str


class AutoUpdater:
    """Check and apply updates described by a JSON manifest."""

    def __init__(self, manifest_url: str, app_root: Path) -> None:
        self.manifest_url = manifest_url
        self.app_root = app_root
        self._status_var = ctk.StringVar(value="Idle")

        parsed_manifest = urlparse(manifest_url)
        if parsed_manifest.scheme in {"", "file"}:
            self._manifest_dir: Optional[Path] = Path(parsed_manifest.path).resolve().parent
        else:
            self._manifest_dir = None

    @property
    def status_var(self) -> ctk.StringVar:
        return self._status_var

    def fetch_manifest(self) -> Optional[UpdateInfo]:
        self._status_var.set("Checking for updates…")
        try:
            with urlopen(self.manifest_url) as response:  # nosec - trusted local resource
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - handled by UI feedback
            self._status_var.set(f"Update check failed: {exc}")
            return None

        return UpdateInfo(
            version=data.get("version", "0.0.0"),
            description=data.get("description", ""),
            download_url=data["download_url"],
        )

    def is_update_available(self, info: UpdateInfo) -> bool:
        return info.version > __version__

    def download_update(self, info: UpdateInfo) -> Optional[Path]:
        self._status_var.set("Downloading update…")
        target = Path(tempfile.gettempdir()) / "ctk_app_update.zip"

        parsed = urlparse(info.download_url)
        try:
            if parsed.scheme in {"", "file"}:
                source_path = Path(parsed.path)
                if not source_path.is_absolute() and self._manifest_dir is not None:
                    source_path = (self._manifest_dir / source_path).resolve()
                shutil.copy(source_path, target)
            else:
                with urlopen(info.download_url) as response:  # nosec - trusted resource
                    target.write_bytes(response.read())
        except Exception as exc:  # pragma: no cover - handled by UI feedback
            self._status_var.set(f"Download failed: {exc}")
            return None

        return target

    def apply_update(self, archive_path: Path) -> bool:
        self._status_var.set("Applying update…")
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                archive.extractall(self.app_root)
        except zipfile.BadZipFile as exc:  # pragma: no cover - handled by UI feedback
            self._status_var.set(f"Invalid update package: {exc}")
            return False

        self._status_var.set("Update installed. Restart the app.")
        return True

    def run_update_flow(self) -> None:
        info = self.fetch_manifest()
        if not info:
            return

        if not self.is_update_available(info):
            self._status_var.set("Already up-to-date.")
            return

        archive_path = self.download_update(info)
        if not archive_path:
            return

        self.apply_update(archive_path)
