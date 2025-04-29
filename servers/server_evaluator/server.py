import traceback
from fastapi import FastAPI, HTTPException
import uvicorn
from logging_setup import configure_logging
from datetime import datetime
from models import EvaluationRequest
from executor import FunctionExecutor
from evaluators import FUNCTIONS  # Registry of available functions
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

    # Validation Function executor
    executor = FunctionExecutor(FUNCTIONS)

    # ---------------------------
    # Healthcheck Endpoint
    # ---------------------------
    @app.get('/healthcheck')
    def healthcheck_endpoint():
        return {
            "status": "Successful", 
            "message": "Service is operational!"
        }

    # ---------------------------
    # Evaluate Endpoint
    # ---------------------------
    @app.post("/evaluate")
    async def evaluate_endpoint(body: EvaluationRequest):
        try:
            result = executor.execute({"func": body.name, "args": body.args})
            return {"result": result}
        except Exception as e:
            logger.error(f"Error during function execution: {e}")
            raise HTTPException(status_code=500, detail=str(e))

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