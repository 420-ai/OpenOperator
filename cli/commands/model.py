import click


@click.command(name="download")
def download_model():
    click.echo("downloading models")
