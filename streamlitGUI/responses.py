import asyncio
import logging
import streamlit as st
from logging import warning
from database import create_conversation
from bot.logger import log_to_file
from bot.assistant import submit_user_message

def respond(input_text:str, state):

    try:
        conversation_history = state['conversation_history']
        search_history = state['search_history']
        settings = state['settings']
        
    except KeyError:
        raise KeyError('Bot not initialized.')
    
    response, conversation_history, search_history, prompt, results, tokens_used = submit_user_message(
        input_text,
        conversation_history,
        search_history,
        settings
    )

    st.session_state['conversation'] = conversation_history
    st.session_state['search_history'] = search_history
    
    return response, results, prompt, tokens_used