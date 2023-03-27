import streamlit as st
from bot.utils import markdown_litteral, num_of_tokens
from streamlitGUI.init_bot import load_assistant_settings

def display_assistant_response(answer, similar_google_results, prompt, tokens_used):
    st.markdown('---')
    st.write('Assistant: ' + markdown_litteral(answer))
    with st.expander("Sources:"):
        for row in similar_google_results.iterrows():
            st.write(markdown_litteral(row[1]['text']) + f" [Source]({row[1]['link']})") 
    with st.expander("Prompt used:"):
        st.write(markdown_litteral(prompt).replace('\n','  \n  \n'))
        st.markdown(':green[Tokens used: ]' + f':green[{str(tokens_used)}]')
        

def display_chat_history(starting_conversation, settings):
    chat_so_far = ''
    for i, text in enumerate(st.session_state['conversation']['text']):
        chat_so_far += text + '\n'
        if i < len(starting_conversation): continue
        if settings['include_time']: text = text[:-13]
        if text[:4] == 'User':
            text = '👤' + text
        else:
            text = '🖥️' + markdown_litteral(text)
        st.write(text)
        st.markdown('---')
        
def add_links(settings):
    with st.expander("Add links"):
        num_of_queries = st.number_input("Number of additional links", min_value=0, value=1,
                                         help="Here you can provide sources to the chatbot.")
        
        settings['specify_sources'] = []
        for i in range(num_of_queries):
            search = st.text_input("Link", key=f'l_{i}')
            if search != '':
                settings['specify_sources'].append(search)
                
    return settings

def add_searches(settings):
    with st.expander("Add searches"):
        num_of_queries = st.number_input("Number of additional searches", min_value=0, value=1,
                                         help="Here you can provide supporting searches to the chatbot.")
        
        settings['additional_searches'] = []
        for i in range(num_of_queries):
            search = st.text_input("Search query", key=f's_{i}')
            if search != '':
                settings['additional_searches'].append(search)
                
    return settings


def assistant_settings(chat_submitted, col2, loaded_archetype):
    settings = {}
    if 'settings' not in st.session_state:
        st.session_state['settings'] = settings
    
    if 'answer_with_search' not in st.session_state['settings']:
        st.session_state['settings']['answer_with_search'] = False
    settings['answer_with_search'] = col2.checkbox('Search internet to answer',
                                        value=False,
                                        help="When checked, the Assistant will make a new \
                                            search using your question as the query. If you \
                                                disable this, the Assistant will use only the \
                                                        search history.")
    with st.expander("Assistant settings"):
        col1, col2 = st.columns(2)
        archetypes, default_setting_index = load_assistant_settings(loaded_archetype)
        archetypes_list = list(archetypes.keys())

        archetype = col1.selectbox('Archetype',
                                                archetypes_list,
                                                help='Determines how the assistant will behave \
                                                    (Custom archetypes can be created in the \
                                                        "Create your Assistant" tab).',
                                                index=default_setting_index)

        if 'num_of_excerpts' not in st.session_state['settings']:
            st.session_state['settings']['num_of_excerpts'] = 5
            st.session_state['settings']['consult_search_history'] = False
            st.session_state['settings']['specify_sources'] = ''
            st.session_state['settings']['max_tokens'] = archetypes[archetype]['params']['max_tokens']
            st.session_state['settings']['temperature'] = archetypes[archetype]['params']['temperature']
            st.session_state['settings']['top_p'] = archetypes[archetype]['params']['top_p']
            st.session_state['settings']['presence_penalty'] = archetypes[archetype]['params']['presence_penalty']
            st.session_state['settings']['frequency_penalty'] = archetypes[archetype]['params']['frequency_penalty']
            st.session_state['settings']['consult_search_history'] = archetypes[archetype]['params']['consult_search_history']
            st.session_state['settings']['moderate'] = archetypes[archetype]['params']['moderate']
            st.session_state['settings']['style_pass'] = archetypes[archetype]['params']['style_pass']
        
        settings['max_tokens'] = col1.number_input('Max tokens',
                                              min_value=0,max_value=2000,
                                              value=archetypes[archetype]['params']['max_tokens'])
                  
        settings['temperature'] = col2.slider('Temperature',
                                              min_value=0.0,max_value=1.0,
                                              value=archetypes[archetype]['params']['temperature'],
                                              step=0.01,
                                              help="Determine how random the Assistant responses are \
                                                  lower numbers mean more deterministic answers \
                                                      higher values mean more random.") 
        
        settings['top_p'] = col2.slider('Top p',
                                              min_value=0.0,max_value=1.0,
                                              value=archetypes[archetype]['params']['top_p'],
                                              step=0.01,
                                              help="""An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.""")
        
        settings['presence_penalty'] = col2.slider('Presence penalty',
                                              min_value=-2.0,max_value=2.0,
                                              value=archetypes[archetype]['params']['presence_penalty'],
                                              step=0.01,
                                              help="""Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.""")
        
        settings['frequency_penalty'] = col2.slider('Frequency penalty',
                                              min_value=-2.0,max_value=2.0,
                                              value=archetypes[archetype]['params']['frequency_penalty'],
                                              step=0.01,
                                              help="""Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.""")
        
        with col2.container():
            st.write("")
        
        settings['num_of_excerpts'] = col1.number_input('How many excerpts to use',
                                                          min_value=1,
                                                          value=3,
                                                          help='This indicates how many \
                                                              pieces of texts from searches \
                                                                  to use in the prompt') 
        
        settings['consult_search_history'] = col1.checkbox('Consult search history',
                                                             value=archetypes[archetype]['params']['consult_search_history'],
                                                             help="When checked, the Assistant will look into \
                                                                 the search history to find relevant excerpts.")
        
        settings['moderate'] = col1.checkbox('Auto moderation',
                                                             value=archetypes[archetype]['params']['moderate'],
                                                             help="When checked, both the messages sent by the \
                                                                 Assistant as well as the user will be checked and \
                                                                     blocked if the moderation API detects something.")
        
        settings['style_pass'] = col1.checkbox("Style pass",
                                                help="""When checked, the AI will have a second pass on the image to make it more in the style described by the AI's mood. This will make the AI use more tokens.""",
                                                value=archetypes[archetype]['params']['style_pass'])   
        
        settings['include_time'] = False
        settings['specify_sources'] = ''
        
    if chat_submitted:
        settings['archetype'] = archetypes[archetype]
        st.session_state['settings'] = settings
        st.session_state['search_history'] = settings['archetype']['search_history']
                                                                
    return settings
        
