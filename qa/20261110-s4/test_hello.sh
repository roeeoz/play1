#!/bin/sh
# Checks that the hello.sh next to this file prints exactly "hello s4" and exits 0.
# Story QA20261110-2 "QA-20261110-S4 hello.sh prints hello s4".
set -u

dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || {
	echo "FAIL: cannot resolve the directory of $0" >&2
	exit 1
}

# The trailing "x" sentinel keeps trailing newlines that $(...) would strip;
# the subshell exits with hello.sh's own status.
out=$("$dir/hello.sh"; rc=$?; printf x; exit "$rc")
rc=$?
out=${out%x}
expected=$(printf 'hello s4\nx')
expected=${expected%x}

if [ "$rc" -ne 0 ]; then
	echo "FAIL: hello.sh exited with status $rc (expected 0)" >&2
	exit 1
fi
if [ "$out" != "$expected" ]; then
	printf 'FAIL: hello.sh printed [%s] (expected [hello s4] plus one newline)\n' "$out" >&2
	exit 1
fi
echo 'PASS: hello.sh printed "hello s4"'
exit 0
