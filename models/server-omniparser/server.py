import click
import time

from fastapi import FastAPI
from pydantic import BaseModel
from os import path
from typing import TypedDict

from util.omniparser import Omniparser

root_dir = path.join(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


class Config(TypedDict):
    som_model_path: str
    caption_model_name: str
    caption_model_path: str
    device: str
    BOX_TRESHOLD: float


class ParseRequest(BaseModel):
    base64_image: str


config: Config = {
    'som_model_path': path.join(root_dir, 'models/vision/omniparser/icon_detect/model.pt'),
    'caption_model_name': 'florence2',
    'caption_model_path': path.join(root_dir, 'models/vision/omniparser/icon_caption_florence'),
    'device': 'cpu',
    'BOX_TRESHOLD': 0.05,
}

if config:
    config.update(config)

omniparser = Omniparser(config)

app = FastAPI()


@app.post('/parse')
async def parse(parse_request: ParseRequest):
    print('start parsing...')
    start = time.time()
    dino_labled_img, parsed_content_list = omniparser.parse(parse_request.base64_image)
    latency = time.time() - start
    print('time:', latency)
    return {
        'som_image_base64': dino_labled_img,
        'parsed_content_list': parsed_content_list,
        'latency': latency,
    }


@app.get('/probe')
async def probe():
    return {'message': 'Omniparser API ready'}

@click.command()
@click.option('--host', default='localhost', help='Host to run the server on.')
@click.option('--port', default=8000, help='Port to run the server on.')
def main(host: str, port: int):
    """Run the FastAPI server."""
    import uvicorn
    uvicorn.run("server:app", host=host, port=port, reload=True)

if __name__ == '__main__':
    main()
    