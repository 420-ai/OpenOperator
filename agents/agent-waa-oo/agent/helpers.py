
def remove_min_leading_spaces(text):  
    lines = text.split('\n')  
    min_spaces = min(len(line) - len(line.lstrip(' ')) for line in lines if line)  
    return '\n'.join([line[min_spaces:] for line in lines])  

def prev_actions_to_string(prev_actions, n_prev=3):  
    result = ""  
    n_prev = min(n_prev, len(prev_actions))  # Limit n_prev to the length of the array  
    for i in range(1, n_prev + 1):  
        action = prev_actions[-i]  # Get the element at index -i (from the end)  
        result += f"Screen is currently at time step T. Below is the action executed at time step T-{i}: \n{action}\n\n"  
    return result  

def resize_image_openai(image):
    """
    Resize the image to OpenAI's input resolution so that text written on it doesn't get processed any further.
    
    Steps:
    1. If the image's largest side is greater than 2048, scale it down so that the largest side is 2048, maintaining aspect ratio.
    2. If the shortest side of the image is longer than 768px, scale it so that the shortest side is 768px.
    3. Return the resized image.
    
    Reference: https://platform.openai.com/docs/guides/vision/calculating-costs
    """
    max_size = 2048
    target_short_side = 768
    
    out_w, out_h = image.size

    # Step 0: return the image without scaling if it's already within the target resolution
    if out_w <= max_size and out_h <= max_size and min(out_w, out_h) <= target_short_side:
        return image, out_w, out_h, 1.0
    
    # Initialize scale_factor
    scale_factor = 1.0
    
    # Step 1: Calculate new size to fit within a 2048 x 2048 square
    max_dim = max(out_w, out_h)
    if max_dim > max_size:
        scale_factor = max_size / max_dim
        out_w = int(out_w * scale_factor)
        out_h = int(out_h * scale_factor)
    
    # Step 2: Calculate new size if the shortest side is longer than 768px
    min_dim = min(out_w, out_h)
    if min_dim > target_short_side:
        new_scale_factor  = target_short_side / min_dim
        out_w = int(out_w * new_scale_factor)
        out_h = int(out_h * new_scale_factor)
        # Combine scale factors from both steps
        scale_factor *= new_scale_factor
    
    # Perform the resize operation once
    resized_image = image.resize((out_w, out_h))
    
    return resized_image, out_w, out_h, scale_factor
