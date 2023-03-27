# To create a new setting, simply change setting_name, mood, warn_assistant, and
# starting_conversation. Then run this script.

setting_name = 'Customer Service AI'
mood = "You are a friendly and helpful AI assistant. You were created to answer concisely questions about OccamDAO."
warn_assistant = "WARNING: The user may ask about information that is not in the documents " + \
    "you were provided. If that is the case, try to answer the question based only on the facts " + \
    "given. Only provide one of the following hyperlinks if they are highly relevant:\n" + \
    "Occam Introduction and OCC token: https://hackmd.io/@OccamDAO/Introduction\n" + \
    "Occam DAO Governance: https://hackmd.io/@OccamDAO/Governance\n" + \
    "OccamRazer: https://hackmd.io/@OccamDAO/OccamRazer\n" + \
    "Occam ISPO: https://hackmd.io/@OccamDAO/ISPO"
starting_conversation = ['User: Who are you?',
                         'Assistant: Hello, my name is Assistant. How can I help you?']

import pandas as pd
from openai.embeddings_utils import get_embedding, cosine_similarity
import openai
import json
import os

# Navigate to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
with open(os.path.join(parent_dir, 'api_key.txt'), 'r') as f:
    openai.api_key = f.read()

text_length = [len(x) for x in starting_conversation]
data = pd.DataFrame({'text': starting_conversation, 'text_length': text_length})
print('Creating embeddings...')
data['ada_search'] = data['text'].apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))

dictionary = {
    "setting_name": setting_name,
    "mood": mood + '\n',
    "warn_assistant": '\n' + warn_assistant + '\n',
    "starting_conversation": data.to_dict()
}

# Serializing json
json_object = json.dumps(dictionary, indent=4)
 
# Writing to file
file_name = setting_name.replace(' ', '_') + ".json"
with open(file_name, "w") as outfile:
    outfile.write(json_object)
    
print('Setting successfully created. You may close this window')