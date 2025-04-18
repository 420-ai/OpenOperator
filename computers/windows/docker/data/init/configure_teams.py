
def configure_teams(username: str):
    try:
        # copy the "configuration.json" to the installation location: 
        teams_path = fr"\users\{username}\appdata\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams"
        teams_config_path = os.path.join(
            teams_path, "configuration.json"
        )

        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), "configuration.json"),
            teams_config_path,
        )

    except Exception as e:
        logging.error(f"Failed to copy Teams configuration: {e}")
        raise
        