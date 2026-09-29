#!/usr/bin/env bash
# Bootstrap the installer from a published release, never a development checkout.
set -euo pipefail
if ! command -v omarchy >/dev/null; then
  echo 'jump.exe requires Omarchy.' >&2
  exit 1
fi
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
  https://github.com/gardnmi/jump.exe/releases/latest/download/install.py \
  --output "$tmp/install.py"
exec_status=0
/usr/bin/python -I "$tmp/install.py" "$@" || exec_status=$?
exit "$exec_status"
