import streamlit as st
import database as db
from utils import tell_to_reload_page
from gpt_api import test_api_key

# Load the API key to the session state
def load_api_key():
    if 'api_key' not in st.session_state:
        try:
            #api_key = db.get_api_key(st.session_state['username'])
            #st.session_state['api_key'] = api_key
            raise
        except:
            api_key_form()
    return st.session_state['api_key']


def api_key_form():
    st.session_state['api_key'] = st.secrets['API-KEY']

def reset_api_key():
    #db.delete_api_key(st.session_state['username'])
    if 'api_key' in st.session_state:
        st.session_state.pop('api_key')
    st.experimental_rerun()

def reset_key_button():
    st.button('Reset API Key', on_click=reset_api_key)
        