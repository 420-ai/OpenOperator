import traceback
from fastapi import FastAPI, HTTPException
import uvicorn
from logging_setup import configure_logging
from evaluators.teams_telemetry import evaluate
from datetime import datetime
from models import EvaluationRequest
import setproctitle
import logging
import os
from dotenv import load_dotenv
load_dotenv()

try:

    # Port
    port = os.getenv("PORT", 5053)
    print("PORT", port)
    port = int(port)  # Convert to integer

    # Setup logging
    logs_path = os.getenv("LOG_PATH")
    print("LOG_PATH", logs_path)
    configure_logging(logs_path)
    logger = logging.getLogger("server_evaluator")
    print("Logging configured")

    app = FastAPI(title="OO Evaluator")


    @app.post("/evaluate")
    async def evaluate_endpoint(body: EvaluationRequest):
        filename = body.telemetry_file
        markers = body.markers

        logger.info("filename: %s", filename)
        logger.info("markers: %s", markers)

        response = evaluate(filename, markers)

        logger.info(f"Evaluation response: {response}")
        return response


    # ---------------------------
    # Run Server
    # ---------------------------
    if __name__ == "__main__":
        logger.info(f"Server starting on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Named the process for easier identification
        setproctitle.setproctitle("evaluator_server")

        try:
            uvicorn.run(
                "server:app",
                host="0.0.0.0",
                port=port,
                log_config=None,
                timeout_graceful_shutdown=0,
            )

        except Exception as e:
            logger.error(f"Exception while running Uvicorn: {e}")
            logger.error(traceback.format_exc())

except Exception as ee:
    logger.critical("Fatal error during startup")
    logger.critical(traceback.format_exc())