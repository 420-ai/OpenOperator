import click

from cli.commands.model import model_group


@click.command()
def hello():
    """Say hello."""
    click.echo('Hello, World!')


@click.group()
@click.version_option()
def main():
    """CLI for Echo Operator."""
    pass


main.add_command(model_group)

if __name__ == '__main__':
    main()
