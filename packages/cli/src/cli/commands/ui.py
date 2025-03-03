import click


@click.command(name='ui')
def ui_start():
    """Start the UI for Echo Operator."""

    from echo_operator_ui.app import app

    app.launch(pwa=True)
