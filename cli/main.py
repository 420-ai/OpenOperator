import click

from commands.model import download_model


@click.group()
def cli():
    pass


@click.group()
def model():
    pass


cli.add_command(model)
model.add_command(download_model)

if __name__ == '__main__':
    cli()
