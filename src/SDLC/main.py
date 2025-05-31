from src.SDLC.ui.loadui import LoadStreamlitUi,initialize_streamlit_ui
import streamlit as st
import os


def load_agentic_sdlc_app(st_session_state):
    initialize_streamlit_ui(st_session_state)

    if "ui" not in st_session_state:
        st_session_state.ui = LoadStreamlitUi(st_session_state)

    if st_session_state.ui.get_session_stage() == "config":
        st_session_state.ui.load_streamlit_ui(st_session_state)
    else:
        st_session_state.ui.render_streamlit_ui(st_session_state)
        
    