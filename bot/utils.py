from transformers import GPT2Tokenizer
from itertools import zip_longest
import pickle
import glob
import os

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
def num_of_tokens(prompt: str):
    return len(tokenizer.encode(prompt))

def str_to_list(string: str):
    return list(map(float, string[1:-1].split(',')))
    
def separate_list(iterable, n):
    # Collect data into fixed-length chunks or blocks
    args = [iter(iterable)] * n
    groups = zip_longest(*args, fillvalue=None) # ('ABCDEFG', 3, 'None') --> ((A,B,C), (D,E,F), (G,None,None))
    result = list(groups)
    return [list(filter(lambda x: x is not None, sublist)) for sublist in result] # Remove None

def markdown_litteral(string: str):
    return string.replace('$','\$')

def load_settings_file(file):
    with open(file, 'rb') as f:
        return pickle.loads(f.read())
    
def app_root():
    script_path = os.path.dirname(__file__)
    parent_folder = os.path.dirname(script_path)
    return parent_folder

def get_settings_path(file):
    parent_folder = app_root()
    folder_path = os.path.join(parent_folder, 'settings')
    settings_path = os.path.join(folder_path, file + '.pkl')
    return settings_path

def get_all_settings_names():
    parent_folder = app_root()
    folder_path = os.path.join(parent_folder, 'settings')
    files = glob.glob(folder_path + '/*.pkl')
    
    file_names = [os.path.basename(file).replace('.pkl','')
                  for file in files]

    return file_names