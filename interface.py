import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import random
import os

# Set page configuration
st.set_page_config(
    page_title="AI Image Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Upload an image and ask questions about it!"}
    ]
if 'current_selection' not in st.session_state:
    st.session_state.current_selection = None
if 'selections' not in st.session_state:
    st.session_state.selections = []
if 'image' not in st.session_state:
    st.session_state.image = None
if 'annotated_image' not in st.session_state:
    st.session_state.annotated_image = None
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 1.0
if 'dragging' not in st.session_state:
    st.session_state.dragging = False
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = None

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .message {
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        font-size: 14px;
        position: relative;
    }
    .system {
        background-color: #f0f2f6;
        width: 80%;
        margin: 0 auto;
        font-style: italic;
        color: #555;
    }
    .user {
        background-color: #0084ff;
        color: white;
        float: right;
        clear: both;
        max-width: 75%;
        border-top-right-radius: 4px;
    }
    .assistant {
        background-color: #f1f1f1;
        float: left;
        clear: both;
        max-width: 75%;
        border-top-left-radius: 4px;
    }
    .clear {
        clear: both;
    }
    .selection-box {
        position: absolute;
        border: 2px solid red;
        background-color: rgba(255, 0, 0, 0.1);
        pointer-events: none;
    }
    .image-container {
        position: relative;
        overflow: hidden;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .zoom-controls {
        margin-top: 10px;
        text-align: center;
    }
    .message-container {
        margin-bottom: 20px;
        overflow-y: auto;
        max-height: 60vh;
    }
</style>
""", unsafe_allow_html=True)

# Mock AI response function - would be replaced with actual AI API call
def get_ai_response(question, selected_area=None, image=None):
    # Mock processing the image and question
    if image is None:
        return "Please upload an image first."
    
    if "analyze" in question.lower() and selected_area:
        # Create and return chart data
        st.session_state.chart_data = pd.DataFrame({
            'Category': ['A', 'B', 'C', 'D', 'E'],
            'Value': [random.randint(50, 500) for _ in range(5)]
        })
        return "Here's an analysis of the selected region. I've created a chart showing the distribution of elements."
    
    elif "identify" in question.lower() and selected_area:
        # Add annotation to the image
        annotate_image(selected_area, "Object of interest")
        return "I've identified the main object in your selection. It appears to be [object description]."
    
    else:
        # Just return text
        return "Based on the image, I can see [description]. For more specific information, try selecting a part of the image and asking about it directly."

def annotate_image(selection, label):
    """Add annotation to the current image based on selection area"""
    if st.session_state.image is None:
        return
    
    # Create a copy of the image for annotation
    img = st.session_state.image.copy()
    draw = ImageDraw.Draw(img)
    
    # Draw rectangle
    draw.rectangle(
        [selection[0], selection[1], selection[2], selection[3]],
        outline="blue",
        width=3
    )
    
    # Add label text
    # This is a simple implementation; a more robust one would use proper font handling
    draw.text((selection[0], selection[1] - 20), label, fill="blue")
    
    # Update the annotated image
    st.session_state.annotated_image = img
    
    # Add selection to saved selections
    if selection not in st.session_state.selections:
        st.session_state.selections.append(selection)

def display_chart():
    """Display a chart based on the analysis of a region"""
    if st.session_state.chart_data is not None:
        fig, ax = plt.subplots(figsize=(10, 5))
        chart_data = st.session_state.chart_data
        bars = ax.bar(chart_data['Category'], chart_data['Value'], color='skyblue')
        
        # Add data labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax.set_title('Analysis of Selected Region')
        ax.set_xlabel('Category')
        ax.set_ylabel('Value')
        
        # Display the chart
        st.pyplot(fig)

def chat_interface():
    """Display the chat interface and handle messages"""
    st.subheader("Chat with AI about the image")
    
    # Display messages
    message_container = st.container()
    with message_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                st.markdown(f'<div class="message system">{content}</div><div class="clear"></div>', unsafe_allow_html=True)
            elif role == "user":
                st.markdown(f'<div class="message user">{content}</div><div class="clear"></div>', unsafe_allow_html=True)
            else:  # assistant
                st.markdown(f'<div class="message assistant">{content}</div><div class="clear"></div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_input", clear_on_submit=True):
        user_input = st.text_input("Ask about the image:", disabled=st.session_state.image is None)
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = get_ai_response(
                user_input, 
                st.session_state.current_selection, 
                st.session_state.image
            )
            
            # Add AI response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to update UI
            st.experimental_rerun()

def main():
    st.title("AI Image Chat")
    
    # Sidebar for upload
    with st.sidebar:
        st.header("Upload Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Load and display the image
            image = Image.open(uploaded_file)
            st.session_state.image = image
            st.session_state.annotated_image = None
            st.session_state.current_selection = None
            st.session_state.selections = []
            st.session_state.chart_data = None
            
            # Reset messages but keep system message
            st.session_state.messages = [
                {"role": "system", "content": "Image uploaded! What would you like to know about it?"}
            ]
            
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = [
                {"role": "system", "content": "Chat cleared. What would you like to know about the image?"}
            ]
            st.rerun()
    
    # Main area
    main_container = st.container()
    
    with main_container:
        # Split into two columns for the main content
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Image viewer section
            if st.session_state.image is not None:
                # Display image with any annotations
                display_image = st.session_state.annotated_image if st.session_state.annotated_image else st.session_state.image
                st.image(display_image, use_column_width=True)
                
                # Zoom controls - in a separate container
                zoom_container = st.container()
                zoom_controls = zoom_container.columns(3)
                
                if zoom_controls[0].button("Zoom In"):
                    st.session_state.zoom_level *= 1.2
                    st.experimental_rerun()
                    
                if zoom_controls[1].button("Reset Zoom"):
                    st.session_state.zoom_level = 1.0
                    st.experimental_rerun()
                    
                if zoom_controls[2].button("Zoom Out"):
                    st.session_state.zoom_level = max(0.5, st.session_state.zoom_level / 1.2)
                    st.experimental_rerun()
                
                # Simple selection interface
                st.write("To select an area, specify coordinates (relative to image dimensions):")
                
                # Create two separate column sets for coordinates
                coord_row1 = st.columns(2)
                coord_row2 = st.columns(2)
                
                img_width, img_height = st.session_state.image.size
                
                x1 = coord_row1[0].number_input("Left (x1)", 0, img_width, int(img_width * 0.25))
                y1 = coord_row1[1].number_input("Top (y1)", 0, img_height, int(img_height * 0.25))
                x2 = coord_row2[0].number_input("Right (x2)", 0, img_width, int(img_width * 0.75))
                y2 = coord_row2[1].number_input("Bottom (y2)", 0, img_height, int(img_height * 0.75))
                
                if st.button("Create Selection"):
                    selection = (x1, y1, x2, y2)
                    st.session_state.current_selection = selection
                    
                    # Add a system message about the selection
                    st.session_state.messages.append({
                        "role": "system", 
                        "content": f"Area selected ({x1},{y1}) to ({x2},{y2}). You can now ask questions about this specific region."
                    })
                    st.experimental_rerun()
                
                # Chart display - in its own section
                if st.session_state.chart_data is not None:
                    st.subheader("Analysis Results")
                    display_chart()
            else:
                st.info("Please upload an image to begin.")
        
        with col2:
            # Chat interface
            chat_interface()
            
            # List of saved selections
            if st.session_state.selections:
                st.subheader("Saved Selections")
                for i, sel in enumerate(st.session_state.selections):
                    st.write(f"Selection {i+1}: ({sel[0]},{sel[1]}) to ({sel[2]},{sel[3]})")

if __name__ == "__main__":
    main()
