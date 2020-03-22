"""
For the most part, these functions are copied from
https://github.com/radiantearth/mlhub-tutorials/blob/master/notebooks/radiant-mlhub-api-know-how.ipynb
"""
import requests
from urllib.parse import urlparse
from pathlib import Path
import boto3

from .token import get_headers, get_credentials

from typing import Dict, List, Optional


def get_collections() -> List[Dict]:
    r = requests.get(
        "https://api.radiant.earth/mlhub/v1/collections", headers=get_headers()
    )
    h = r.json()
    return h["collections"]


def get_download_url(asset_dict: Dict) -> str:
    r = requests.get(
        asset_dict.get("href"), headers=get_headers(), allow_redirects=False
    )
    return r.headers.get("Location")


def download_file(url: str, download_path: Path = Path(".")) -> None:
    filename = urlparse(url).path.split("/")[-1]
    savepath = download_path / filename

    if not savepath.exists():
        r = requests.get(url)
        f = savepath.open("wb")
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:
                f.write(chunk)
        f.close()
        print(f"Downloaded {filename}")
    else:
        print(f"{savepath} already exists! Skipping")


def download_s3_file(
    url: str, download_path: Path = Path(".")) -> None:

    access_key, secret_key = get_credentials()
    parsed_url = urlparse(url)

    bucket = parsed_url.hostname.split(".")[0]
    path = parsed_url.path[1:]
    filename = path.split("/")[-1]

    savepath = download_path / filename

    if not savepath.exists():
        s3 = boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )

        s3.download_file(
            bucket,
            path,
            savepath.absolute().as_posix(),
            ExtraArgs={"RequestPayer": "requester"},
        )
        print(f"Downloaded s3://{bucket}/{path}")
    else:
        print(f"{savepath} already exists! Skipping")


def get_all_assets(
    collection_id: str = "ref_african_crops_kenya_01",
    limit: int = 10,
    bounding_box: Optional[List] = None,
    date_time: Optional[List] = None,
) -> Dict:

    if bounding_box is None:
        bounding_box = []

    if date_time is None:
        date_time = []

    r = requests.get(
        f"https://api.radiant.earth/mlhub/v1/collections/{collection_id}/items",
        params={"limit": limit, "bbox": bounding_box, "datetime": date_time},
        headers=get_headers(),
    )
    collection = r.json()

    if collection.get("code") == 401:
        print(f"Error!: {collection}")
        return {}

    output_assets = {}

    # for the ref_african_crops_kenya_01, features is only a list of length 1
    for feature in collection.get("features", []):
        selected_item = feature
        output_assets[feature.get("id")] = feature.get("assets")
    return output_assets
