from pathlib import Path
import datetime
import re

from .utils import (
    get_all_assets,
    download_file,
    get_download_url,
    download_s3_file,
)

from typing import Optional, Tuple


KENYA_O2_ID = "ref_african_crops_kenya_02"
KENYA_02_LABELS = "ref_african_crops_kenya_02_labels"
KENYA_02_SRC = "ref_african_crops_kenya_02_source"


def download_collection(
    collection_id: str,
    download_path: Path,
    image_band: Optional[str] = None,
    ignore_source_images: bool = False,
) -> None:

    if collection_id in [KENYA_02_SRC, KENYA_02_LABELS, KENYA_O2_ID]:
        download_kenya_02(
            download_path=download_path,
            image_band=image_band,
            ignore_source_images=ignore_source_images,
        )
    download_all_assets(
        collection_id=collection_id,
        download_path=download_path,
        image_band=image_band,
        ignore_source_images=ignore_source_images,
    )


def is_source_image(filename: str) -> bool:
    # if it maches the pattern "year_month_day_*",
    # then it is a source image.
    # This is only true for this collection
    return bool(re.match("\d{4}_\d{2}_\d{2}_.*", filename))


def get_date(filename: str) -> str:
    # extract the date
    return "".join(filename.split("_")[:3])


def download_all_assets(
    collection_id: str,
    download_path: Path,
    image_band: Optional[str] = None,
    ignore_source_images: bool = False,
) -> None:

    download_folder = download_path / collection_id
    download_folder.mkdir(exist_ok=True)

    assets = get_all_assets(collection_id=collection_id)

    for feature, feature_dict in assets.items():

        feature_folder = download_folder / feature
        feature_folder.mkdir(exist_ok=True)

        for asset_key, asset_dict in feature_dict.items():

            if not is_source_image(asset_key):
                print(f"Downloading {asset_key}")
                url = get_download_url(asset_dict)
                if url is not None:
                    download_file(url=url, download_path=feature_folder)
                else:
                    print("No url returned! No file being downloaded")
            elif not ignore_source_images:
                if (image_band is not None) and (not asset_key.endswith(image_band)):
                    print("Wrong image band - skipping")
                    continue
                print(f"Downloading {asset_key} from AWS")
                date_string = get_date(asset_key)
                date_folder = feature_folder / date_string
                date_folder.mkdir(exist_ok=True)
                if date_string == "20190924":
                    url = get_download_url(asset_dict)
                    if url is not None:
                        download_s3_file(url=url, download_path=date_folder)
                    else:
                        print("No url returned! No file being downloaded")


def get_tile_and_date(
    feature_key: str, collection_id: str
) -> Tuple[str, Optional[str]]:
    tileid = feature_key.split("_")[-2]

    if collection_id == KENYA_02_SRC:
        dateid: Optional[str] = feature_key.split("_")[-1]
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

        if collection_id == KENYA_02_SRC:
            if ignore_source_images:
                continue

        assets = get_all_assets(collection_id=collection_id)

        for feature, feature_dict in assets.items():
            print(f"Downloading assets from {feature}")

            tileid, dateid = get_tile_and_date(feature, collection_id)

            feature_download_folder = download_folder / tileid
            if collection_id == KENYA_02_SRC:
                assert dateid is not None  # shouldn't be None for source images
                feature_download_folder = feature_download_folder / dateid
            feature_download_folder.mkdir(parents=True, exist_ok=True)

            for asset_key, asset_dict in feature_dict.items():
                if (collection_id == KENYA_02_SRC) and (image_band is not None):
                    if asset_key != image_band:
                        print(f"Skipping {asset_key} as it is not {image_band}")
                        continue
                print(f"Downloading {asset_key}")
                url = get_download_url(asset_dict)
                if url is not None:
                    download_file(url=url, download_path=feature_download_folder)
                else:
                    print("No url returned! No file being downloaded")
