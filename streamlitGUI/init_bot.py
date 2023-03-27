import os
import json
import random
import pickle
import collections
import pandas as pd
from streamlit import secrets
import openai
from bot.utils import load_settings_file, get_settings_path, get_all_settings_names


def load_api_key():
    return secrets['API_KEY']

openai.api_key = load_api_key()
        

def assistant_settings1(default_archetype,
                       answer_with_search=False,
                       temperature=1.0,
                       specify_sources='',
                       consult_search_history=True,
                       num_of_excerpts=5,
                       include_time=False,
                       additional_searches=[]):

    archetypes, default_setting_index = load_assistant_settings(default_archetype)
    default_setting = list(archetypes.keys())[default_setting_index]

    settings = {}
    settings['answer_with_search'] = answer_with_search
    settings['temperature'] = temperature
    settings['specify_sources'] = specify_sources
    settings['consult_search_history'] = consult_search_history
    settings['num_of_excerpts'] = num_of_excerpts
    settings['include_time'] = include_time
    settings['additional_searches'] = additional_searches
    settings['archetype'] = archetypes[default_setting]

    return settings


def load_assistant_settings(custom_archetype=None, default_setting="Strictly Factual"):
    script_path = os.path.dirname(__file__)
    folder_path = os.path.join(script_path, 'conversation_settings')
    file_names = os.listdir(folder_path)
    if custom_archetype == None:
        all_settings = []
    else:
        all_settings = [custom_archetype]
        if custom_archetype['setting_name'] != '':
            default_setting = custom_archetype['setting_name']
        
    for file_name in file_names:
        if file_name.endswith('.json'):
            with open(os.path.join(folder_path, file_name)) as f:
                data = json.load(f)
                all_settings.append(data)

    archetypes = {setting['setting_name']: {'setting_name':setting['setting_name'],
                                            'mood':setting['mood'],
                                            'warn_assistant':setting['warn_assistant'],
                                            'params':setting['params'],
                                            'starting_conversation':pd.DataFrame(setting['starting_conversation']),
                                            'search_history':pd.DataFrame(setting['search_history'])}
                    for setting in all_settings if setting['setting_name'] != ''}

    archetypes = collections.OrderedDict(sorted(archetypes.items()))
    default_setting_index = list(archetypes.keys()).index(default_setting)

    return archetypes, default_setting_index
