#!/usr/bin/env bash
# PLAY-190: runs s2-hello.sh for 'Ada' and '' and exits 0 only if stdout (exact bytes), stderr and exit code match for both.
dir=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd) || exit 1
target="$dir/s2-hello.sh"

errfile=$(mktemp) || exit 1
trap 'rm -f -- "$errfile"' EXIT

failed=0

# check CASE ARG EXPECTED_STDOUT EXPECTED_STDERR EXPECTED_RC
check() {
	local case=$1 arg=$2 want_out=$3 want_err=$4 want_rc=$5 out rc err ok=1
	# The sentinel "x" keeps trailing newlines that $(...) would otherwise strip.
	out=$("$target" "$arg" 2>"$errfile"; rc=$?; printf 'x%s' "$rc")
	rc=${out##*x}
	out=${out%x*}
	err=$(cat -- "$errfile"; printf x)
	err=${err%x}

	if [[ $rc != "$want_rc" ]]; then
		printf 'FAIL: %s: exit code %s, expected %s\n' "$case" "$rc" "$want_rc" >&2
		ok=0
	fi
	if [[ $out != "$want_out" ]]; then
		printf 'FAIL: %s: stdout %q, expected %q\n' "$case" "$out" "$want_out" >&2
		ok=0
	fi
	if [[ $err != "$want_err" ]]; then
		printf 'FAIL: %s: stderr %q, expected %q\n' "$case" "$err" "$want_err" >&2
		ok=0
	fi
	if ((ok)); then
		printf 'PASS: %s\n' "$case"
	else
		failed=1
	fi
}

check "greet 'Ada'" 'Ada' $'Hello, Ada!\n' '' 0
check "reject ''" '' '' $'name must not be empty\n' 1

exit "$failed"
