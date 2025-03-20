import asyncio
import os
from clients.som import omniparser
from PIL import Image
import json

async def test_omniparser():
    current_dir = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_dir, 'img/test_desktop.png'))

    response = omniparser.analyze_image(img)

    # Get parsed image and content
    parsed_image = response["parsed_image"]
    parsed_content_list = response["parsed_content_list"]

    # Save the parsed image and content to files
    os.makedirs(os.path.join(current_dir, 'out'), exist_ok=True)
    parsed_image.save(os.path.join(current_dir, 'out/test_desktop_parsed.png'))
    with open(os.path.join(current_dir, 'out/test_desktop_parsed.json'), 'w') as f:
        f.write(json.dumps(parsed_content_list, indent=4))

if __name__ == "__main__":
    print("-" * 20)
    print("Testing Omniparser server ...")
    asyncio.run(test_omniparser())

    print("-" * 20)
    print("Testing completed.")