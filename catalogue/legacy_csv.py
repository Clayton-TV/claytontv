"""Parsing helpers for the pre-Epic-2 CSV exports."""

from functools import cache


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

    @cache
    def parses_from(start: int) -> tuple[tuple[str, ...], ...]:
        if start == len(value):
            return ((),)

        parses: list[tuple[str, ...]] = []
        for name in known_names:
            end = start + len(name)
            if not value.startswith(name, start):
                continue
            if end == len(value):
                parses.append((name,))
            elif value[end] in ",;":
                next_start = end + 1
                while next_start < len(value) and value[next_start].isspace():
                    next_start += 1
                parses.extend((name, *rest) for rest in parses_from(next_start))
            if len(parses) > 1:
                return tuple(parses[:2])
        return tuple(parses)

    parses = parses_from(0)
    if len(parses) != 1:
        raise TopicResolutionError(f"Could not uniquely resolve legacy topic value: {value!r}")
    return list(parses[0])
