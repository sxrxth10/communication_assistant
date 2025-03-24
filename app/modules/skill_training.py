import streamlit as st
from utils.utils import record_and_convert, generate_feedback_skilltraining, generate_prompt_skilltraining

def display_skill_training():
    # Page setup
    st.title("🗣 Skill Training")
    st.write("Practice specific communication skills with AI-generated prompts and feedback.")

    # CSS for consistency
    st.markdown("""
        <style>
        .main-container {
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }
        h3 {
            color: #34495e;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .record-button .stButton>button {
            background-color: #e64e4e !important;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            transition: background-color 0.3s ease;
        }
        .record-button .stButton>button:hover {
            background-color: #c0392b !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Activity selection
    activity = st.selectbox("Choose an activity:", ["Impromptu Speaking", "Storytelling", "Conflict Resolution"])

    # Initialize session state
    if "current_prompt" not in st.session_state or st.session_state.get("current_activity") != activity:
        with st.spinner("Generating a new prompt..."):
            st.session_state.current_prompt = generate_prompt_skilltraining(activity)
        st.session_state.current_activity = activity
        st.session_state.feedback = None

    # Display the prompt as an AI chat message
    with st.chat_message("assistant"):
        if st.session_state.current_prompt.startswith("Oops!") or "error" in st.session_state.current_prompt.lower():
            st.error(st.session_state.current_prompt)  # Display errors in red
        else:
            if activity == "Impromptu Speaking":
                st.write(f"Topic: {st.session_state.current_prompt}")
            elif activity == "Storytelling":
                st.write(f"Prompt: {st.session_state.current_prompt}")
            elif activity == "Conflict Resolution":
                st.write(f"Scenario: '{st.session_state.current_prompt}'")

    # Record button
    st.markdown('<div class="record-button">', unsafe_allow_html=True)
    record_button = st.button("Record Response")
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input for text response
    user_input = st.chat_input("Type your response here...")

    # Process text input
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        with st.spinner(f"Evaluating your {activity.lower()} response..."):
            feedback = generate_feedback_skilltraining(user_input, activity)
        with st.chat_message("assistant"):
            st.write("### Feedback Report")
            st.markdown(feedback)

    # Process voice input
    if record_button:
        audio_file, text = record_and_convert()
        if not text.startswith("Sorry") and not text.startswith("Could not"):
            with st.chat_message("user"):
                st.write("Voice Response:")
                st.audio(audio_file, format="audio/wav")
            with st.spinner(f"Evaluating your {activity.lower()} response..."):
                feedback = generate_feedback_skilltraining(text, activity, is_voice=True)
            with st.chat_message("assistant"):
                st.write("### Feedback Report")
                st.markdown(feedback)

    # Back to Home Button
    st.markdown(
        """
        <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
            <a href="/" target="_self">
                <button style="
                    padding: 10px 20px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #34495e;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    transition: background-color 0.3s ease;
                " onmouseover="this.style.backgroundColor='#2c3e50'" onmouseout="this.style.backgroundColor='#34495e'">
                    ⬅ Back to Home
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)
