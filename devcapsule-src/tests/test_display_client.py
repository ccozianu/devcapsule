"""Host side of the contained display: port, URL, readiness, opener choice."""

from __future__ import annotations

import socket
from threading import Event
from unittest.mock import patch

import pytest

from devcapsule.display_client import (
    accepts_connections,
    allocate_loopback_port,
    default_opener,
    display_url,
    new_display_token,
    watch_display_ready,
)
from devcapsule.host_open import HOST_OPEN_SOCKET_ENV, HostOpenError


def test_token_and_port_are_fresh_and_usable() -> None:
    token = new_display_token()
    assert len(token) == 48 and token != new_display_token()
    port = allocate_loopback_port()
    assert 0 < port < 65536
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", port))  # still free a moment later


def test_display_url_autoconnects_through_the_token_path() -> None:
    url = display_url(6080, "abc123")
    assert url == "http://127.0.0.1:6080/vnc.html?autoconnect=1&resize=remote&path=websockify%3Ftoken%3Dabc123"


def test_watcher_opens_once_the_port_answers_and_reports_opener_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(8)  # each probe leaves one accepted-but-unread connection behind
    port = listener.getsockname()[1]
    opened: list[str] = []
    try:
        assert accepts_connections(port)
        watch_display_ready(port, "http://u", opened.append, Event()).join(timeout=10)
        assert opened == ["http://u"]
        assert capsys.readouterr().err == ""  # the opener, not the watcher, reports what it did

        def failing(url: str) -> None:
            raise HostOpenError("no browser")

        watch_display_ready(port, "http://u", failing, Event()).join(timeout=10)
        assert "could not be opened (no browser); open it yourself: http://u" in capsys.readouterr().err
    finally:
        listener.close()


def test_watcher_gives_up_on_timeout_or_stop(capsys: pytest.CaptureFixture[str]) -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    assert not accepts_connections(port)
    opened: list[str] = []
    watch_display_ready(port, "http://u", opened.append, Event(), timeout=0.3).join(timeout=10)
    assert opened == []
    assert f"did not answer on port {port} within 0.3s" in capsys.readouterr().err
    stop = Event()
    thread = watch_display_ready(port, "http://u", opened.append, stop, timeout=60)
    stop.set()
    thread.join(timeout=10)
    assert not thread.is_alive() and opened == []


def test_default_opener_prefers_the_host_bridge_inside_a_capsule(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("devcapsule.display_client.in_container", return_value=True):
        default_opener({})("http://u")
        assert "ready; open it in a browser: http://u" in capsys.readouterr().err
        with patch("devcapsule.display_client.open_host_url") as bridge:
            default_opener({HOST_OPEN_SOCKET_ENV: "/run/bridge.sock"})("http://u")
        bridge.assert_called_once()
        assert bridge.call_args.args == ("http://u",)
        assert "opened through the host-browser bridge" in capsys.readouterr().err
    with (
        patch("devcapsule.display_client.in_container", return_value=False),
        patch("devcapsule.display_client.webbrowser.open", return_value=False) as browser,
    ):
        with pytest.raises(HostOpenError, match="no browser could be started"):
            default_opener({})("http://u")
        browser.assert_called_once_with("http://u", new=2)
    with (
        patch("devcapsule.display_client.in_container", return_value=False),
        patch("devcapsule.display_client.webbrowser.open", return_value=True),
    ):
        default_opener({})("http://u")
        assert "opened in your browser" in capsys.readouterr().err
