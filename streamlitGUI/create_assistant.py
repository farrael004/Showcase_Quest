import streamlit as st
import pandas as pd
import json
from bot.gpt_api import get_embedding

def create_assistant_ui():
    customize_assistant = st.container()
    num_of_examples = st.container()
    download_archetype = st.container()
    st.markdown('---')
    load_loaded_archetype = st.container()
    
    with load_loaded_archetype:
        loaded_file = st.file_uploader('Upload custom Assistant')
        
        if loaded_file == None:
            loaded_archetype = {'setting_name': '',
                                'mood': '',
                                'warn_assistant': '',
                                'params': {
                                    'max_tokens': 250,
                                    'temperature': 0.5,
                                    'top_p': 0.9,
                                    'presence_penalty': 0.0,
                                    'frequency_penalty': 0.0,
                                    'consult_search_history': False,
                                    'moderate': False,
                                    'style_pass': False
                                },
                                'starting_conversation': pd.DataFrame({'text': ['','']})}
        else:
            loaded_json = json.loads(loaded_file.read())
            loaded_archetype = {'setting_name':loaded_json['setting_name'],
                                'mood':loaded_json['mood'],
                                'warn_assistant':loaded_json['warn_assistant'],
                                'params':loaded_json['params'],
                                'search_history': {'text': [], 'link': [], 'query': [], 'text_length': [], 'ada_search': []},
                                'starting_conversation':pd.DataFrame(loaded_json['starting_conversation'])}

        if st.button('Apply'):
            st.session_state['settings']['archetype'] = loaded_archetype
            st.session_state['loaded_archetype'] = loaded_archetype
            
            
    if 'loaded_archetype' not in st.session_state:
        st.session_state['loaded_archetype'] = loaded_archetype
    
    with num_of_examples:
        default_val = round(len(loaded_archetype['starting_conversation'].index)/2)
        entries_num = st.number_input('Number of example entries',
                                       min_value=0,
                                       max_value=3,
                                       value=default_val,
                                       help="Useful for showing how the Assistant should behave.")
    
    with customize_assistant:
        new_archetype = {}
        entries = []
        with st.form('Create Assistant'):
            new_archetype['setting_name'] = st.text_input('Name', placeholder='Pirate', value=loaded_archetype['setting_name'])
            new_archetype['mood'] = st.text_area('Mood', placeholder="You are a friendly and helpful AI assistant. The user has requested for you to speak as a pirate would.", value=loaded_archetype['mood'])
            new_archetype['warn_assistant'] = st.text_area('Warning (optional)', placeholder="ATTENTION: Pretend to be a pirate and respond as a pirate would", value=loaded_archetype['warn_assistant'])
            
            with st.expander('Settings'):
                
                c1, c2 = st.columns(2)
                
                max_tokens = c1.number_input('Max tokens',
                                              min_value=50,max_value=2000,
                                              value=loaded_archetype['params']['max_tokens'])
                
                consult_search_history = c1.checkbox(
                    'Consult search history',
                    value=loaded_archetype['params']['consult_search_history'],
                    help="""When checked, the Assistant will look into the search history to find relevant excerpts."""
                )
                moderate = c1.checkbox(
                    'Auto moderation',
                    value=loaded_archetype['params']['moderate'],
                    help="""When checked, the messages sent by the user will be checked and blocked if the moderation API detects something."""
                )
                
                style_pass = c1.checkbox(
                    'Style pass',
                    value=loaded_archetype['params']['style_pass'],
                    help="""When checked, the AI will have a second pass on the image to make it more in the style described by the AI's mood. This will make the AI use more tokens."""
                )
                
                temperature = c2.slider('Temperature',
                                              min_value=0.0,max_value=1.0,
                                              value=loaded_archetype['params']['temperature'],
                                              step=0.01,
                                              help="Determine how random the Assistant responses are \
                                                  lower numbers mean more deterministic answers \
                                                      higher values mean more random.")
                
                top_p = c2.slider('Top p',
                                              min_value=0.0,max_value=1.0,
                                              value=loaded_archetype['params']['top_p'],
                                              step=0.01,
                                              help="""An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
We generally recommend altering this or temperature but not both.""")
                
                presence_penalty = c2.slider('Presence penalty',
                                              min_value=-2.0,max_value=2.0,
                                              value=loaded_archetype['params']['presence_penalty'],
                                              step=0.01,
                                              help="""Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.""")
            
                frequency_penalty = c2.slider('Frequency penalty',
                                              min_value=-2.0,max_value=2.0,
                                              value=loaded_archetype['params']['frequency_penalty'],
                                              step=0.01,
                                              help="""Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.""")
            
                params = {
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': top_p,
                    'presence_penalty': presence_penalty,
                    'frequency_penalty': frequency_penalty,
                    'consult_search_history': consult_search_history,
                    'moderate': moderate,
                    'style_pass': style_pass
                }
            
            with st.expander('Example conversation'):
                for i in range(entries_num):
                    st.markdown('---')
                    default_value_human = ''
                    default_value_assistant = ''
                    if 2*i+1 < len(loaded_archetype['starting_conversation'].index):
                        default_value_human = loaded_archetype['starting_conversation']['text'].iloc[2*i][6:]
                        default_value_assistant = loaded_archetype['starting_conversation']['text'].iloc[2*i+1][len(new_archetype['setting_name'])+2:]
                    human_entry = st.text_area('User', placeholder="Can you tell me a story about Blackbeard?", key=2*i+1, value=default_value_human)
                    ai_response = st.text_area('Target response', placeholder="Arrr, I can spin ye a tale about the notorious Blackbeard! Edward Teach, better known as Blackbeard, was a fearsome pirate who terrorized the Caribbean and the eastern coast of the American colonies in the early 18th century. His long black beard, braided and tied with ribbons, added to his fearsome appearance, and he was known to have a volatile temper. Blackbeard was said to have set fire to his own ship to intimidate his enemies, and his legend has lived on as one of the most famous pirates in history. Eventually, Blackbeard met his end in a battle with a British naval force, but his legend lives on as one of the most notorious pirates to ever sail the seven seas.", key=2*i+2, value=default_value_assistant)

                    if human_entry == '' or ai_response == '':
                        st.warning("Please fill the example for both the human and the Assistant.")
                    else:
                        entries.append(human_entry)
                        entries.append(ai_response)
                        
            
            if st.form_submit_button():
                new_archetype['params'] = params
                new_archetype['starting_conversation'] = entries if entries != [] else ['']
                new_archetype = create_assistant_file(**new_archetype)
                st.session_state['loaded_archetype'] = new_archetype
                st.session_state['settings']['archetype'] = new_archetype
                st.success("Don't forget to donwload your Assistant for later use.")
        
        loaded_archetype = st.session_state['loaded_archetype']
        
        with download_archetype:
            if new_archetype['setting_name'] == '' or 'params' not in new_archetype:
                st.warning('First create an archetype and press the "Submit" button')
            else:
                json_object = json.dumps(new_archetype, indent=4)
                st.download_button('Download Assistant', json_object, file_name=f"{new_archetype['setting_name']}.json")
                
    return loaded_archetype


def create_assistant_file(setting_name, mood, warn_assistant, starting_conversation, params):
    for i, entry in enumerate(starting_conversation):
        if (i % 2) == 0: # if even
            starting_conversation[i] = 'User: ' + entry
        else:
            starting_conversation[i] = f'{setting_name}: ' + entry
    
    text_length = [len(x) for x in starting_conversation]
    conversation = pd.DataFrame({'text': starting_conversation, 'text_length': text_length})
    conversation['ada_search'] = conversation['text'].apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))

    search_history = {
        'text': [],
        'link': [],
        'query': [],
        'text_length': [],
        'ada_search': []
    }

    dictionary = {
        "setting_name": setting_name,
        "mood": mood + '\n',
        "warn_assistant": '\n' + warn_assistant + '\n',
        "params": params,
        "search_history": search_history,
        "starting_conversation": conversation.to_dict()
    }

    return dictionary