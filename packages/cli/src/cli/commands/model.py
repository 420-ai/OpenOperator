import click
from huggingface_hub import snapshot_download
from pathlib import Path

@click.command(name='download')
def download_model():
    click.echo('downloading models')
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_caption/*', local_dir='../weights')
    snapshot_download('microsoft/OmniParser-v2.0', allow_patterns='icon_detect/*', local_dir='../weights')
    # rename icon_detect to icon_detect_florence
    Path('../weights/icon_detect').rename('../weights/icon_detect_florence')