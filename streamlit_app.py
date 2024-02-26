"""
Created on Sun Feb 25 11:26:27 2024

@author: Zach
"""

import streamlit as st
from PIL import Image
import os
import base64
from io import BytesIO
import random
from streamlit_image_select import image_select
from streamlit_extras.buy_me_a_coffee import button
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Directory where noggle designs (.png) are stored
NOGGLES_DIR = "noggles"
DEFAULT_IMAGE_PATH = "C:\\Users\\Zach\\Downloads\\a43aef78-9580-441f-8a76-ec48900cd581.png"

available_filters = [
    "Black and White", "Sepia", "Blur", "Edge Enhance",
    "Brightness Adjust", "Contrast Adjust", "Posterize", "Solarize", "Pixelate"
]

def resize_image(image, size=(32, 32)):
    """Resize the image to 32x32 pixels."""
    img = image.convert("RGBA")
    img = img.resize(size, Image.NEAREST)  # Resize with NEAREST to keep it pixelated
    return img
# Define your filter functions here
def apply_black_and_white(image):
    return image.convert('L').convert('RGBA')

def apply_sepia(image):
    sepia_image = ImageEnhance.Color(image).enhance(0.3)
    return sepia_image

def apply_blur(image):
    return image.filter(ImageFilter.BLUR)

def apply_edge_enhance(image):
    return image.filter(ImageFilter.EDGE_ENHANCE)

def apply_brightness(image, level):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(level)

def apply_contrast(image, level):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(level)

def apply_posterize(image, bits=2):
    """Apply a posterize effect, reducing the number of bits for each color channel."""
    if image.mode == 'RGBA':
        # Separate the alpha channel
        r, g, b, a = image.split()
        # Convert the RGB components to 'RGB' mode for posterization
        rgb_image = Image.merge('RGB', (r, g, b))
        # Apply the posterize effect to the RGB channels
        rgb_image = ImageOps.posterize(rgb_image, bits)
        # Merge the posterized RGB channels with the alpha channel
        image = Image.merge('RGBA', (rgb_image.split() + (a,)))
    else:
        # Apply the posterize effect to non-RGBA images
        image = ImageOps.posterize(image, bits)
    return image

def apply_solarize(image, threshold=128):
    if image.mode == 'RGBA':
        rgb, a = image.split()[0:3], image.split()[3]
        rgb_image = Image.merge('RGB', rgb)
        rgb_image = ImageOps.solarize(rgb_image, threshold)
        image = Image.merge('RGBA', (*rgb_image.split(), a))
    else:
        image = ImageOps.solarize(image, threshold)
    return image

