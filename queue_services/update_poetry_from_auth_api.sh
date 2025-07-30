#!/bin/bash
set -euo pipefail

TARGET_DIRS=("account-mailer" "auth-queue")

BRANCH=$(git rev-parse --abbrev-ref HEAD)
REPO=$(git config --get remote.origin.url)
# git config --get remote.upstream.url if you need bcgov

update_pyproject_and_poetry() {
  local dir=$1
  local file="$dir/pyproject.toml"
  if [ ! -f "$file" ]; then
    echo "Skipping $dir: pyproject.toml not found."
    return
  fi

  echo "Updating $file..."
  sed -i -E "s|auth-api = \{ git = .*?, rev = .*?, subdirectory = \"auth-api\" \}|auth-api = \{ git = \"$REPO\", rev = \"$BRANCH\", subdirectory = \"auth-api\" \}|" "$file"

  echo "Running poetry update auth-api in $dir..."
  cd "$dir"
  poetry update auth-api
  cd - > /dev/null
}

for dir in "${TARGET_DIRS[@]}"; do
  update_pyproject_and_poetry "$dir"
done

echo "All done."
