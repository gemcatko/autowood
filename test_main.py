import pytest
import main

def test_bb_intersection_over_union():
    boxA = [0.0, 0.0, 50.0, 50.0]
    boxB = [0, 0, 100, 100]
    assert round(main.bb_intersection_over_union(boxA,boxB), 2) == 0.25

def test_bb_intersection_over_union_2():
    boxA = [0.0, 0.0, 150.0, 150.0]
    boxB = [0, 0, 100, 100]
    assert round(main.bb_intersection_over_union(boxA,boxB), 2) == 0.45

def test_bb_intersection_over_union3():
    boxA = [0.0, 0.0, 50.0, 50.0]
    boxB = [60, 60, 100, 100]
    assert round(main.bb_intersection_over_union(boxB,boxA), 2) == 0.25