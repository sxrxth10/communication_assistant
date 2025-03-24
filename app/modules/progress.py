import streamlit as st
import pandas as pd
from utils.utils import generate_tips_from_trend

def display_progress():
    st.title("📈 Progress Tracking")
    st.write("View your day-by-day progress and trends across all modules.")

    # CSS for consistency and custom styling
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
        .day-header {
            font-size: 22px;
            font-weight: bold;
            color: #2980b9;
            margin-bottom: 10px;
        }
        .module-name {
            font-size: 20px;
            font-weight: bold;
            color: #34495e;
            margin-bottom: 5px;
        }
        .module-container {
            margin-bottom: 15px;
        }
        .back-to-home-container {
            display: flex;
            justify-content: flex-end;
            margin-top: 20px;
        }
        .back-to-home-button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            background-color: #34495e;
            color: white;
            border: none;
            border-radius: 20px;
            transition: background-color 0.3s ease;
        }
        .back-to-home-button:hover {
            background-color: #2c3e50;
        }
        </style>
    """, unsafe_allow_html=True)

    # Interactive Progress Chart from CSV
    st.subheader("Progress Over Time")
    try:
        df = pd.read_csv("progress.csv")
        if df.empty:
            st.write("No data for graph yet. Keep practicing!")
        else:
            df['date'] = pd.to_datetime(df['date'])
            # Calculate single average score per day across all criteria
            criteria_cols = ['Content', 'Delivery', 'Structure', 'Language skills', 'Creativity', 'Communication', 'Vocabulary', 'Grammar']
            avg_scores = df.groupby('date')[criteria_cols].mean().mean(axis=1).to_frame(name='Average Score')

            # Single-user interactive chart
            with st.container(border=True):
                rolling_average = st.toggle("Rolling Average (7-day)", value=False)
                if rolling_average:
                    chart_data = avg_scores.rolling(7, min_periods=1).mean()  # Rolling average over 7 days
                else:
                    chart_data = avg_scores

                # Tabs for chart and dataframe
                tab1, tab2 = st.tabs(["Chart", "Data"])
                with tab1:
                    st.line_chart(chart_data, height=250, use_container_width=True)
                with tab2:
                    st.dataframe(df, height=250, use_container_width=True)  # Full raw data

    except FileNotFoundError:
        st.write("No data for graph yet. Start practicing!")

    # Get Tips Section
    st.subheader("Advice")
    st.markdown('<div class="tips-section">', unsafe_allow_html=True)
    st.write("Click below to get AI-generated advice based on your past performance.")
    st.markdown('<div class="tips-button">', unsafe_allow_html=True)
    if st.button("Generate"):
        with st.spinner("Generating tips based on your progress..."):
            try:
                df = pd.read_csv("progress.csv")
                tips = generate_tips_from_trend(df)
                if tips.startswith("Oops!") or "error" in tips.lower():
                    st.error(tips)  # Display API errors in red
                else:
                    st.markdown("### Your Personalized Tips")
                    st.markdown(tips)
            except FileNotFoundError:
                st.write("No progress data available yet. Start practicing to get tips!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Back to Home Button
    st.markdown(
        """
        <div class="back-to-home-container">
            <a href="/" target="_self">
                <button class="back-to-home-button">
                    ⬅ Back to Home
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

