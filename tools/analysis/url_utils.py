"""URL parsing helpers shared by video analysis tools."""

from __future__ import annotations

from urllib.parse import urlsplit


def normalize_http_url(value: str) -> str | None:
    """Return a normalized HTTP(S) URL, or ``None`` for invalid input."""
    candidate = value.strip()
    if candidate.lower().startswith("www."):
        candidate = f"https://{candidate}"

    try:
        parsed = urlsplit(candidate)
        hostname = parsed.hostname
        parsed.port  # Validate malformed and out-of-range ports.
    except ValueError:
        return None

    if parsed.scheme.lower() not in {"http", "https"} or not hostname:
        return None
    if parsed.username is not None or parsed.password is not None:
        return None
    return parsed.geturl()


def _hostname_matches(hostname: str, domain: str) -> bool:
    return hostname == domain or hostname.endswith(f".{domain}")


def looks_like_url_reference(value: str) -> bool:
    """Return whether a source claims URL semantics rather than a local path."""
    candidate = value.strip()
    if candidate.startswith("//") or candidate.lower().startswith("www."):
        return True
    try:
        scheme = urlsplit(candidate).scheme
    except ValueError:
        return "://" in candidate
    if not scheme:
        return "://" in candidate
    if len(scheme) == 1 and len(candidate) > 2 and candidate[1] == ":" and candidate[2] in "/\\":
        return False
    return True


def detect_video_url_platform(value: str) -> str | None:
    """Classify a valid video URL by hostname without trusting substrings."""
    normalized = normalize_http_url(value)
    if normalized is None:
        return None

    parsed = urlsplit(normalized)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    path = parsed.path.lower()

    if _hostname_matches(hostname, "youtube.com"):
        return "shorts" if path == "/shorts" or path.startswith("/shorts/") else "youtube"
    if _hostname_matches(hostname, "youtu.be"):
        return "youtube"
    if _hostname_matches(hostname, "instagram.com"):
        return "instagram"
    if _hostname_matches(hostname, "tiktok.com"):
        return "tiktok"
    if _hostname_matches(hostname, "vimeo.com"):
        return "vimeo"
    if _hostname_matches(hostname, "twitter.com") or _hostname_matches(hostname, "x.com"):
        return "twitter"
    return "other_url"
