"""Tests for Phantom source map."""

from __future__ import annotations

from phantom.source_map import SourceMap, SourceMapping


def test_source_mapping_dataclass():
    m = SourceMapping(original_line=10, transformed_line=12, file="app.py")
    assert m.original_line == 10
    assert m.transformed_line == 12
    assert m.file == "app.py"


def test_source_map_basic():
    sm = SourceMap()
    sm.add_mapping(1, 5, file="a.py")
    sm.add_mapping(2, 6, file="a.py")

    assert sm.original_to_transformed(1, file="a.py") == 5
    assert sm.original_to_transformed(2, file="a.py") == 6
    assert sm.original_to_transformed(3, file="a.py") is None

    assert sm.transformed_to_original(5, file="a.py") == 1
    assert sm.transformed_to_original(6, file="a.py") == 2
    assert sm.transformed_to_original(7, file="a.py") is None


def test_source_map_default_lookup():
    sm = SourceMap()
    sm.add_mapping(10, 20)
    assert sm.original_to_transformed(10) == 20
    assert sm.transformed_to_original(20) == 10
    assert sm.original_to_transformed(99) is None


def test_source_map_identity_map():
    sm = SourceMap.identity_map(5, file="test.py")
    assert len(sm) == 5
    for i in range(1, 6):
        assert sm.original_to_transformed(i, file="test.py") == i
        assert sm.transformed_to_original(i, file="test.py") == i

    assert sm.original_to_transformed(6, file="test.py") is None


def test_source_map_iteration():
    sm = SourceMap.identity_map(3)
    mappings = list(sm)
    assert len(mappings) == 3
    assert mappings[0].original_line == 1
    assert mappings[0].transformed_line == 1
