import time
from fastapi import FastAPI
from pydantic import BaseModel
from os import path
from typing import TypedDict
from download import download_omniparser
import os
from datetime import datetime
from torch import cuda
from util.omniparser import Omniparser
import uvicorn
import traceback
import logging
from logging_setup import configure_logging

from dotenv import load_dotenv
load_dotenv()


# Port
port = os.getenv("PORT")
print(port)
port = int(port)  # Convert to integer

# Setup logging
logs_path = os.getenv("LOG_PATH")
print(logs_path)
os.makedirs(logs_path, exist_ok=True)

configure_logging(logs_path)
logger = logging.getLogger("server_omniparser")

try:

    root_dir = path.dirname(__file__)
    weights_dir = path.join(root_dir, 'weights')

    if path.exists(weights_dir) == False:
        os.makedirs(weights_dir, exist_ok=True)
        logger.info('weights folder not found, downloading models...')
        download_omniparser(weights_dir)
        logger.info('models downloaded successfully!')


    class Config(TypedDict):
        som_model_path: str
        caption_model_name: str
        caption_model_path: str
        device: str
        BOX_TRESHOLD: float


    class ParseRequest(BaseModel):
        base64_image: str


    config: Config = {
        'som_model_path': path.join(weights_dir, 'icon_detect/model.pt'),
        'caption_model_name': 'florence2',
        'caption_model_path': path.join(weights_dir, 'icon_caption_florence'),
        'device': 'cuda' if cuda.is_available() else 'cpu',
        'BOX_TRESHOLD': 0.05,
    }

    if config:
        config.update(config)

    omniparser = Omniparser(config)

    app = FastAPI()


    @app.post('/parse')
    async def parse(parse_request: ParseRequest):
        logger.info('start parsing...')
        start = time.time()
        dino_labled_img, parsed_content_list = omniparser.parse(parse_request.base64_image)
        latency = time.time() - start
        logger.info(f'time: {latency:.2f} seconds')
        return {
            'som_image_base64': dino_labled_img,
            'parsed_content_list': parsed_content_list,
            'latency': latency,
        }


    @app.get('/healthcheck')
    async def healthcheck():
        return {
            "status": "Successful", 
            "message": "Service is operational!"
        }


    print("Starting server...")
    if __name__ == '__main__':
        logger.info(f"Server started on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            uvicorn.run(
                "server:app", 
                host="0.0.0.0",  
                port=port, 
                reload=False,
                log_config=None,  # Disable Uvicorn's default logging setup
            )
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            error_traceback = traceback.format_exc()
            logger.error(error_traceback)
    
except Exception as ee:
    logger.error("An unexpected error occurred:", ee)
    error_traceback = traceback.format_exc()
    logger.error(error_traceback)