import click

from os import path
from shutil import rmtree
from huggingface_hub import snapshot_download
from pathlib import Path

dirname = path.dirname(path.abspath(__file__))


@click.group(name='model')
def model_group():
    """Model related commands."""
    pass


@model_group.command(name='download')
def download_model():
    """Download the OmniParser models."""

    weights_path = path.join(dirname, '../../../../../weights')
    click.echo(f'downloading models to {weights_path}')
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_caption/*', local_dir=weights_path)
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_detect/*', local_dir=weights_path)

    # rename icon_caption to icon_caption_florence
    if path.exists(path.join(weights_path, 'icon_caption_florence')):
        # unlink a previously downloaded icon_caption_florence directory
        rmtree(path.join(weights_path, 'icon_caption_florence'))

    Path(path.join(weights_path, 'icon_caption')).rename(path.join(weights_path, 'icon_caption_florence'))

    click.echo('models downloaded successfully!')
