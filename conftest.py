
# Shared pytest setup.

# pytest automatically discovers a file named conftest.py and makes the fixtures
# defined here available to every test file — no import needed.

import pytest


@pytest.fixture(autouse=True)
def isolated_data_files(monkeypatch, tmp_path):
    # Run every test inside its own empty temporary directory.

    # auth.py and notes.py read and write users.json / notes.json using relative
    # paths, so moving into a fresh temp dir gives each test its own clean data
    # files. Real users.json and notes.json are never touched, and tests
    # never interfere with each other.

    # autouse=True means this applies to every test automatically.
    monkeypatch.chdir(tmp_path)
