#!/bin/sh
# Prints the value of QA_S4_MARKER verbatim (exit 0), or reports on stderr that it is not set (exit 1).
if [ "${QA_S4_MARKER+set}" = set ]; then
	printf '%s\n' "$QA_S4_MARKER"
	exit 0
fi
printf 'QA_S4_MARKER is not set\n' >&2
exit 1
