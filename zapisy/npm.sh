#!/usr/bin/env bash
set -e

# Ensure the directory exists and has proper perms
./webpack_resources/create_modules_dir.sh
./webpack_resources/run_npm_with_copy.sh $@
