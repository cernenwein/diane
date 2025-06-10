#!/usr/bin/env python3
import os
import stat
import pwd
import grp
import json
import sys

def emit_recreate_script(manifest_path, output_script):
    """
    Read manifest_path (JSON), then write a shell script that:
      - Creates all directories (with correct mode and ownership)
      - Creates empty files (with correct mode and ownership)
    NOTE: File contents are NOT copied—only empty files are created.
    """
    with open(manifest_path, "r") as f:
        entries = json.load(f)

    lines = ["#!/usr/bin/env bash", "set -e", ""]
    # Track which parent directories we've handled
    created_dirs = set()

    for e in entries:
        path = e["path"]
        mode = e["mode"]
        uid = e["owner"]
        gid = e["group"]
        # Convert UID/GID to names if possible; else keep numeric
        try:
            user = pwd.getpwuid(uid).pw_name
        except KeyError:
            user = str(uid)
        try:
            group = grp.getgrgid(gid).gr_name
        except KeyError:
            group = str(gid)

        parent = os.path.dirname(path)
        if parent and parent not in created_dirs:
            lines.append(f"mkdir -p '{parent}'")
            lines.append(f"chown {user}:{group} '{parent}'")
            lines.append(f"chmod {mode:o} '{parent}'")
            created_dirs.add(parent)

        if e["type"] == "dir":
            # Create the directory itself
            lines.append(f"mkdir -p '{path}'")
            lines.append(f"chown {user}:{group} '{path}'")
            lines.append(f"chmod {mode:o} '{path}'")
        elif e["type"] == "file":
            # Create empty file if not exists
            lines.append(f"touch '{path}'")
            lines.append(f"chown {user}:{group} '{path}'")
            lines.append(f"chmod {mode:o} '{path}'")
        lines.append("")

    with open(output_script, "w") as out:
        out.write("\n".join(lines))

    os.chmod(output_script, 0o755)
    print(f"Recreate script written to {output_script}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: recreate_state_from_manifest.py <manifest.json> <output_script.sh>")
        sys.exit(1)
    manifest_file = sys.argv[1]
    output_script = sys.argv[2]
    emit_recreate_script(manifest_file, output_script)
