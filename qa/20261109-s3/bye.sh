#!/bin/bash
# Prints bye, and bye <name> when a name is given.
printf 'bye\n'
if [ -n "${1-}" ]; then
  printf 'bye %s\n' "$1"
fi
