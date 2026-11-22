#!/bin/sh
# Runs s4_marker.sh in each QA_S4_MARKER case and exits 0 only if stdout, stderr and exit code all match.
dir=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd) || exit 1
target="$dir/s4_marker.sh"
errfile=$(mktemp) || exit 1
trap 'rm -f "$errfile"' EXIT
trap 'exit 1' HUP INT TERM

# check NAME RUNNER MODE VALUE EXPECTED_OUT EXPECTED_ERR EXPECTED_RC [ARGS...]
# RUNNER is "direct" (via the shebang) or a shell name; MODE is "set" or "unset".
check() {
	name=$1 runner=$2 mode=$3 value=$4 exp_out=$5 exp_err=$6 exp_rc=$7
	shift 7
	# The sentinel "x" keeps trailing newlines that $(...) would otherwise strip.
	out=$(
		if [ "$mode" = set ]; then
			QA_S4_MARKER=$value
			export QA_S4_MARKER
		else
			unset QA_S4_MARKER
		fi
		if [ "$runner" = direct ]; then
			"$target" "$@" 2>"$errfile"
		else
			"$runner" "$target" "$@" 2>"$errfile"
		fi
		rc=$?
		printf 'x%s' "$rc"
	)
	rc=${out##*x}
	out=${out%x*}
	err=$(cat "$errfile"; printf x)
	err=${err%x}
	if [ "$rc" != "$exp_rc" ]; then
		printf 'FAIL: %s [%s]: exited %s, expected %s\n' "$name" "$runner" "$rc" "$exp_rc" >&2
		exit 1
	fi
	if [ "$out" != "$exp_out" ]; then
		printf 'FAIL: %s [%s]: unexpected stdout\n' "$name" "$runner" >&2
		exit 1
	fi
	if [ "$err" != "$exp_err" ]; then
		printf 'FAIL: %s [%s]: unexpected stderr\n' "$name" "$runner" >&2
		exit 1
	fi
}

nl='
'
two_lines="line one${nl}line two"

run_cases() {
	r=$1
	check 'non-empty value' "$r" set 'prod-eu-1' "prod-eu-1$nl" '' 0
	check 'empty value' "$r" set '' "$nl" '' 0
	check 'unset' "$r" unset '' '' "QA_S4_MARKER is not set$nl" 1
	check 'value -n' "$r" set '-n' "-n$nl" '' 0
	check 'value with backslashes' "$r" set 'a\nb\c' "a\\nb\\c$nl" '' 0
	check 'value with % sequences' "$r" set '%s %d' "%s %d$nl" '' 0
	check 'value with leading/trailing spaces' "$r" set ' sp ' " sp $nl" '' 0
	check 'value with embedded newline' "$r" set "$two_lines" "$two_lines$nl" '' 0
	check 'arguments ignored (set)' "$r" set 'v1' "v1$nl" '' 0 -n extra arg
	check 'arguments ignored (unset)' "$r" unset '' '' "QA_S4_MARKER is not set$nl" 1 some-arg
}

run_cases direct
if command -v dash >/dev/null 2>&1; then
	run_cases dash
else
	printf 'SKIP: dash not installed; dash pass not run\n'
fi
printf 'PASS: %s\n' "$target"
