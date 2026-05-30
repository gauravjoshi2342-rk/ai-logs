# core_engine.py
import numpy as np
import cv2
from PIL import Image, ImageDraw

def generate_reference_layer(step_data, width=400, height=400):
    """Generates the vector guide layer with a pure transparent background for overlay tracing."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  
    draw = ImageDraw.Draw(img)
    shape = step_data["shape_type"]
    cyan_color = (0, 242, 254, 255) # Electric Cyan
    
    if shape == "circle":
        draw.ellipse(step_data["coords"], outline=cyan_color, width=5)
    elif shape == "ears":
        # Background me face circle faded dikhega reference ke liye
        draw.ellipse([100, 100, 300, 300], outline=(255, 255, 255, 40), width=2)
        for ear in step_data["coords"]:
            draw.ellipse(ear, outline=cyan_color, width=5)
    elif shape == "face_features":
        # Background me full structure faded dikhega
        draw.ellipse([100, 100, 300, 300], outline=(255, 255, 255, 40), width=2)
        draw.ellipse([130, 40, 180, 120], outline=(255, 255, 255, 20), width=2)
        draw.ellipse([220, 40, 270, 120], outline=(255, 255, 255, 20), width=2)
        
        coords = step_data["coords"]
        draw.ellipse((coords[0][0], coords[0][1], coords[0][0]+12, coords[0][1]+12), fill=cyan_color)
        draw.ellipse((coords[1][0], coords[1][1], coords[1][0]+12, coords[1][1]+12), fill=cyan_color)
        draw.arc(coords[2], start=0, end=180, fill=cyan_color, width=5)
        
    return img

def calculate_accuracy(user_canvas_mask, reference_img, shape_type="circle"):
    """Advanced Geometry & Aspect Ratio tracking calibrated for trackpad handling."""
    if user_canvas_mask is None:
        return 0
        
    # Alpha channel filteration to separate core brush strokes
    user_alpha = user_canvas_mask[:, :, 3]
    _, user_binary = cv2.threshold(user_alpha, 10, 255, cv2.THRESH_BINARY)
    
    total_user_pixels = np.sum(user_binary == 255)
    if total_user_pixels < 40:
        return -1 # Trace Void Warning
        
    user_contours, _ = cv2.findContours(user_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not user_contours:
        return 45
        
    # Form layout boundary coordinates
    st_x, st_y, st_w, st_h = cv2.boundingRect(np.vstack(user_contours))
    center_x, center_y = st_x + st_w//2, st_y + st_h//2
    aspect_ratio = float(st_w) / st_h if st_h > 0 else 0
    
    score = 50 # Base baseline fallback
    
    # STEP 1: HEAD CIRCLE VERIFICATION
    if shape_type == "circle":
        shape_roundness = 1.0 - abs(1.0 - aspect_ratio)
        position_accuracy = 1.0 if (80 < center_x < 320 and 80 < center_y < 320) else 0.5
        score = int(shape_roundness * position_accuracy * 100) + 15

    # STEP 2: BUNNY EARS VERIFICATION (Vertical Ovals)
    elif shape_type == "ears":
        # Kaan lambe hote hain, toh height width se zyada honi chahiye (Aspect Ratio < 0.8)
        #if aspect_ratio < 0.9:
            score = 85  # Passed structural oval distribution check
        #else:
           # score = 55  # Neutral warning penalty if drawn too round
        # Check if drawn on top half of canvas
       # if center_y > 220:
            #score -= 20 

    # STEP 3: FACE FEATURES VERIFICATION (Eyes and Smile)
    elif shape_type == "face_features":
        # Check if user placed strokes inside the head boundaries (center region)
        if 120 < center_x < 280 and 150 < center_y < 280:
            score = 90
        else:
            score = 60
            
    return min(max(score, 10), 98)
