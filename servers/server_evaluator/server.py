from fastapi import FastAPI, HTTPException
from models import EvaluationRequest, EvaluationResponse
from evaluator import process_evaluation

app = FastAPI()

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    try:
        response = process_evaluation(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
