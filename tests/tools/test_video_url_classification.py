from __future__ import annotations

import pytest

from tools.analysis.url_utils import detect_video_url_platform
from tools.analysis.video_analyzer import VideoAnalyzer
from tools.analysis.video_downloader import VideoDownloader


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=abc", "youtube"),
        ("https://m.youtube.com/shorts/abc", "shorts"),
        ("https://youtu.be/abc", "youtube"),
        ("https://subdomain.instagram.com/reel/abc", "instagram"),
        ("https://www.tiktok.com/@example/video/1", "tiktok"),
        ("https://vimeo.com/123456", "vimeo"),
        ("https://x.com/example/status/1", "twitter"),
        ("https://youtube.com.evil.example/watch?v=abc", "other_url"),
        ("https://evil.example/?next=instagram.com", "other_url"),
    ],
)
def test_video_platform_uses_the_url_hostname(url: str, expected: str) -> None:
    assert detect_video_url_platform(url) == expected


@pytest.mark.parametrize(
    "url",
    ["https://youtube.com:not-a-port/watch?v=abc", "https://youtube.com:70000/watch?v=abc"],
)
def test_video_platform_rejects_invalid_ports(url: str) -> None:
    assert detect_video_url_platform(url) is None


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/video.mp4",
        "https://user:password@youtube.com/watch?v=abc",
    ],
)
def test_video_downloader_rejects_unsafe_urls_before_io(tmp_path, url: str) -> None:
    output_dir = tmp_path / "download"

    result = VideoDownloader().execute(
        {"url": url, "output_dir": str(output_dir), "format": "metadata_only"}
    )

    assert result.success is False
    assert result.error == "url must be a valid HTTP(S) URL without embedded credentials"
    assert not output_dir.exists()


@pytest.mark.parametrize(
    "source",
    [
        "file:///etc/passwd",
        "file:/etc/passwd",
        "data:text/plain,hello",
        "mailto:test@example.com",
        "//example.com/video.mp4",
        "ftp://example.com/video.mp4",
        "https://user:password@youtube.com/watch?v=abc",
    ],
)
def test_video_analyzer_rejects_unsafe_urls_before_io(tmp_path, source: str) -> None:
    output_dir = tmp_path / "analysis"

    result = VideoAnalyzer().execute(
        {"source": source, "output_dir": str(output_dir)}
    )

    assert result.success is False
    assert result.error == "source URL must use HTTP(S) without embedded credentials"
    assert not output_dir.exists()
