#!/bin/sh
# Runs hello.sh directly and exits 0 only if it prints exactly "hello s3\n" and exits 0.
dir=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd) || exit 1
target="$dir/hello.sh"

# The sentinel "x" keeps trailing newlines that $(...) would otherwise strip.
out=$("$target"; rc=$?; printf 'x%s' "$rc")
rc=${out##*x}
out=${out%x*}

expected='hello s3
'

if [ "$rc" != 0 ]; then
	printf 'FAIL: %s exited %s, expected 0\n' "$target" "$rc" >&2
	exit 1
fi
if [ "$out" != "$expected" ]; then
	printf 'FAIL: %s printed unexpected output\n' "$target" >&2
	exit 1
fi
printf 'PASS: %s\n' "$target"
