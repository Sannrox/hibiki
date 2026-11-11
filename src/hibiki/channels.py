from __future__ import annotations

import grpc

# grpc-python leaves the HTTP/2 ``:authority`` pseudo-header empty for
# ``unix://`` targets. Tonic/hyper servers (Sekai and Chisei) treat an empty
# ``:authority`` as a protocol violation and reset every stream with
# ``RST_STREAM`` (PROTOCOL_ERROR). Pinning a valid default authority makes
# unix-socket targets behave exactly like ``host:port`` targets, for which the
# authority is already populated.
_CHANNEL_OPTIONS: tuple[tuple[str, str], ...] = (("grpc.default_authority", "localhost"),)


def insecure_channel(target: str) -> grpc.Channel:
    """Open an insecure gRPC channel that works over both TCP and unix sockets."""
    return grpc.insecure_channel(target, options=list(_CHANNEL_OPTIONS))
