from config.paths import (
    ORIGINAL_UPLOAD_DIR,
    TRANSLATED_UPLOAD_DIR
)


def build_tree(directory):

    items = []

    if not directory.exists():
        return items

    for path in sorted(
        directory.iterdir(),
        key=lambda p: (p.is_file(), p.name.lower())
    ):

        if path.is_dir():

            items.append({
                "name": path.name,
                "type": "folder",
                "children": build_tree(path)
            })

        else:

            items.append({
                "name": path.name,
                "type": "file"
            })

    return items


def get_workspace():

    return {
        "name": "Workspace",
        "type": "folder",
        "children": [
            {
                "name": "Originals",
                "type": "folder",
                "children": build_tree(
                    ORIGINAL_UPLOAD_DIR
                )
            },
            {
                "name": "Translated",
                "type": "folder",
                "children": build_tree(
                    TRANSLATED_UPLOAD_DIR
                )
            }
        ]
    }