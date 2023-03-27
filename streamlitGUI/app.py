from streamlit_lottie import st_lottie
import streamlit as st
import requests
import os
import sys

script_path = os.path.dirname(__file__)
parent_folder = os.path.dirname(script_path)
sys.path.append(parent_folder)

from bot.internet_search import *
from bot.assistant import *
from bot.regions import regions
from streamlitGUI.responses import respond
from streamlitGUI.init_bot import load_assistant_settings
from streamlitGUI.create_assistant import create_assistant_ui
from streamlitGUI.bot_interactions import display_chat_history, display_assistant_response, add_searches, add_links, assistant_settings

@st.cache_data
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        warning(f'Could not find lottie from url {url}.')
        return None

st.set_page_config(page_title='Quest🔍')
st.title("Quest🔍")
st.markdown('Tired of sifting through search results to find the \
    information you need? The Assistant can take care of it for you! \
        This open source AI-powered personal assistant can access the internet, \
            providing both quick and accurate answers to your questions.')

# Create Sidebar
with st.sidebar:
    lottie_image1 = load_lottie_url('https://assets10.lottiefiles.com/packages/lf20_ofa3xwo7.json')
    st_lottie(lottie_image1)

tab1, tab2 = st.tabs(["Chat", "Create"])

with tab2:
    loaded_archetype = create_assistant_ui()

with tab1:
    response = st.container()
    chat = st.container()

    # Section where user inputs directly to GPT
    with chat:
        with st.form('Chat'):
            user_chat_text = st.text_area(label="Ask the Assistant")
            col1, col2, col3 = st.columns([1,4,3])
            region = col3.selectbox('Region', regions.keys(), index=63)
            chat_submitted = col1.form_submit_button("Submit")
            
        st.session_state['settings'] = assistant_settings(chat_submitted, col2, loaded_archetype)
        st.session_state['settings']['region'] = regions[region]

        add_links(st.session_state['settings'])
        add_searches(st.session_state['settings'])


    # User input is used here to process and display GPT's response
    with response:
        if 'archetype' not in st.session_state['settings']:
            archetypes, default_setting_index = load_assistant_settings(loaded_archetype)
            default_setting = list(archetypes.keys())[default_setting_index]
            st.session_state['settings']['archetype'] = archetypes[default_setting]
            
        starting_conversation = st.session_state['settings']['archetype']['starting_conversation']
        
        # load conversation if it is not loaded or if the initial conversation has changed.
        if ('conversation' not in st.session_state 
        or starting_conversation['text'].to_list() != 
        st.session_state['conversation']['text'].iloc[:len(starting_conversation.index)].to_list()):
            st.session_state['conversation'] = starting_conversation
            
        display_chat_history(starting_conversation, st.session_state['settings'])
        
        if chat_submitted and user_chat_text != '':
            st.write('👤User: ' + user_chat_text)
            
            with st.spinner("Generating response..."):
                state = {'settings': st.session_state['settings'], 'search_history': st.session_state['search_history']}
                state['conversation_history'] = st.session_state['conversation']
                response, results, prompt, tokens_used = respond(user_chat_text, state)
            
            display_assistant_response(response, results, prompt, tokens_used)
            
    if st.button("Reset conversation"):
        st.session_state['conversation'] = starting_conversation
        st.experimental_rerun()