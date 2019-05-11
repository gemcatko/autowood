import pytest
import main

def test_bb_intersection_over_union_one_on_one():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [50.0, 50.0, 50.0, 50.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 1

def test_bb_intersection_over_union_bigger_in_smaller():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [50.0, 50.0, 100.0, 100.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0.25

def test_bb_intersection_over_union_next_to_33_p_owerlap():
    """
    using xywh format
    :return:
    """
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [75.0, 50.0, 50.0, 50.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0.34

def test_bb_intersection_over_union_not_owerlap():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [100.0, 100.0, 50.0, 50.0]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0

def test_bb_intersection_over_union_small_digits():
    boundsA = [50.222, 50.444, 50.444, 50.54353463634]
    boundsB = [50.123234, 50.5435634, 50.54645, 50.324235]
    assert round(main.bb_intersection_over_union(boundsA,boundsB), 2) == 0.99

def test_get_bounding_box_of_area_ower_union_sane_objects():
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [50.0, 50.0, 50.0, 50.0]
    assert main.get_bounding_box_around_area_ower_union(boundsB, boundsA) == [50.0, 50.0, 50.0, 50.0]

def test_get_bounding_box_of_area_ower_union_sane_objects_owerlap():
    """
       using xywh format
       :return: xAyAxByB
    """

    boundsA = [50.0, 50.0, 100.0, 100.0]
    boundsB = [100.0, 100.0, 100.0, 100.0]
    assert main.get_bounding_box_around_area_ower_union(boundsB, boundsA) == [0, 0, 150.0, 150.0]

def test_get_bounding_box_of_area_ower_union_sane_objects_owerlap_33p():
    """
       using xywh format
       :return: xAyAxByB
    """
    boundsA = [50.0, 50.0, 50.0, 50.0]
    boundsB = [75.0, 50.0, 50.0, 50.0]
    assert main.get_bounding_box_around_area_ower_union(boundsB, boundsA) == [25, 25, 100, 75]


