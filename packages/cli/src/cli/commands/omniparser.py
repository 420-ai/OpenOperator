import click
from server_omniparser.server import OmniParserServer

@click.group(name='omniparser')
def omniparser_group():
    """OmniParser related commands."""
    pass

@omniparser_group.command(name='start')
@click.option('--host', default='localhost', help='Host to bind the server to')
@click.option('--port', default=8000, type=int, help='Port to bind the server to')
def start_omniparser_server(host, port):
    """Start the OmniParser server."""
    click.echo(f'Starting OmniParser server on {host}:{port}')
    server = OmniParserServer()
    server.start(host=host, port=port)
