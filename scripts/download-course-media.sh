#!/usr/bin/env bash
# Download the Issue #97 course files with curl. See docs/course-downloads.md.
set -u

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
manifest="$script_dir/course-downloads.tsv"
retries=${CURL_RETRIES:-3}

usage() {
    echo "Usage: $0 OUTPUT_DIRECTORY [--manifest PATH]" >&2
}

if [[ $# -lt 1 ]]; then
    usage
    exit 2
fi

output_dir=$1
shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --manifest)
            manifest=${2:?"--manifest needs a path"}
            shift 2
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

if ! command -v curl >/dev/null; then
    echo "curl is required." >&2
    exit 2
fi
if [[ ! -f "$manifest" ]]; then
    echo "Manifest not found: $manifest" >&2
    exit 2
fi

mkdir -p "$output_dir/.course-downloads-state"
report="$output_dir/download-report.tsv"
printf 'status\tpath\turl\tmessage\n' >"$report"
failures=0

while IFS=$'\t' read -r course path url; do
    [[ -z "$course" || "$course" == "course" ]] && continue
    target="$output_dir/$path"
    partial="$target.part"
    marker="$output_dir/.course-downloads-state/$path.url"
    mkdir -p "$(dirname -- "$target")" "$(dirname -- "$marker")"

    if [[ -f "$target" ]]; then
        if [[ -f "$marker" ]] && cmp -s "$marker" <(printf '%s\n' "$url"); then
            printf 'skipped\t%s\t%s\tpreviously completed\n' "$path" "$url" >>"$report"
            continue
        fi
        printf 'failed\t%s\t%s\ttarget exists without a matching completion record\n' "$path" "$url" >>"$report"
        printf 'Refusing to overwrite %s\n' "$target" >&2
        failures=1
        continue
    fi

    if curl --fail --location --continue-at - --retry "$retries" --retry-delay 2 \
        --retry-all-errors --connect-timeout 30 --output "$partial" "$url"; then
        mv -- "$partial" "$target"
        printf '%s\n' "$url" >"$marker"
        printf 'completed\t%s\t%s\t\n' "$path" "$url" >>"$report"
    else
        printf 'failed\t%s\t%s\tcurl failed; retained .part file for resume\n' "$path" "$url" >>"$report"
        printf 'Failed: %s\n' "$url" >&2
        failures=1
    fi
done <"$manifest"

if [[ "$failures" -ne 0 ]]; then
    echo "One or more downloads failed. See $report" >&2
    exit 1
fi

echo "Completed. Report: $report"
