r"""
Export functions for the collection with
collection id ref_african_crops_kenya_02
"""
from pathlib import Path
import datetime

from src.utils import (
    get_all_assets,
    download_file,
    get_download_url,
)

from typing import Optional, Tuple


KENYA_O2_ID = "ref_african_crops_kenya_02"
KENYA_02_LABELS = "ref_african_crops_kenya_02_labels"
KENYA_02_SRC = "ref_african_crops_kenya_02_source"


def get_tile_and_date(feature_key: str, collection_id: str) -> Tuple[str, Optional[str]]:
    tileid = feature_key.split("_")[-2]

    if collection_id == KENYA_02_SRC:
        dateid = feature_key.split("_")[-1]
    elif collection_id == KENYA_02_LABELS:
        dateid = None
    else:
        raise AssertionError(f"collection id {collection_id} not recognized")

    return tileid, dateid


def download_kenya_02(
    download_path: Path,
    image_band: Optional[str] = None,
    ignore_source_images: bool = False,
) -> None:

    download_folder = download_path / KENYA_O2_ID
    download_folder.mkdir(exist_ok=True)

    for collection_id in [KENYA_02_LABELS, KENYA_02_SRC]:

        if (collection_id == KENYA_02_SRC):
            if ignore_source_images:
                continue

        assets = get_all_assets(collection_id=collection_id)

        for feature, feature_dict in assets.items():
            print(f"Downloading assets from {feature}")

            tileid, dateid = get_tile_and_date(feature, collection_id)

            feature_download_folder = download_folder / tileid
            if collection_id == KENYA_02_SRC:
                feature_download_folder = feature_download_folder / dateid
            feature_download_folder.mkdir(parents=True, exist_ok=True)

            for asset_key, asset_dict in feature_dict.items():
                if (collection_id == KENYA_02_SRC) and (image_band is not None):
                    if asset_key != image_band:
                        print(f"Skipping {asset_key} as it is not {image_band}")
                        continue
                print(f"Downloading {asset_key}")
                download_file(
                    url=get_download_url(asset_dict), download_path=feature_download_folder
                )
