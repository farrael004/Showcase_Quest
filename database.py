import os
import sys
from sqlalchemy import create_engine
import pandas as pd
from bot.utils import str_to_list

engine = create_engine("sqlite:///conversations.db")

def create_conversation(id, bot_name, initial_conversation):
    initial_conversation['ada_search'] = initial_conversation['ada_search'].apply(lambda x: str(x))
    initial_conversation.to_sql(f"{bot_name}_{id}", engine, if_exists="replace", index=False)
    return initial_conversation

def get_conversation(id, bot_name):
    query = f"SELECT * from {bot_name}_{id}"
    
    df = pd.read_sql(query, engine)

    df['ada_search'] = df['ada_search'].apply(str_to_list)

    return df

def conversation_exists(id, bot_name):
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    df = pd.read_sql_query(query, engine)
    if f'{bot_name}_{id}' in df['name'].values:
        return True
    else:
        return False