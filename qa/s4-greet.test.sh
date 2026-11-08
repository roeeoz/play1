#!/bin/sh
# Bats-free test for qa/s4-greet.sh: passes only if it exits 0 and prints exactly "HELLO FROM S4" plus a newline.

target="$(dirname -- "$0")/s4-greet.sh"
expected='HELLO FROM S4
'

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

[ -e "$target" ] || fail "$target is missing"
[ -f "$target" ] || fail "$target is not a regular file"
[ -x "$target" ] || fail "$target is not executable"

# The trailing sentinel "x" keeps any trailing newlines that $(...) would otherwise strip.
out=$("$target"; rc=$?; printf x; exit "$rc")
status=$?
out=${out%x}

[ "$status" -eq 0 ] || fail "$target exited with status $status"

if [ "$out" != "$expected" ]; then
    printf 'FAIL: %s printed unexpected output (expected "HELLO FROM S4" and one newline); got:\n' "$target" >&2
    printf '%s' "$out" | od -c >&2
    exit 1
fi

printf "PASS: %s printed 'HELLO FROM S4'\n" "$target"
exit 0
