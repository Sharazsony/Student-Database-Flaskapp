#!/bin/bash
set -e
if [ ! -f .env ]; then
  echo '❌ ERROR: .env file not found. Copy .env.example to .env and fill values.'
  exit 1
fi
set -a
source .env
set +a
FULL_IMAGE=
