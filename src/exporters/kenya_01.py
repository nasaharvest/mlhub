r"""
Export functions for the collection with
collection id ref_african_crops_kenya_01
"""
from pathlib import Path
import pandas as pd
import re

from src.utils import (
    get_all_assets,
    download_file,
    get_download_url,
    download_s3_file,
)

from typing import Dict, Optional


KENYA_01_ID = "ref_african_crops_kenya_01"


def is_source_image(filename: str) -> bool:
    # if it maches the pattern "year_month_day_*",
    # then it is a source image.
    # This is only true for this collection
    return re.match("\d{4}_\d{2}_\d{2}_.*", filename)


def get_date(filename: str) -> str:
    # extract the date
    return "".join(filename.split("_")[:3])


def download_kenya_01(
    download_path: Path,
    image_band: Optional[str] = "b03",
    ignore_source_images: bool = False,
) -> None:

    download_folder = download_path / KENYA_01_ID
    download_folder.mkdir(exist_ok=True)

    assets = get_all_assets(collection_id=KENYA_01_ID)

    for feature, feature_dict in assets.items():

        feature_folder = download_folder / feature
        feature_folder.mkdir(exist_ok=True)

        for asset_key, asset_dict in feature_dict.items():

            if not is_source_image(asset_key):
                print(f"Downloading {asset_key}")
                download_file(
                    url=get_download_url(asset_dict), download_path=feature_folder
                )
            elif not ignore_source_images:
                if (image_band is not None) and (not asset_key.endswith(image_band)):
                    print("Wrong image band - skipping")
                    continue
                print(f"Downloading {asset_key} from AWS")
                date_string = get_date(asset_key)
                date_folder = feature_folder / date_string
                date_folder.mkdir(exist_ok=True)
                if date_string == "20190924":
                    download_s3_file(
                        url=get_download_url(asset_dict),
                        download_path=date_folder)
