import click

from os import path
from shutil import rmtree
from huggingface_hub import snapshot_download
from pathlib import Path

dirname = path.dirname(path.abspath(__file__))

@click.group(name="download")
def download():
    """Download models from Hugging Face Hub."""
    pass

@download.command(name='omniparser')
def download_omniparser():
    """Download the OmniParser models."""
    weights_path = str(Path(path.join(dirname, '../vision/omniparser')).resolve())
    
    click.echo(f'downloading models to {weights_path}')
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_caption/*', local_dir=weights_path)
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_detect/*', local_dir=weights_path)

    # rename icon_caption to icon_caption_florence
    if path.exists(path.join(weights_path, 'icon_caption_florence')):
        # unlink a previously downloaded icon_caption_florence directory
        rmtree(path.join(weights_path, 'icon_caption_florence'))

    Path(path.join(weights_path, 'icon_caption')).rename(path.join(weights_path, 'icon_caption_florence'))

    click.echo('models downloaded successfully!')

if __name__ == '__main__':
    download()