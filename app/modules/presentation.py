import streamlit as st
from utils.utils import record_and_convert, generate_feedback_presentation


def display_presentation():
        
    # Page setup
    st.title("📢 Presentation Submission")
    st.write("Submit your weekly presentation and receive detailed AI feedback.")

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

    # Define 10 weekly presentation tasks
    weekly_tasks = [
        "Deliver a 2-minute self-introduction highlighting your strengths and goals.",
        "Present a project you’ve worked on, explaining its purpose and impact.",
        "Pitch a product or service idea to a potential investor in 2 minutes.",
        "Explain a complex concept (e.g., AI, climate change) in simple terms.",
        "Share a personal success story and what you learned from it.",
        "Argue for or against a controversial topic (e.g., remote work benefits).",
        "Describe your vision for the future of your industry or field.",
        "Teach a skill or hobby you’re passionate about in a clear manner.",
        "Propose a solution to a common workplace problem.",
        "Give a motivational speech to inspire a team or audience."
    ]

    # Manual week selection
    week_options = [f"Week {i+1}: {task[:50]}..." for i, task in enumerate(weekly_tasks)]
    selected_week = st.selectbox("Choose a weekly task:", week_options)
    current_week = week_options.index(selected_week)
    task = weekly_tasks[current_week]

    # Display the selected task
    with st.chat_message("assistant"):
        st.write(f"Task: {task}")

    # Record button
    st.markdown('<div class="record-button">', unsafe_allow_html=True)
    record_button = st.button("Record Presentation")
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input for text submission
    user_input = st.chat_input("Type your presentation here...")

    # Process text input
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        with st.spinner("Evaluating your presentation..."):
            feedback = generate_feedback_presentation(user_input,task)
        if feedback.startswith("Oops!") or "error" in feedback.lower():
                    st.error(feedback)  # Display API errors in red
        else:
            with st.chat_message("assistant"):
                st.write("### Feedback Report")
                st.markdown(feedback)
             
        

    # Process voice input
    if record_button:
        audio_file, text = record_and_convert()
        if not text.startswith("Sorry") and not text.startswith("Could not"):
            with st.chat_message("user"):
                st.write("Voice Presentation:")
                st.audio(audio_file, format="audio/wav")
            with st.spinner("Evaluating your presentation..."):
                feedback = generate_feedback_presentation(text,task, is_voice=True)
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