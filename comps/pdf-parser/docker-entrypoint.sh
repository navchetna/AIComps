#!/bin/sh
set -euo pipefail

# Ensure storage directories exist.
# These can be overridden via environment variables when running the container:
#   UPLOAD_DIR           - temporary upload directory
#   BATCH_STORE_DIR      - batch job metadata/JSON store
#   BATCH_PROCESSING_DIR - processed output files
mkdir -p "${UPLOAD_DIR:-./uploads}"
mkdir -p "${BATCH_STORE_DIR:-./batch_jobs_store}"
mkdir -p "${BATCH_PROCESSING_DIR:-./batch_processing}"

exec "$@"

