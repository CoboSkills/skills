#!/usr/bin/env python3
"""Thin wrapper for the compressed go-stargazing engine.

ClawHub publish embeds text files for indexing; the full implementation is large,
so we ship it as a compressed `.py.gz` payload and load it at runtime.
"""

from __future__ import annotations

import gzip
import sys
import types
from pathlib import Path

_IMPL = Path(__file__).with_name("dynamic_sampling_prototype_impl.py.gz")
_MODULE_NAME = "_dynamic_sampling_prototype_impl_"
_module = types.ModuleType(_MODULE_NAME)
_module.__file__ = str(_IMPL)
_module.__package__ = None
sys.modules[_MODULE_NAME] = _module

with gzip.open(_IMPL, "rt", encoding="utf-8") as fh:
    code = fh.read()
exec(compile(code, str(_IMPL), "exec"), _module.__dict__)

main = _module.__dict__["main"]

if __name__ == "__main__":
    main()
