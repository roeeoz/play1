#!/usr/bin/env bash
set -euo pipefail
# PLAY-190: prints "Hello, NAME!" for a non-empty NAME; rejects the empty string (or no argument) on stderr with exit 1.
name="${1-}"
if [[ -z $name ]]; then
	printf '%s\n' 'name must not be empty' >&2
	exit 1
fi
printf 'Hello, %s!\n' "$name"
