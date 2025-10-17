"""Generate the demo update archive used by the auto-updater."""
from __future__ import annotations

from pathlib import Path

import zipfile


TARGET_VERSION = "1.0.1"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    updates_dir = repo_root / "updates"
    updates_dir.mkdir(exist_ok=True)

    archive_path = updates_dir / f"update_{TARGET_VERSION}.zip"

    updated_version_py = (
        '"""Application version information."""\n\n'
        f'__version__ = "{TARGET_VERSION}"\n'
    )

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("app/version.py", updated_version_py)

    print(f"Demo update written to {archive_path}")


if __name__ == "__main__":
    main()
