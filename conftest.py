"""
conftest.py — Project-root pytest configuration.

Ensures the project root is on sys.path so all imports resolve
without needing per-file sys.path manipulation. This makes both
pytest and Pyre2/Pyright recognize `adapters`, `app`, and `lib`
as first-class packages from the project root.
"""
import sys
import os

# Guarantee the project root is the first entry on the path.
# pytest.ini already sets pythonpath = . but this makes it
# explicit for static analysis tools that parse conftest.py.
sys.path.insert(0, os.path.dirname(__file__))
