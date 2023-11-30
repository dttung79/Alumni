import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

# Function to detect the largest rectangle in the image, which is assumed to be the grey frame
def detect_grey_frame(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    return x, y, w, h
    
    

# Function to detect face using Haar Cascades
def detect_face(image, margin_percentage=0.2):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        x, y, w, h = faces[0]  # Get the coordinates of the first face
        margin = int(max(w, h) * margin_percentage)  # Calculate the margin based on the face size
        x -= margin
        y -= margin
        w += 2 * margin
        h += 2 * margin
        return x, y, w, h
    else:
        return None

def create_invitation(portrait, name):
    # Load the images using OpenCV
    invitation_img = cv2.imread('static/invite.png')
    portrait_img = cv2.imread(portrait)

    # Detect the grey frame on the invitation
    frame_x, frame_y, frame_w, frame_h = detect_grey_frame(invitation_img)

    # Detect the face in the portrait
    face = detect_face(portrait_img)
    if face is None:
        raise Exception("No face detected in the portrait image.")

    # Extract face coordinates
    face_x, face_y, face_w, face_h = face

    # Crop the face from the portrait with some margin
    margin = int(max(face_w, face_h) * 0.2)  # 20% margin
    face_cropped = portrait_img[face_y-margin:face_y+face_h+margin, face_x-margin:face_x+face_w+margin]

    # Resize cropped face to fit the grey frame on the invitation
    face_resized = cv2.resize(face_cropped, (frame_w, frame_h))

    # Place the resized face into the grey frame area of the invitation
    invitation_with_face = invitation_img.copy()
    invitation_with_face[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = face_resized

    # Add the name to the invitation
    invitation_with_face_pil = Image.fromarray(cv2.cvtColor(invitation_with_face, cv2.COLOR_BGR2RGB))
    font_path = 'static/taviraj.ttf'
    font_size = 150  # chosen size for the font
    font = ImageFont.truetype(font_path, font_size)

    # Initialize ImageDraw
    draw = ImageDraw.Draw(invitation_with_face_pil)

    # Add text to the invitation
    #text = "Welcome to the event!"
    frame_center_x = frame_x + frame_w // 2 - 100
    frame_bottom_y = frame_y + frame_h
    text_width, text_height = draw.textsize(name, font=font)
    text_x = frame_center_x - text_width // 2
    text_y = frame_bottom_y + 280  # Place the text below the grey frame
    text_position = (text_x, text_y)
    text_color = (255, 255, 255)  # White color for the text

    # Draw the text onto the invitation
    draw.text(text_position, name.upper(), font=font, fill=text_color)
    # Convert the modified image back to a PIL Image to save as PNG
    #final_image = Image.fromarray(cv2.cvtColor(np.array(invitation_with_face_pil), cv2.COLOR_RGB2BGR))
    final_image = invitation_with_face_pil
    final_image_path = 'static/invite/' + portrait.split('/')[-1]
    final_image.save(final_image_path)

    return final_image_path

