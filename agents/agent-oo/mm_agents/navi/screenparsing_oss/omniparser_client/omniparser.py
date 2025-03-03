from pprint import pprint
from typing import Dict, List
from .client import OmniparserClient
from PIL import Image
import numpy as np

class Omniparser:
    def __init__(self):
        self.client = OmniparserClient()

    def caption_ents(self, image: Image, ents: List[Dict]):

        # LK_TODO: Add logic for parsing A11y text !!!!!

        for ent in ents:
            pprint(ent)
        

            
        # print("OMNIPARSER - CAPTION_ENTS")
        # print(parsed_content_icon)

        # return parsed_content_icon
        return [] 


    def propose_ents(self, image: Image, with_captions: bool = True) -> List[Dict]:
        """
        Uses the Omniparser client to analyze the image and generate entities.
        The returned list of entities has the same structure as in the original code.
        Since the Omniparser client does not return bounding boxes, each entity is 
        assigned a bounding box that covers the entire image.
        """
        # Use the Omniparser client to analyze the image
        result = self.client.analyze_image(image)

        # print("OMNIPARSER - ANALYZE_IMAGE")
        # print(result["parsed_content_list"])

        return result["parsed_content_list"]
        
        # If the client returns a parsed image file, load it.
        # parsed_image_path = result.get("parsed_image_path")
        # if parsed_image_path:
        #     try:
        #         parsed_image = Image.open(parsed_image_path)
        #     except Exception:
        #         parsed_image = image
        # else:
        #     parsed_image = image

        # width, height = image.size
        # Create one entity per caption returned by the client.
        # Here we assume that all detected entities are text.
        # ents = []
        # for caption in result.get("parsed_content_list", []):
        #     ents.append({
        #         'from': 'omniparser',
        #         'shape': {'x': 0, 'y': 0, 'width': width, 'height': height},
        #         'text': caption if with_captions else '',
        #         'type': 'text'
        #     })
        
        # LK_TODO: IS NOT NEEDED ANYMORE ????
        # If additional captioning is needed (for example if some entities lack text),
        # the caption_ents method can be invoked to update them.
        # if with_captions:
        #     self.caption_ents(image, ents)
        
        # Ensure that the shape values are integers
        # result = [
        #     {
        #         **ent,
        #         "shape": {
        #             "x": int(ent["shape"]["x"]),
        #             "y": int(ent["shape"]["y"]),
        #             "width": int(ent["shape"]["width"]),
        #             "height": int(ent["shape"]["height"])
        #         }
        #     }
        #     for ent in ents
        # ]
        
        # print("OMNIPARSER - PROPOSE_ENTS")
        # print(result)

        # return ents
