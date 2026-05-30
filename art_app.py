# art_app.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import base64
from io import BytesIO
from lessons_data import LESSONS
from core_engine import generate_reference_layer, calculate_accuracy

st.set_page_config(page_title="ArtWorkout AI Pro", layout="wide", initial_sidebar_state="expanded")

# Robust CSS Stack Mechanism to overlay canvas perfectly on top of template
st.markdown("""
    <style>
    .main { background-color: #0B0F19; color: #E2E8F0; }
    div[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00F2FE, #4FACFE); }
    .metric-card { background: #1F2937; padding: 15px; border-radius: 12px; border: 1px solid #374151; text-align: center; }
    
    /* Strict CSS Layering System for Absolute Overlay Tracing */
    .canvas-stack-container {
        position: relative;
        width: 400px;
        height: 400px;
        background-color: #1F2937;
        border-radius: 8px;
    }
    .template-underlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 400px;
        height: 400px;
        z-index: 1;
        pointer-events: none;
    }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = 0
if "current_score" not in st.session_state: st.session_state.current_score = None
if "streak" not in st.session_state: st.session_state.streak = 4

with st.sidebar:
    st.title("ArtWorkout AI")
    st.caption("Next-Gen Art Pedagogy Platform")
    st.markdown("---")
    st.markdown(f"<div class='metric-card'><h4>Daily Streak</h4><h2>{st.session_state.streak} Days</h2><p style='color:#00F2FE;'>+150 XP pending</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    lesson_titles = [lesson["title"] for lesson in LESSONS]
    selected_title = st.selectbox("Select Active Curriculum:", lesson_titles)
    active_lesson = next(l for l in LESSONS if l["title"] == selected_title)

st.title(f"Active Canvas: {active_lesson['title']}")
st.markdown(f"**Domain:** {active_lesson['category']} | **Difficulty Level:** `{active_lesson['level']}`")

current_step_idx = st.session_state.step
step_data = active_lesson["steps"][current_step_idx]
total_steps = len(active_lesson["steps"])

progress_percent = (current_step_idx + 1) / total_steps
st.progress(progress_percent)
st.subheader(f"Instruction: Step {current_step_idx + 1} - {step_data['instruction']}")

# Generate transparent guide line image
bg_layer = generate_reference_layer(step_data)

# Convert PIL Image to Base64 to safely embed into HTML background layer
buffered = BytesIO()
bg_layer.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

col_canvas, col_analytics = st.columns([1.3, 1])

with col_canvas:
    st.markdown("### Interactive Tracing Board")
    st.markdown("Trace directly over the cyan guidelines visible inside the board:")
    
    # Injecting the background template image explicitly using an absolute CSS container wrapper
    st.markdown(f"""
        <div class="canvas-stack-container">
            <img class="template-underlay" src="data:image/png;base64,{img_base64}" />
        </div>
    """, unsafe_allow_html=True)
    
    # Standalone drawing component with zero native backgrounds to capture pure user stroke matrices
    user_canvas = st_canvas(
        fill_color="rgba(0, 0, 0, 0.0)",
        stroke_width=5,
        stroke_color="#00F2FE",
        background_color="rgba(0,0,0,0)", # Keeps canvas overlay see-through
        background_image=None,  
        height=400,
        width=400,
        drawing_mode="freedraw",
        key=f"canvas_layer_s{current_step_idx}"
    )

with col_analytics:
    st.markdown("### AI Performance Monitor")
    st.markdown("Click below to evaluate tracing accuracy vectors.")
    
    if st.button("Evaluate Stroke Precision", use_container_width=True):
        if user_canvas.image_data is not None:
            # FIXED PARAMETER: shape_type passed dynamically into core_engine
            calculated_score = calculate_accuracy(
                user_canvas.image_data, 
                bg_layer, 
                shape_type=step_data["shape_type"]
            )
            
            if calculated_score == -1:
                st.session_state.current_score = None
                st.warning("Trace Void: No detected strokes found on the active canvas layer. Please trace along the visible templates.")
            else:
                st.session_state.current_score = calculated_score
        else:
            st.error("Hardware Canvas Layer Not Initialized.")
            
    if st.session_state.current_score is not None:
        score = st.session_state.current_score
        if score >= 70:
            st.metric(label="Accuracy Rating (PASSED)", value=f"{score}%", delta="Target Match Verified")
            st.success("Excellent! Your strokes match the template guides.")
            
            if current_step_idx < total_steps - 1:
                if st.button("Unlock Next Step ", use_container_width=True):
                    st.session_state.step += 1
                    st.session_state.current_score = None
                    st.rerun()
            else:
                st.balloons() # Dynamic victory visual triggers on final sequence completion
                st.success("Curriculum Mastered! Entire artwork sequence successfully processed.")
                if st.button("Reset Matrix Lesson", use_container_width=True):
                    st.session_state.step = 0
                    st.session_state.current_score = None
                    st.rerun()
        else:
            st.metric(label="Accuracy Rating (LOW)", value=f"{score}%", delta="- Deviates from guidelines")
            st.error("Stroke distribution falls below the structural limit. Trace directly over the visible guidelines.")
