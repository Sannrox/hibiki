from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,62}$")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
FALSE_VALUES = frozenset({"0", "false", "no", "off"})


class ConfigurationError(ValueError):
    """Raised when Hibiki's non-secret runtime configuration is invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    namespace: str
    tenkai_repository: str
    birdclaw_account: str
    chisei_target: str
    allow_live_writes: bool

    @classmethod
    def from_environ(cls, environ: Mapping[str, str]) -> Settings:
        namespace = environ.get("HIBIKI_NAMESPACE", "hibiki").strip()
        repository = _required(environ, "HIBIKI_TENKAI_REPOSITORY")
        account = _required(environ, "HIBIKI_BIRDCLAW_ACCOUNT")
        target = _required(environ, "HIBIKI_CHISEI_TARGET")
        live_writes = _boolean(environ.get("HIBIKI_ALLOW_LIVE_WRITES", "false"))

        errors: list[str] = []
        if not NAMESPACE_PATTERN.fullmatch(namespace):
            errors.append("HIBIKI_NAMESPACE must be a lowercase namespace identifier")
        if not REPOSITORY_PATTERN.fullmatch(repository):
            errors.append("HIBIKI_TENKAI_REPOSITORY must use OWNER/REPOSITORY form")
        if any(character.isspace() for character in account):
            errors.append("HIBIKI_BIRDCLAW_ACCOUNT must not contain whitespace")
        if not _valid_grpc_target(target):
            errors.append("HIBIKI_CHISEI_TARGET must be HOST:PORT or unix:///absolute/path")
        if errors:
            raise ConfigurationError("; ".join(errors))

        return cls(namespace, repository, account, target, live_writes)

    def public_dict(self) -> dict[str, str | bool]:
        return {
            "namespace": self.namespace,
            "tenkai_repository": self.tenkai_repository,
            "birdclaw_account": self.birdclaw_account,
            "chisei_target": self.chisei_target,
            "allow_live_writes": self.allow_live_writes,
        }


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} is required")
    return value


def _boolean(raw: str) -> bool:
    value = raw.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ConfigurationError(
        "HIBIKI_ALLOW_LIVE_WRITES must be one of true/false, 1/0, yes/no, or on/off"
    )


def _valid_grpc_target(target: str) -> bool:
    if target.startswith("unix:///"):
        return len(target) > len("unix:///")
    if "://" in target or target.count(":") != 1:
        return False
    host, separator, port = target.rpartition(":")
    return bool(separator and host and port.isdigit() and 0 < int(port) <= 65535)
