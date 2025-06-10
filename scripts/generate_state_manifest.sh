#!/usr/bin/env python3
import os
import stat
import json

def generate_manifest(root_dirs, manifest_path):
    """
    Walk each directory in root_dirs, recording every directory and file.
    Output a JSON list of entries with path, type, owner, group, and mode.
    """
    entries = []
    for root_dir in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            st = os.stat(dirpath)
            entries.append({
                "path": dirpath,
                "type": "dir",
                "owner": st.st_uid,
                "group": st.st_gid,
                "mode": stat.S_IMODE(st.st_mode)
            })
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                stf = os.stat(fpath)
                entries.append({
                    "path": fpath,
                    "type": "file",
                    "owner": stf.st_uid,
                    "group": stf.st_gid,
                    "mode": stat.S_IMODE(stf.st_mode),
                    "size": stf.st_size
                })
    # Sort entries so that parent directories come before nested files/dirs
    entries.sort(key=lambda e: e["path"])
    with open(manifest_path, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"State manifest written to {manifest_path}")

if __name__ == "__main__":
    # Adjust these root folders as needed.
    roots = [
        "/home/diane/diane",  # your repo and scripts
        "/mnt/ssd/models",    # models on SSD
        "/mnt/ssd/voice_config",  # configs on SSD
        "/mnt/ssd/tmp",       # temp
        "/mnt/ssd/whisper_cache"
    ]
    manifest_file = "/home/diane/diane/state_manifest.json"
    generate_manifest(roots, manifest_file)
