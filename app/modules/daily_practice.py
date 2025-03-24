
import streamlit as st
from utils.utils import record_and_convert,daily_practice_chat_response, generate_feedback_daily_practice

def display_daily_practice():
    # Custom CSS for enhanced styling with fixed Record button
    st.markdown("""
        <style>
        /* General layout */
        .main-container {
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* Typography */
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
        .stText {
            color: #7f8c8d;
            font-size: 16px;
        }
        /* Chat container */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding: 15px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            max-height: 400px;
            overflow-y: auto;
        }
        .user-message {
            align-self: flex-end;
            background-color: #3498db;
            color: white;
            padding: 12px;
            margin-left: auto;
            margin-top: 10px;
            border-radius: 15px;
            max-width: 70%;
            text-align: left;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .ai-message {
            align-self: flex-start;
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 12px;
            margin-top: 10px;
            border-radius: 15px;
            max-width: 70%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        /* Buttons */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2980b9;
        }
        .st-emotion-cache-htrdra {
            width: 106.67px;
            position: relative;
            display: flex;
            flex: 1 1 0%;
            flex-direction: column;
            gap: 0rem;
        }
        /* Specific button tweaks */
        .record-button .stButton>button {  /* More specific selector */
            background-color: #e64e4e !important;  /* Red, enforced with !important */
        }
        .record-button .stButton>button:hover {
            background-color: #c0392b !important;  /* Darker red on hover */
            padding: 8px 16px;  /* Fixed padding to match default */
        }
        .end-chat-button>button {
            background-color: #e67e22;
        }
        .end-chat-button>button:hover {
            background-color: #d35400;
        }
        .start-new-button>button {
            background-color: #27ae60;
        }
        .start-new-button>button:hover {
            background-color: #219653;
        }
        /* Selectbox */
        .stSelectbox select {
            background-color: #ffffff;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 5px;
        }
        /* Feedback section */
        .feedback-section {
            margin-top: 20px;
            padding: 15px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    # Main container
    with st.container():

        st.title("Daily Practice")
        st.write("Practice conversations with AI and get feedback on your communication skills.")

        # Conversation Role Selection
        role = st.selectbox("Choose your conversation partner:", ["Job Interviewer", "Debate Opponent", "Casual Friend"])

        # Initialize chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Chat interface
        st.text("Input Your Message:")
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            user_input = st.text_input("Type your message here:", key="text_input", label_visibility="collapsed")
        with col2:
            st.markdown('<div class="record-button">', unsafe_allow_html=True)
            record_button = st.button("Record")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            send_button = st.button("Send")

        # Process input (text or voice)
        if send_button and user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input, "type": "text"})
            with st.spinner("Getting AI response..."):
                ai_response, ai_audio = daily_practice_chat_response(role, st.session_state.chat_history)
            if ai_audio is None:  # Error case
                st.error(ai_response)  # Display error message
            else:
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response, "type": "text", "audio_file": ai_audio})

        elif record_button:
            audio_file, voice_text = record_and_convert()
            if voice_text and not voice_text.startswith("Sorry") and not voice_text.startswith("Could not"):
                st.session_state.chat_history.append({"role": "user", "content": voice_text, "type": "audio", "audio_file": audio_file})
                with st.spinner("Getting AI response..."):
                    ai_response, ai_audio = daily_practice_chat_response(role, st.session_state.chat_history)
                if ai_audio is None:  # Error case
                    st.error(ai_response)  # Display error message
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response, "type": "text", "audio_file": ai_audio})
        # Display chat history
        st.subheader("Conversation History:")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                if message["type"] == "text":
                    st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
                elif message["type"] == "audio":
                    st.markdown(f'<div class="user-message"><b>You (Voice):</b></div>', unsafe_allow_html=True)
                    st.audio(message["audio_file"], format="audio/wav")
            else:
                st.markdown(f'<div class="ai-message"><b>AI:</b> {message["content"]}</div>', unsafe_allow_html=True)
                if "audio_file" in message:
                    st.audio(message["audio_file"], format="audio/mp3")

        # Feedback Section
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.text("End Chat and Get Feedback")
        st.markdown('<div class="end-chat-button">', unsafe_allow_html=True)
        if st.button("End Chat"):
            with st.spinner("Generating feedback..."):
                feedback = generate_feedback_daily_practice(st.session_state.chat_history)

                st.write("### Communication Feedback")
                st.markdown(feedback)
            st.markdown('<div class="start-new-button">', unsafe_allow_html=True)
            if st.button("Start New Chat"):
                st.session_state.chat_history = []
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

