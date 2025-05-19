# Manim AI Animation Studio
Manim AI Animation Studio is an innovative web application that empowers users to generate custom mathematical animations using natural language descriptions. By combining the power of Manim, the industry-standard Python animation engine for math visualization, with state-of-the-art large language models (LLMs) accessed via the OpenRouter API, this tool makes high-quality math animation accessible to everyone-no coding required.

# Key Features
- Natural Language to Animation: Users simply describe the animation they want (e.g., “Show a circle morphing into a triangle with labeled sides”), and the app automatically generates the corresponding Manim Python code.

- AI-Powered Code Generation: The app leverages advanced LLMs, such as DeepSeek and Llama 3, to interpret user instructions and produce syntactically correct, Manim-compatible code.

- Automated Rendering: The generated code is executed on the backend using Manim, producing a high-quality MP4 animation.

- Instant Preview and Download: Users can view their animation directly in the browser and download the resulting video for use in presentations, lectures, or social media.

- Customizable Output: Options for rendering quality and animation preview are available, catering to both rapid prototyping and high-resolution export needs.

- Secure and Flexible: The app allows users to securely input their OpenRouter API key and select from multiple LLM models for optimal results.

# Technology Stack
- Frontend: Streamlit (Python)

- Backend: Manim Community Edition (Python)

- AI Integration: OpenRouter API for LLM-powered code generation

- Video Processing: FFmpeg (for rendering and encoding)

# Deployment: Localhost or cloud (Streamlit-compatible environments)

# Use Cases
-Educators can create dynamic math visuals for lectures without writing code.

-Content Creators can generate unique, high-quality animations for YouTube, TikTok, or online courses.

-Students can visualize mathematical concepts and processes for deeper understanding.

-Researchers can quickly prototype and share mathematical ideas visually.

# How It Works
- Describe Your Animation: Enter a plain-English description of the animation you want.

- AI Generates the Code: The LLM interprets your request and writes valid Manim code.

- Automatic Rendering: The app runs the code with Manim and produces a video.

- View & Download: Instantly preview your animation and download the MP4 file.

# Why Manim AI Animation Studio?
- No Coding Required: Democratizes access to mathematical animation.

- AI-Driven: Harnesses the latest LLMs for accurate and creative code generation.

- Professional Output: Produces publication-quality animations suitable for any platform.

- Customizable and Extensible: Built for educators, creators, and learners alike.
