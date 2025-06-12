#!/bin/bash

print_tree() {
    local dir="$1"
    local prefix="$2"
    local entries=()
    local count=0

    # Read directory entries into an array
    while IFS= read -r -d $'\0' entry; do
        entries+=("$entry")
        ((count++))
    done < <(find "$dir" -mindepth 1 -maxdepth 1 -print0 | sort -z)

    for i in "${!entries[@]}"; do
        local path="${entries[$i]}"
        local base="$(basename "$path")"
        local connector="├──"
        local new_prefix="$prefix│   "

        if [ "$i" -eq "$((count - 1))" ]; then
            connector="└──"
            new_prefix="$prefix    "
        fi

        if [ -d "$path" ]; then
            echo "${prefix}${connector} ${base}/"
            print_tree "$path" "$new_prefix"
        else
            size=$(du -h "$path" | cut -f1)
            echo "${prefix}${connector} ${base} ($size)"
        fi
    done
}

# Entry point
root="${1:-.}"
echo "$(basename "$root")/"
print_tree "$root" ""
