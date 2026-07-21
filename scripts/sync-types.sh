#!/usr/bin/env bash
# Regenerate magisterial/types.py from the published OpenAPI contract.
#
# By default pulls the live spec; pass a path to use a local artifact
# (e.g. ../magisterial/api/public_api/openapi.json during development).
#
#   ./scripts/sync-types.sh [spec-path-or-url]
#
# Requires: pip install datamodel-code-generator
set -euo pipefail
cd "$(dirname "$0")/.."

SPEC="${1:-https://api.magisterial.ai/v1/openapi.json}"

if [[ "$SPEC" == http* ]]; then
  curl -fsS "$SPEC" -o openapi.json
else
  cp "$SPEC" openapi.json
fi

datamodel-codegen \
  --input openapi.json \
  --input-file-type openapi \
  --output magisterial/types.py \
  --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.10 \
  --use-schema-description \
  --disable-timestamp \
  --use-double-quotes \
  --collapse-root-models

echo "Regenerated magisterial/types.py from $SPEC"
echo "Review the diff, run pytest, and bump the version if shapes changed."
