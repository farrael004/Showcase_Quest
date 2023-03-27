
import asyncio
import os
import pickle
import pandas as pd
from bot.utils import get_settings_path
from bot.gpt_api import create_embedding


async def add_knowledge(file, settings, new_knowledge):
    settings_path = get_settings_path(file)
    
    search_history = settings['search_history']
    if new_knowledge in search_history['text'].values: return search_history
    new_knowledge_df = pd.DataFrame({'text': [new_knowledge], 'link':['faqs'], 'ada_search': [create_embedding(new_knowledge)]})
    search_history = pd.concat([search_history, new_knowledge_df])
    search_history['text'].drop_duplicates()
    search_history = search_history.reset_index(drop=True)
    
    settings['search_history'] = search_history
    with open(settings_path, 'wb') as f:
        pickle.dump(settings, f)
        
    return search_history


async def remove_knowledge(file, settings, knowledge_to_forget):
    settings_path = get_settings_path(file)
    
    forgotten_knowledge = settings['search_history']['text'][knowledge_to_forget]
    settings['search_history'] = settings['search_history'].drop(knowledge_to_forget)
    settings['search_history'] = settings['search_history'].reset_index(drop=True)
    
    with open(settings_path, 'wb') as f:
        pickle.dump(settings, f)
        
    return settings['search_history'], forgotten_knowledge
    