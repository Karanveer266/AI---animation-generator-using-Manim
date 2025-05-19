import streamlit as st
import requests
import json
import subprocess
import os
import tempfile
import base64
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Manim Video Generator",
    page_icon="🎬",
    layout="wide"
)

# App title and description
st.title("🎬 Manim Video Generator")
st.markdown("""
This app generates mathematical animations using Manim based on your text descriptions.
Simply describe the animation you want, and the AI will generate the code and create the video.
""")

# Function to call OpenRouter API with improved prompt
def generate_manim_code(description, api_key):
    prompt = f"""
You are an expert in creating animations with Manim, the Mathematical Animation Engine.
A user has requested the following animation:

"{description}"

Please write complete, executable Manim code that creates this animation.
The code should:
1. Import ONLY from the standard manim library (from manim import *)
2. Define a Scene class named ManimScene
3. Implement the construct method with appropriate animations
4. Be ready to run with the Manim CLI
5. Include helpful comments explaining the code
6. Be optimized for quality and visual appeal
7. ONLY use standard Manim features and built-in classes
8. Be complete and self-contained

IMPORTANT COMPATIBILITY NOTES:
- Do not use operand type(s) for *: 'method' and 'float'
- DO NOT import any external libraries or dependencies beyond the standard manim package
- Use ONLY these text classes: Text, Tex, or MathTex (NOT TextField, TextMobject, or TexMobject)
- To animate text, use self.play(Write(text_object)) instead of animate=True parameter
- Always include self.wait(1) at the end of your animations
- Position text with next_to() method, e.g., text.next_to(circle, DOWN)
- Always use standard Manim colors like RED, GREEN, BLUE, YELLOW, etc.
- For any object creation, use self.play(Create(object)) not ShowCreation
- Ensure all animations are properly sequenced with self.play() calls
- DO NOT use side_length with Triangle() - instead use Triangle().scale(size)
- For polygons, use scale() method to adjust size rather than constructor parameters
- Avoid using x_min, x_max parameters - use x_range instead for axes
- When transforming between shapes, ensure they are compatible types
- For 3D objects, always import ThreeDScene and use it as the base class
- Always end your animation with at least one self.wait() call
- DO NOT use any custom classes or functions not included in the standard manim package

Return ONLY the Python code without any explanations or markdown formatting.
"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",    #change this code according to your API 
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",               
            "HTTP-Referer": "https://manimgenerator.app",
            "X-Title": "Manim Video Generator",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-r1-distill-llama-70b:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Clean up the code by removing markdown formatting
        if "```" in content:
            # Find code between markdown code blocks
            start_marker = "```python"
            if start_marker in content:
                start_idx = content.find(start_marker) + len(start_marker)
            else:
                start_marker = "```"
                start_idx = content.find(start_marker) + len(start_marker)
            
            end_idx = content.rfind("```")
            
            if end_idx > start_idx:
                content = content[start_idx:end_idx].strip()
        
        return content
    else:
        st.error(f"Error from API: {response.status_code}")
        st.error(response.text)
        return None

# Function to run Manim code and get video path
def run_manim_code(code):
    # Create a temporary directory for the code and output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the code file
        code_file = Path(temp_dir) / "manim_scene.py"
        with open(code_file, "w") as f:
            f.write(code)
        
        # Run Manim command to generate video
        try:
            # -pql = preview, quality low (for faster rendering)
            cmd = ["manim", "-pql", str(code_file), "ManimScene"]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=temp_dir
            )
            
            if result.returncode != 0:
                st.error("Error running Manim:")
                st.code(result.stderr)
                
                # Try to extract the actual class name from the code if ManimScene fails
                import re
                class_match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)", code)
                if class_match:
                    actual_class = class_match.group(1)
                    st.info(f"Trying with detected class name: {actual_class}")
                    cmd = ["manim", "-pql", str(code_file), actual_class]
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True,
                        cwd=temp_dir
                    )
                    if result.returncode != 0:
                        st.error(f"Still failed with class {actual_class}:")
                        st.code(result.stderr)
                        return None
                else:
                    return None
            
            # Find the generated video file - search in different possible paths
            possible_paths = [
                Path(temp_dir) / "media" / "videos" / "manim_scene" / "480p15",
                Path(temp_dir) / "media" / "videos" / "manim_scene" / "1080p60",
                Path(temp_dir) / "media" / "videos" / Path(code_file.stem) / "480p15",
            ]
            
            video_file = None
            for path in possible_paths:
                if path.exists():
                    video_files = list(path.glob("*.mp4"))
                    if video_files:
                        video_file = video_files[0]
                        break
            
            if not video_file:
                st.error("No video file was generated")
                return None
                
            # Copy the video to a location outside the temp directory
            output_dir = Path("./output")
            st.info(f"Saving to: {output_dir.absolute()}")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / "generated_video.mp4"
            
            with open(video_file, "rb") as src_file:
                with open(output_file, "wb") as dst_file:
                    dst_file.write(src_file.read())
                    
            return str(output_file)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

# Function to display video
def display_video(video_path):
    if video_path and os.path.exists(video_path):
        # Read video file
        with open(video_path, "rb") as file:
            video_bytes = file.read()
        
        # Display video
        st.video(video_bytes)
        
        # Provide download button
        st.download_button(
            label="Download Video",
            data=video_bytes,
            file_name="manim_animation.mp4",
            mime="video/mp4"
        )
    else:
        st.error("Video file not found")

# Sidebar for API key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("OpenRouter API Key", 
                           value="" , #include your API key here . 
                           type="password")
    
    # Model selection
    st.subheader("Model Selection")
    model = st.selectbox(
        "Select AI Model",
        ["deepseek/deepseek-r1-distill-llama-70b:free", 
         "meta-llama/llama-3.3-8b-instruct:free",
         "anthropic/claude-3-opus:beta"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app uses:
    - Streamlit for the web interface
    - OpenRouter API to access LLMs
    - Manim for mathematical animations
    """)
    
    # FFmpeg installation info
    st.markdown("### FFmpeg Installation")
    st.markdown("""
    If you see FFmpeg warnings:
    1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
    2. Add to your system PATH
    3. Restart the app
    """)

