import click

from commands.model import download_model


@click.group()
def cli():
    pass


@click.group()
def model():
    pass

def main():
    cli.add_command(model)
    model.add_command(download_model)
    cli()

if __name__ == '__main__':
    main()
