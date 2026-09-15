from pathlib import Path

from config.paths import (
    ORIGINAL_UPLOAD_DIR,
    TRANSLATED_UPLOAD_DIR,
)


def ensure_workspace_directories():
    (ORIGINAL_UPLOAD_DIR / "documents").mkdir(
        parents=True,
        exist_ok=True,
    )

    (TRANSLATED_UPLOAD_DIR / "documents").mkdir(
        parents=True,
        exist_ok=True,
    )


def build_tree(directory: Path):
    if not directory.exists() or not directory.is_dir():
        return []

    items = []

    for path in sorted(
        directory.iterdir(),
        key=lambda p: (
            not p.is_dir(),
            p.name.lower(),
        ),
    ):
        if path.is_dir():
            items.append({
                "name": path.name,
                "type": "folder",
                "children": build_tree(path),
            })
        elif path.is_file():
            items.append({
                "name": path.name,
                "type": "file",
            })

    return items


def get_workspace():
    ensure_workspace_directories()

    return {
        "name": "Workspace",
        "type": "folder",
        "children": [
            {
                "name": "originals",
                "type": "folder",
                "children": build_tree(
                    ORIGINAL_UPLOAD_DIR
                ),
            },
            {
                "name": "translated",
                "type": "folder",
                "children": build_tree(
                    TRANSLATED_UPLOAD_DIR
                ),
            },
        ],
    }