# Main app interface
description = st.text_area(
    "Describe the mathematical animation you want to create:",
    height=150,
    placeholder="Example: Create an animation showing a circle transforming into a square, then into a triangle, with appropriate mathematical formulas appearing next to each shape."
)

# Advanced options collapsible section
with st.expander("Advanced Options"):
    quality_options = {
        "Low (faster)": "-ql",
        "Medium": "-qm",
        "High (slower)": "-qh"
    }
    quality = st.selectbox("Rendering Quality", options=list(quality_options.keys()), index=0)
    
    preview = st.checkbox("Preview while rendering", value=True)
    
    manim_flags = quality_options[quality]
    if preview:
        manim_flags = "-p" + manim_flags[1:]

# Generate button
generate_button = st.button("Generate Animation", type="primary")
if generate_button:
    if not description:
        st.warning("Please enter a description of the animation you want to create.")
    elif not api_key:
        st.warning("Please enter your OpenRouter API key.")
    else:
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Generate Manim code
        status_text.text("Generating Manim code from your description...")
        code = generate_manim_code(description, api_key)
        progress_bar.progress(33)
        
        if code:
            # Display the generated code
            with st.expander("Generated Manim Code", expanded=True):
                st.code(code, language="python")
            
            # Step 2: Run the code to generate video
            status_text.text("Rendering animation with Manim (this may take a while)...")
            video_path = run_manim_code(code)
            progress_bar.progress(66)
            
            # Step 3: Display the video
            if video_path:
                status_text.text("Animation complete!")
                progress_bar.progress(100)
                
                st.subheader("Your Generated Animation")
                display_video(video_path)
            else:
                status_text.text("Failed to generate video.")
                progress_bar.progress(100)
        else:
            status_text.text("Failed to generate Manim code.")
            progress_bar.progress(100)

# Sample gallery
st.markdown("---")
st.header("Example Descriptions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Basic Shapes Animation**
    ```
    Create an animation showing a circle that transforms into a square, then into a triangle. Include labels for each shape.
    ```
    """)
    
    st.markdown("""
    **Function Graphing**
    ```
    Plot the function f(x) = sin(x) being drawn from left to right, then show its derivative appearing below it in a different color.
    ```
    """)

with col2:
    st.markdown("""
    **3D Rotation**
    ```
    Create a 3D cube that rotates around all three axes. Then show it transforming into a sphere.
    ```
    """)
    
    st.markdown("""
    **Calculus Concept**
    ```
    Visualize the concept of a Riemann sum approximating the area under a curve, with rectangles that gradually get thinner.
    ```
    """)
