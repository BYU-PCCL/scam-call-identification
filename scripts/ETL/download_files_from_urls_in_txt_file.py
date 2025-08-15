import requests
import sys
import os
import re
from pathlib import Path

from src.ml_scam_classification.utils.file_models import (
    download_file_from_url,
    get_urls_from_text_file
)

if __name__ == "__main__":
    args = sys.argv
    print(args)
    # TODO - finish implementing args, using hard-coded values for now

    urls = get_urls_from_text_file("src/ml_scam_classification/data/candor/file_urls.txt")

    for i, url in enumerate(urls):
        if i <= 60:
            continue
        print(f"\n\n -> Downloading from URL: {i + 1}/{len(urls)} \n")
        print(url)
        print()
        download_file_from_url(url, 'D:\scam-detector\src\ml_scam_classification\data\candor')

"""
USAGE EXAMPLE/TEMPLATE


"""
