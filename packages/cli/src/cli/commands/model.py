import click

from os import path
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
    
    # rename icon_detect to icon_detect_florence
    if path.exists(path.join(weights_path, 'icon_detect_florence')):
        # remove it 
        click.echo('removing existing icon_detect_florence')
        Path(path.join(weights_path, 'icon_detect_florence')).unlink(missing_ok=True)

    Path(path.join(weights_path, 'icon_detect')).rename(path.join(weights_path, 'icon_detect_florence'))
