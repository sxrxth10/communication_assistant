import streamlit as st

def display_home():
    # CSS for enhanced home page styling with tabs
    st.markdown("""
        <style>
        .home-container {
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        h2 {
            color: #34495e;
            font-size: 24px;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .module-card {
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
        }
        .step {
            font-size: 16px;
            margin: 10px 0;
            color: #2c3e50;
        }
        .step b {
            color: #2980b9;
        }
        .stTabs [role="tablist"] {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stTabs [role="tab"] {
            color: #34495e;
            font-weight: bold;
            padding: 8px 16px;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background-color: #3498db;
            color: white;
            border-radius: 6px;
        }
        </style>
    """, unsafe_allow_html=True)



    st.title("Welcome to Your Communication Journey!")
    st.write("Your all-in-one AI-powered tool to master speaking skills.")


    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs for Overview and Guide
    tab1, tab2 = st.tabs(["Project Overview", "Beginner’s Guide"])

    # Tab 1: Project Overview
    with tab1:
        st.subheader("Project Overview")
        st.write("""
        This app is designed to help you become a confident and effective communicator. Whether you're preparing for a job interview, sharpening your debate skills, or simply improving everyday conversations, our AI-driven modules provide personalized practice and feedback. Here's what you can expect:
        - **Interactive Practice**: Engage with AI in realistic scenarios tailored to your goals.
        - **Detailed Feedback**: Get insights on content, delivery, grammar, and more to pinpoint strengths and areas for growth.
        - **Progress Tracking**: Visualize your improvement over time with charts and tips powered by AI.
        - **Beginner-Friendly**: No prior experience needed—just dive in and start speaking!
        """)
        
        st.markdown("### Explore Our Modules:")
        st.markdown('<div class="module-card">- <b>Daily Practice</b>: Chat with AI as an interviewer, debater, or friend to build confidence.</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-card">- <b>Skill Training</b>: Sharpen impromptu speaking, storytelling, and conflict resolution.</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-card">- <b>Presentation</b>: Submit weekly presentations for detailed AI feedback.</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-card">- <b>Progress</b>: Track your improvement over time with trends and tips.</div>', unsafe_allow_html=True)

    # Tab 2: Beginner’s Guide
    with tab2:
        st.subheader("Beginner’s Guide: Get Started in 3 Steps")
        st.write("""
        New to the app? Follow these simple steps to kick off your communication journey:
        """)
        st.markdown('<div class="step"><b>Step 1: Start with Daily Practice</b> - Navigate to "Daily Practice" from the sidebar, choose a conversation partner (e.g., Job Interviewer), and type or record your first message.</div>', unsafe_allow_html=True)
        st.markdown('<div class="step"><b>Step 2: Review Feedback</b> - After chatting, click "End Chat" to get AI feedback on your performance. Note areas like Vocabulary or Delivery to focus on.</div>', unsafe_allow_html=True)
        st.markdown('<div class="step"><b>Step 3: Track Progress</b> - Visit the "Progress" page to see your scores over time and click "Generate Tips" for personalized advice.</div>', unsafe_allow_html=True)
        st.write("That’s it! Practice daily, explore other modules, and watch your skills grow.")

    st.markdown('</div>', unsafe_allow_html=True)  


