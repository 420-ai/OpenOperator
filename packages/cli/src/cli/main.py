import click

from cli.commands.model import model_group
from cli.commands.omniparser import omniparser_group
from cli.commands.ui import ui_start
from dotenv import load_dotenv

# loading variables from .env file
load_dotenv()


@click.command()
def hello():
    """Say hello."""
    click.echo('Hello, World!')


@click.group()
@click.version_option()
def main():
    """CLI for Echo Operator."""
    pass


main.add_command(hello)
main.add_command(model_group)
main.add_command(omniparser_group)
main.add_command(ui_start)

if __name__ == '__main__':
    main()
