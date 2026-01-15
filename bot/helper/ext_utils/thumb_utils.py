from os import path as ospath
from re import compile, split, sub


_ARABIC_EPISODE_RE = compile(r"^(.*?)\s+(?:الحلقه|الحلقة)\b", flags=0)
_SEASON_RE = compile(r"^(.*?)(?:[\s._-]*s\d{1,2}(?:e\d{1,3})?.*)", flags=2)
_NORMALIZE_RE = compile(r"[\s._-]+")


def normalize_thumb_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.strip().lower()
    name = _NORMALIZE_RE.sub(" ", name)
    name = sub(r"\s+", " ", name).strip()
    return name


def parse_thumb_caption(caption: str) -> list[str]:
    if not caption:
        return []
    parts = split(r"[,|\n]+", caption)
    normalized = []
    for part in parts:
        cleaned = normalize_thumb_name(part)
        if cleaned:
            normalized.append(cleaned)
    return list(dict.fromkeys(normalized))


def extract_thumb_match_name(filename: str) -> str:
    base = ospath.splitext(filename)[0]
    arabic_match = _ARABIC_EPISODE_RE.search(base)
    if arabic_match:
        base = arabic_match.group(1)
    else:
        season_match = _SEASON_RE.search(base)
        if season_match:
            base = season_match.group(1)
    return normalize_thumb_name(base)
