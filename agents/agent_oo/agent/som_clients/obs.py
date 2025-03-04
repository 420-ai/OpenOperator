from typing import List
from agent.som_clients.som import draw_som, filter_entities, add_labels

def create_text_list(entities: List[dict], width, height)-> str:
        list_of_text = "ID | Type | Text content or description | Normalized location [x1, y1, x2, y2]\n"
        # create a list of all the elements in the form
        # ID | Type | Text | Normalized location (x1, y1, x2, y2)
        for ent in entities:
            region_id = ent["label"]
            region_type = ent["type"]
            shape = ent["shape"]
            location = [round(shape["x"]/width, 2), round(shape["y"]/height, 2), round((shape["x"]+shape["width"])/width, 2), round((shape["y"]+shape["height"])/height, 2)]
            # check if the key exists
            if "text" in ent.keys():
                list_of_text += f"{region_id} | {region_type} | {ent['text']} | {location}\n"
            else:
                list_of_text += f"{region_id} | {region_type} | {'-'} | {location}\n"
        return list_of_text


def parser_to_prompt(screen, entities, color_mapping_debug=None, color_mapping_prompt=None):
    """Convert screen parser output to image + text prompt."""
    add_labels(entities, template='{i}', shuffle=False)
    vis_entities = filter_entities(entities)
    
    image_som_full = draw_som(screen, vis_entities, color_mapping=color_mapping_debug)
    image_som_notext = draw_som(screen, vis_entities, color_mapping=color_mapping_prompt)
    text = create_text_list(vis_entities, screen.width, screen.height)
    return image_som_full, image_som_notext, text
