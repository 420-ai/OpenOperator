from websockify import WebSocketProxy
import click


@click.command()
@click.option("--target-host", default="127.0.0.1")
@click.option("--target-port", default=5900)
def start_websockify(target_host: str, target_port: int):
    """
    Start the websockify server to proxy WebSocket connections to VNC.
    """
    
    click.echo(f"Starting websockify server... {target_host}:{target_port}")
    WebSocketProxy(
        target_host=target_host,
        target_port=target_port,
        listen_host="127.0.0.1",
        listen_port=8081,
    ).start_server()


if __name__ == "__main__":
    start_websockify()