def apply_pixelate(image, pixel_size=2):
    # Ensure pixel_size does not exceed image dimensions
    pixel_size = min(pixel_size, image.width, image.height)
    small_image = image.resize(
        (image.width // pixel_size, image.height // pixel_size), Image.NEAREST
    )
    return small_image.resize(
        (image.width, image.height), Image.NEAREST
    )
# Function to apply filters based on the selected filter list
def apply_selected_filters(image):
    if 'filter_list' in st.session_state:
        for filter_name in st.session_state.filter_list:
            if filter_name == "Black and White":
                image = apply_black_and_white(image)
            elif filter_name == "Sepia":
                image = apply_sepia(image)
            elif filter_name == "Blur":
                image = apply_blur(image)
            elif filter_name == "Edge Enhance":
                image = apply_edge_enhance(image)
            elif filter_name == "Brightness Adjust":
                # Example: adjust level based on additional user input, or set a default
                image = apply_brightness(image, 1.5)
            elif filter_name == "Contrast Adjust":
                # Same as above for contrast adjustment
                image = apply_contrast(image, 1.5)
            elif filter_name == "Posterize":
                image = apply_posterize(image)
            elif filter_name == "Solarize":
                image = apply_solarize(image)
            elif filter_name == "Pixelate":
                image = apply_pixelate(image)
    return image

# Function to move an item in a list
def move_item(lst, item, direction):
    index = lst.index(item)
    if direction == "up" and index > 0:
        lst[index], lst[index - 1] = lst[index - 1], lst[index]
    elif direction == "down" and index < len(lst) - 1:
        lst[index], lst[index + 1] = lst[index + 1], lst[index]
    return lst

# MAIN Functions 
def list_noggles(directory=NOGGLES_DIR):
    """List all noggle designs available in the specified directory with full paths."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.png')]

def display_noggles_as_clickable_grid():
    with st.sidebar:
        with st.expander("Choose your Noggles", expanded=False):
            #"""Display noggles as a grid of clickable images for selection."""
            noggles = list_noggles()  # This should return the full paths to the noggle images
            
            # Use the image_select component with the correct arguments
            selected_noggle = image_select("", noggles)
            
            # Display the selected noggle
            if selected_noggle:
                st.session_state.selected_noggle_path = selected_noggle
               # st.write(f"You selected: {selected_noggle}")
        st.header("Filter Selection")
        # Filter selection and management
        # Filter selection and management
        filter_options = [
            "None", "Black and White", "Sepia", "Blur", "Edge Enhance",
            "Brightness Adjust", "Contrast Adjust", "Posterize", "Solarize", "Pixelate"
        ]

        if 'selected_filter_index' not in st.session_state:
            st.session_state.selected_filter_index = 0

        selected_filter = st.selectbox(
            "Add a filter:", filter_options, index=st.session_state.selected_filter_index, key="filter_select"
        )

        if st.button("Add Filter") and selected_filter != "None":
            if 'filter_list' not in st.session_state:
                st.session_state.filter_list = []
            if selected_filter not in st.session_state.filter_list:
                st.session_state.filter_list.append(selected_filter)
            st.session_state.selected_filter_index = 0
            st.experimental_rerun()

        if 'filter_list' in st.session_state:
            for idx, filter_name in enumerate(st.session_state.filter_list):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(filter_name)
                with col2:
                    if st.button("❌", key=f"delete-{idx}"):
                        st.session_state.filter_list.pop(idx)
                        st.experimental_rerun()

        if st.button("Clear Filters"):
            st.session_state.filter_list = []
            st.experimental_rerun()
            
def convert_png_to_svg(image):
    """Convert a 32x32 PNG image to SVG format."""
    svg_elements = []
    for y in range(32):
        for x in range(32):
            r, g, b, a = image.getpixel((x, y))
            if a != 0:  # Skip fully transparent pixels
                color = f'#{r:02x}{g:02x}{b:02x}'
                svg_elements.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{color}"/>')
    return ''.join(svg_elements)

def generate_svg(pixel_art_svg, svg_width=32, svg_height=32, scale_factor=1):
    """Generate an SVG with given width and height, scaled by scale_factor for display."""
    scaled_width = svg_width * scale_factor
    scaled_height = svg_height * scale_factor
    return f'<svg width="{scaled_width}px" height="{scaled_height}px" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">{pixel_art_svg}</svg>'

def display_svg(svg_content):
    """Display SVG content in Streamlit."""
    st.markdown(f'<div style="width: 100%; display: flex; justify-content: center;">{svg_content}</div>', unsafe_allow_html=True)

def generate_downloadable_svg(svg_content):
    """Create a download button for the SVG content."""
    b64 = base64.b64encode(svg_content.encode()).decode()
    href = f'<a href="data:image/svg+xml;base64,{b64}" download="pixel_art_nft.svg">Download SVG</a>'
    st.markdown(href, unsafe_allow_html=True)

def create_image_grid(image, scale_factor):
    """Scale up an image by a scale factor using nearest neighbor (to keep the pixelated look)."""
    image = image.resize((image.width * scale_factor, image.height * scale_factor), Image.NEAREST)
    return image
# Function to allow downloading the processed image
def download_image(image):
    # Convert PIL Image to bytes for download
    img_bytes = BytesIO()
    format = st.selectbox("Select download format:", ["PNG", "WEBP"])
    filename = "processed_image." + format.lower()
    image.save(img_bytes, format=format)
    st.download_button(label="Download Image",
                       data=img_bytes.getvalue(),
                       file_name=filename,
                       mime=f"image/{format.lower()}")
    
def display_image_with_noggles(uploaded_file=None):
    """Display the default or uploaded image with an applied noggle."""
    # Load the default image or the uploaded image from session state
    if st.session_state.uploaded_image is not None:
        image = Image.open(st.session_state.uploaded_image).convert("RGBA")
    else:
        image = Image.open(DEFAULT_IMAGE_PATH).convert("RGBA")

    # Resize the image to 32x32
    image = resize_image(image)
    
    # Apply the selected filters sequentially
    image = apply_selected_filters(image)
    
    # If a noggle has been selected, overlay it on the image
    if 'selected_noggle_path' in st.session_state and st.session_state.selected_noggle_path:
        noggle_path = st.session_state.selected_noggle_path
        noggle_image = Image.open(noggle_path).convert("RGBA").resize((32, 32), Image.NEAREST)
        image.paste(noggle_image, (0, 0), noggle_image)


    

    # Convert the processed image to SVG for download (actual size)
    pixel_art_svg_download = convert_png_to_svg(image)
    final_svg_download = generate_svg(pixel_art_svg_download)

    # Convert the processed image to scaled SVG for display (scaled up)
    scale_factor = 20  # Scale factor for display
    pixel_art_svg_display = convert_png_to_svg(image)
    final_svg_display = generate_svg(pixel_art_svg_display, scale_factor=scale_factor)

    # Display the scaled SVG in the app
    display_svg(final_svg_display)

    # Provide a link to download the actual size SVG
    generate_downloadable_svg(final_svg_download)
    
    download_image(final_svg_display)
    


# Use this function where appropriate in your main function
# For example, right before displaying the image with noggles applied

def example():
    button(username="zamy00t", floating=False, width=221)



def main():
    
    
    st.title("VRBBuilder")

    # Ensure the noggle path is initialized in session state
    if 'selected_noggle_path' not in st.session_state:
        noggles = list_noggles()
        st.session_state.selected_noggle_path = random.choice(noggles) if noggles else None

    # Initialize session states for filter list and uploaded image if not present
    if 'filter_list' not in st.session_state:
        st.session_state.filter_list = []
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    # Display the noggles selection grid
    display_noggles_as_clickable_grid()

    # File uploader for the image
    uploaded_file = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"])
    
    # Update session state for uploaded image when a new file is uploaded
    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file

    # Display the image with the noggle applied
    display_image_with_noggles(uploaded_file)

    example()



if __name__ == "__main__":
    main()

