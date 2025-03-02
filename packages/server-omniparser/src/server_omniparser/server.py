import os
import sys
import time
import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypedDict, Optional
from util.omniparser import Omniparser

root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)


class Config(TypedDict):
    som_model_path: str
    caption_model_name: str
    caption_model_path: str
    device: str
    BOX_TRESHOLD: float


class ParseRequest(BaseModel):
    base64_image: str


class OmniParserServer:
    app = FastAPI()

    def __init__(self, config: Optional[Config] = None):
        self.config: Config = {
            'som_model_path': '../../../../weights/icon_detect_florence/model.pt',
            'caption_model_name': 'florence2',
            'caption_model_path': '../../../../weights/icon_caption',
            'device': 'cpu',
            'BOX_TRESHOLD': 0.05,
        }

        if config:
            self.config.update(config)

        self.omniparser = Omniparser(self.config)

    @app.post('/parse/')
    async def parse(self, parse_request: ParseRequest):
        print('start parsing...')
        start = time.time()
        dino_labled_img, parsed_content_list = self.omniparser.parse(parse_request.base64_image)
        latency = time.time() - start
        print('time:', latency)
        return {'som_image_base64': dino_labled_img, 'parsed_content_list': parsed_content_list, 'latency': latency}

    @app.get('/probe/')
    async def root():
        return {'message': 'Omniparser API ready'}

    def start(self, host: str = 'localhost', port: int = 8000):
        """Start the FastAPI server."""
        print(f'Starting server at http://{host}:{port}')
        uvicorn.run('server:app', host=host, port=port, reload=True)

# export this class variable for uvicorn to reload when code changes
app = OmniParserServer.app

if __name__ == '__main__':
    print('Starting OmniParser server...')
    OmniParserServer().start(host='localhost', port=8000)
