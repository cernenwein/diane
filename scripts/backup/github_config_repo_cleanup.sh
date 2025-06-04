#!/bin/bash

echo "🧹 Starting Diane GitHub Repo Cleanup"
echo "This script will remove old/unused files not matching the known structure."

# Confirm repo path
REPO="$HOME/OneDrive/Documents/GitHub/diane"

# Known safe paths and files
declare -a SAFE_PATHS=(
  "$REPO/opt_copy"
  "$REPO/voice_llama_chat.py"
  "$REPO/README.md"
  "$REPO/.github"
  "$REPO/.git"
)

declare -a SAFE_PATTERNS=(
  "$REPO/XX_setup_diane_*.sh"
  "$REPO/github_config_*.sh"
  "$REPO/*.service"
  "$REPO/*.md"
  "$REPO/*.sh"
)

# Dry run confirmation
echo "🧪 Preview: Will keep the following paths and patterns:"
printf "   %s\n" "${SAFE_PATHS[@]}"
printf "   %s\n" "${SAFE_PATTERNS[@]}"
echo ""

# Find all files not matching the safe patterns
echo "🔍 Scanning for files not matching safe list..."
mapfile -t all_files < <(find "$REPO" -type f ! -path "$REPO/.git/*")
mapfile -t all_dirs < <(find "$REPO" -mindepth 1 -type d ! -path "$REPO/.git*")

declare -a to_delete=()

for file in "${all_files[@]}"; do
  keep=false
  for safe in "${SAFE_PATHS[@]}"; do [[ "$file" == "$safe" ]] && keep=true && break; done
  for pattern in "${SAFE_PATTERNS[@]}"; do [[ "$file" == $pattern ]] && keep=true && break; done
  if ! $keep; then to_delete+=("$file"); fi
done

echo "🗑️ The following files will be removed:"
printf "   %s\n" "${to_delete[@]}"
echo ""
read -p "❓ Proceed with deleting these files? (y/n) " confirm
if [[ "$confirm" != "y" ]]; then
  echo "❌ Cancelled."
  exit 1
fi

# Delete files
for f in "${to_delete[@]}"; do
  rm -f "$f"
done

echo "✅ File cleanup complete."

# Now clean empty directories not in SAFE_PATHS and not .git
for dir in "${all_dirs[@]}"; do
  if [[ -z "$(ls -A "$dir" 2>/dev/null)" ]] && [[ "$dir" != "$REPO" ]]; then
    echo "🧯 Removing empty directory: $dir"
    rm -rf "$dir"
  fi
done

echo "🧼 All clean. Repo structure is now minimal and accurate."
