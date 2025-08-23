"""Download utilities for mflux weights with cache-first behavior."""

import sys

import requests
import urllib3
from huggingface_hub import snapshot_download as hf_snapshot_download


def snapshot_download(repo_id: str, **kwargs) -> str:
    """Download repo files with cache-first behavior.

    This wrapper function is a wrapper for upstream hf_snapshot_download

    2025-07-08 HOT FIX: just pass the args through for now, see #235 discussion
    """
    try:
        return hf_snapshot_download(repo_id, **kwargs)
    except (KeyboardInterrupt, requests.exceptions.ConnectionError, urllib3.exceptions.NameResolutionError):
        print(
            "Could not connect to HuggingFace to download model weights.\n"
            "If you are running without internet or when HuggingFace is down,\n"
            "you can bypass this by setting environment variable TRANSFORMERS_OFFLINE=1"
        )
        sys.exit(1)
