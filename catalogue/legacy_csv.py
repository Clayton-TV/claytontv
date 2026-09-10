"""Parsing helpers for the pre-Epic-2 CSV exports."""


class TopicResolutionError(ValueError):
    """A legacy topic field cannot be mapped to a unique list of names."""


def resolve_topic_names(value: str, known_names: set[str]) -> list[str]:  # noqa: C901
    """Resolve comma/semicolon-delimited legacy topic names without guessing.

    Commas occur both inside topic names and between values in the legacy
    exports.  A value is accepted only when the known topic names give it one
    complete parse.  This lets callers leave existing associations intact when
    the export is incomplete or ambiguous.
    """
    value = value.strip()
    if not value:
        return []

    names_by_initial: dict[str, list[str]] = {}
    for name in known_names:
        if name:
            names_by_initial.setdefault(name[0], []).append(name)

    starts = {0}
    for index, character in enumerate(value):
        if character in ",;":
            next_start = index + 1
            while next_start < len(value) and value[next_start].isspace():
                next_start += 1
            starts.add(next_start)

    parse_counts = {len(value): 1}
    choices: dict[int, tuple[str, int]] = {}
    for start in sorted(starts, reverse=True):
        if start == len(value):
            continue
        count = 0
        for name in names_by_initial.get(value[start], []):
            end = start + len(name)
            if not value.startswith(name, start):
                continue
            if end == len(value):
                next_start = end
                child_count = 1
            elif value[end] in ",;":
                next_start = end + 1
                while next_start < len(value) and value[next_start].isspace():
                    next_start += 1
                child_count = parse_counts.get(next_start, 0)
            else:
                continue

            if child_count and not count:
                choices[start] = (name, next_start)
            count = min(2, count + child_count)
        parse_counts[start] = count

    if parse_counts.get(0) != 1:
        raise TopicResolutionError(f"Could not uniquely resolve legacy topic value: {value!r}")

    names = []
    start = 0
    while start < len(value):
        name, start = choices[start]
        names.append(name)
    return names
