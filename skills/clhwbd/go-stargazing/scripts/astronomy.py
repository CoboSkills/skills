#!/usr/bin/env python3
"""Thin wrapper for compressed astronomy helpers."""

from __future__ import annotations

import gzip
from pathlib import Path

_IMPL = Path(__file__).with_name("astronomy_impl.py.gz")
with gzip.open(_IMPL, "rt", encoding="utf-8") as fh:
    code = fh.read()
exec(compile(code, str(_IMPL), "exec"), globals())
