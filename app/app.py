import streamlit as st
from modules.daily_practice import display_daily_practice
from modules.skill_training import display_skill_training
from modules.presentation import display_presentation
from modules.progress import display_progress
from modules.home import display_home

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Daily Practice","Skill Training", "Presentation", "Progress" ])

with tab1:
    display_home()
with tab2:
    display_daily_practice()
with tab3:
    display_skill_training()
with tab4:
    display_presentation()
with tab5:
    display_progress()
