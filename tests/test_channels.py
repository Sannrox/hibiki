from typing import Any

import grpc

from hibiki import channels


def test_insecure_channel_pins_default_authority(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_insecure_channel(target: str, options: Any = None) -> object:
        captured["target"] = target
        captured["options"] = options
        return object()

    monkeypatch.setattr(grpc, "insecure_channel", fake_insecure_channel)

    channels.insecure_channel("unix:///tmp/sekai.sock")

    assert captured["target"] == "unix:///tmp/sekai.sock"
    # An empty :authority makes Tonic/hyper reset unix-socket streams with
    # RST_STREAM; pinning it keeps unix and TCP targets behaving the same.
    assert ("grpc.default_authority", "localhost") in captured["options"]
