import traceback
from fastapi import FastAPI, HTTPException
from models import EvaluationRequest, EvaluationResponse
from evaluator import process_evaluation
import uvicorn
from logging_setup import configure_logging
import logging
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

port = os.getenv("PORT", 5053)

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    try:
        response = process_evaluation(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    LOG_PATH=os.getenv("LOG_PATH", r"C:\Logs")
    configure_logging(LOG_PATH)
    logger = logging.getLogger("server_evaluator")
    logger.info("starting eval server...")
    try:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=port,
            # reload=True,
            log_config=None,
            timeout_graceful_shutdown=0,
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        error_traceback = traceback.format_exc()
        print(error_traceback)
