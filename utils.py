"""
Utility functions.
"""

import os

def ensure_assets_dir(assets_dir: str):
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
