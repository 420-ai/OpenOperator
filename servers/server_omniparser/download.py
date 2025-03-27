from os import path
from shutil import rmtree
from huggingface_hub import snapshot_download
from pathlib import Path
import logging

logger = logging.getLogger("server_omniparser_download")

def download_omniparser(weights_path: str):
    """Download the OmniParser models."""
    
    logger.info(f'downloading models to {weights_path} ...')
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_caption/*', local_dir=weights_path)
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_detect/*', local_dir=weights_path)

    # rename icon_caption to icon_caption_florence
    if path.exists(path.join(weights_path, 'icon_caption_florence')):
        # unlink a previously downloaded icon_caption_florence directory
        rmtree(path.join(weights_path, 'icon_caption_florence'))

    Path(path.join(weights_path, 'icon_caption')).rename(path.join(weights_path, 'icon_caption_florence'))

    logger.info('models downloaded successfully!')