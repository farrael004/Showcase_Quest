from bot.internet_search import ddg_search
import pandas as pd
import json
import asyncio

file_loc = 'Lomdi Personas.xlsx'
df = pd.read_excel(file_loc, index_col=None, usecols="A,C").dropna()

with open('bot\\conversation_settings\\Lomdi_template.json', 'r') as f:
    template = json.load(f)

for setting in df.values:
    template['setting_name'] = setting[0]
    template['mood'] = setting[1]
    with open('bot\\conversation_settings\\' + f'{template["setting_name"]}.json', 'w') as f:
        json.dump(template, f, indent=4)