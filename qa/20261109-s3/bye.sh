#!/bin/bash
# Prints a farewell, plus a personal one when a name is given; a small helper script for trying out the play1 dev factory.
printf 'bye\n'
if [ -n "${1-}" ]; then
  printf 'bye %s\n' "$1"
fi
exit 0
