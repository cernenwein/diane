#!/bin/bash

VERSION="1.0.0"

print_usage() {
    echo "Usage: $0 [DIRECTORY]"
    echo ""
    echo "Recursively prints an ASCII tree of directories and files."
    echo "Includes file sizes in human-readable format."
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message and exit"
    echo "  --version        Show script version and exit"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/dir"
}

print_version() {
    echo "$0 version $VERSION"
}

print_tree() {
    local dir="$1"
    local prefix="$2"
    local entries=()
    local count=0

    # Read entries into array
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
            local size
            size=$(du -h "$path" | cut -f1)
            echo "${prefix}${connector} ${base} ($size)"
        fi
    done
}

# Parse arguments
case "$1" in
    -h|--help)
        print_usage
        exit 0
        ;;
    --version)
        print_version
        exit 0
        ;;
    "")
        TARGET="."
        ;;
    *)
        TARGET="$1"
        ;;
esac

if [ ! -d "$TARGET" ]; then
    echo "Error: '$TARGET' is not a valid directory."
    echo "Use --help for usage information."
    exit 1
fi

echo "$(basename "$TARGET")/"
print_tree "$TARGET" ""
