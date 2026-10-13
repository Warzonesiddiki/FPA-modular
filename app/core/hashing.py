"""SHA-256 helpers for files, rows and audit chains (docs 12, 24)."""
from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def chain_hash(prev_hash: str, canonical_payload: str) -> str:
    return hashlib.sha256(f"{prev_hash}|{canonical_payload}".encode("utf-8")).hexdigest()
