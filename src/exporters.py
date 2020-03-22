from pathlib import Path
import requests

from src.utils import (
    get_all_assets,
    is_source_image,
    download_file,
    get_download_url,
    download_s3_file,
)

from typing import Dict, Optional, List


KENYA_ID = "ref_african_crops_kenya_01"


def download_kenya_02(
    download_path: Path,
    image_type: Optional[str] = "tci",
    ignore_source_images: bool = False,
) -> None:
    download_by_id(
        collection_id=KENYA_ID,
        download_path=download_path,
        image_type=image_type,
        ignore_source_images=ignore_source_images,
    )


def download_kenya_01(
    download_path: Path,
    image_type: Optional[str] = "tci",
    ignore_source_images: bool = False,
) -> None:
    download_by_id(
        collection_id=KENYA_ID,
        download_path=download_path,
        image_type=image_type,
        ignore_source_images=ignore_source_images,
    )


def download_by_id(
    collection_id: str,
    download_path: Path,
    image_type: Optional[str] = "tci",
    ignore_source_images: bool = False,
) -> None:

    download_folder = download_path / collection_id
    download_folder.mkdir(exist_ok=True)

    assets = get_all_assets(collection_id=collection_id)

    for asset_key, asset_dict in assets.items():

        print(f"Downloading {asset_key}")
        if not is_source_image(asset_key):
            download_file(
                url=get_download_url(asset_dict), download_path=download_folder
            )
        elif not ignore_source_images:
            if (image_type is not None) and (not asset_key.endswith(image_type)):
                print("Wrong image type - skipping")
                continue

            print("Downloading from AWS")
            download_s3_file(
                url=get_download_url(asset_dict),
                download_path=download_folder,
                file_prefix=asset_key,
            )
