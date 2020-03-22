from datetime import date
import pandas as pd
from collections import defaultdict

from .exporters import is_source_image

from typing import Dict, DefaultDict, List, Tuple


def parse_asset_name(asset_name: str) -> Tuple[int, int, int, str]:
    split_vals = asset_name.split("_")

    return int(split_vals[0]), int(split_vals[1]), int(split_vals[2]), split_vals[3]


def features_to_df(features_dict: Dict) -> pd.DataFrame:
    r"""
    Return a pandas dataframe describing all the assets
    """
    features: List[str] = []
    dates: List[date] = []
    bands: List[str] = []

    for feature, f_dict in features_dict.items():

        for asset, asset_dict in f_dict.items():
            if is_source_image(asset):
                year, month, day, band = parse_asset_name(asset)

                features.append(feature)
                dates.append(date(year=year, month=month, day=day))
                bands.append(band)
    return pd.DataFrame({"feature": features, "image_date": dates, "bands": bands})


def check_dates_across_features(features_df: pd.DataFrame, check_all_bands: bool = True) -> pd.DataFrame:

    date_list: List[date] = []
    feature_complete: Dict[str: List[bool]] = defaultdict(list)
    all_features = features_df.feature.unique()
    all_bands = features_df.bands.unique()
    for unique_date in features_df.image_date.unique():
        date_list.append(unique_date)
        for feature in all_features:
            sub_df = features_df[((features_df.feature == feature) & (features_df.image_date == unique_date))]

            if len(sub_df) == 0:
                feature_complete[feature].append(False)
            elif check_all_bands:
                feature_complete[feature].append(len(sub_df.bands.unique()) == len(all_bands))
            else:
                feature_complete[feature].append(True)
    feature_complete["image_date"] = date_list
    df = pd.DataFrame(feature_complete)
    df = df.set_index("image_date")
    return df
