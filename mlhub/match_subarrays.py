r"""
The ref_african_crops_kenya_02 has false coordinates, making it hard to
use additional data (e.g. from beyond the provided timesteps).

This provides some functions which make it easier to retrieve the original
coordinates, by comparing the images to the original images from sentinel
"""

import xarray as xr
import numpy as np

from typing import Tuple, Optional


def to_array(da: xr.DataArray) -> np.ndarray:
    return np.squeeze(da.values, 0)


def find_subarray_indices(
    reference_array: xr.DataArray,
    subarray: xr.DataArray,
    start_x: Optional[int] = None,
    start_y: Optional[int] = 5000,
    max_x: Optional[int] = None,
    max_y: Optional[int] = 5500,
    search_size: int = 10,
    scaling_sub_to_ref: float = 10000,
    verbose: bool = False,
) -> Tuple[int, int]:
    r"""
    :param superarray: The array within which subarray is
    :param subarray: An array which is a subset of superarray

    :returns: a tuple (x, y) indicating the position in array where the bottom left corner of subarray is.
    """
    np_refarray = to_array(reference_array)
    np_subarray = to_array(subarray) * scaling_sub_to_ref

    if start_x is None:
        start_x = 0
    if start_y is None:
        start_y = 0

    if max_y is None:
        max_y = np_refarray.shape[0] - np_subarray.shape[0]
    else:
        max_y = min(max_y, np_refarray.shape[0] - np_subarray.shape[0])

    if max_x is None:
        max_x = np_refarray.shape[1] - np_subarray.shape[1]
    else:
        max_x = min(max_x, np_refarray.shape[1] - np_subarray.shape[1])

    search_subarray = np_subarray[:search_size, :search_size]
    # look for similarity between the areas instead of matching
    for i in range(start_y, max_y):
        if verbose:
            print(f"i: {i}")
        for j in range(start_x, max_x):
            array_subset = np_refarray[i : i + search_size, j : j + search_size]
            assert array_subset.shape == search_subarray.shape
            if np.isclose(array_subset, search_subarray, atol=5).all():
                return (j, i)
    print("No coordinates found!")


def get_coordinates_from_indices(
    super_da: xr.DataArray, sub_da: xr.DataArray, x_start: int, y_start: int,
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Return the x and y for the sub_da, given the coordinates
    x, y found by find_subarray

    :param super_da: The DataArray whose coordinates are being taken
    :param sub_da: The DataArray whose coordinates will be replaced
    :x_start: The location of the top left x coordinate of sub_da in super_da,
        found using find_subarray
    :y_start: The location of the top left y coordinate of sub_da in super_da,
        found using find_subarray

    :returns: A tuple of np.ndarrays representing the x and y coordinates
    """

    return (
        super_da.x[x_start : x_start + sub_da.x.shape[0]].values,
        super_da.y[y_start : y_start + sub_da.y.shape[0]].values,
    )


def update_coords_and_attrs(
    reference_da: xr.DataArray, da_to_update: xr.DataArray, x_start: int, y_start: int
) -> xr.DataArray:

    new_x, new_y = get_coordinates_from_indices(
        reference_da, da_to_update, x_start, y_start
    )

    da_to_update["x"] = new_x
    da_to_update["y"] = new_y

    # we also want to update some of the attributes
    if "transform" in reference_da.attrs:
        da_to_update.attrs["transform"] = reference_da.attrs["transform"]
    if "crs" in reference_da.attrs:
        da_to_update.attrs["crs"] = reference_da.attrs["crs"]
    if "res" in reference_da.attrs:
        da_to_update.attrs["res"] = reference_da.attrs["res"]

    return da_to_update
