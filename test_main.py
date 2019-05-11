import pytest
import main

def test_bb_intersection_over_union_prekrivaju():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [50.0, 50.0, 50.0, 50.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 1

def test_bb_intersection_over_union_prekrivaju_vecsi_v_mensom():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [50.0, 50.0, 100.0, 100.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0.25

def test_bb_intersection_over_union_next_to_50_p_owerlap():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [75.0, 50.0, 50.0, 50.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0.34

def test_bb_intersection_over_union_not_owerlap():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [100.0, 100.0, 50.0, 50.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0

def test_bb_intersection_over_union_digits():
    boundsA = [50.222, 50.444, 50.444, 50.54353463634]
    boundsB = [50.123234, 50.5435634, 50.54645, 50.324235]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0.99


