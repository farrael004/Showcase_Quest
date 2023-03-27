from openai.embeddings_utils import get_embedding, cosine_similarity
import pandas as pd
import openai
from logging import warning


def find_top_similar_results(df: pd.DataFrame, query: str, n: int):
    if len(df.index) < n:
        n = len(df.index)
    embedding = create_embedding(query)
    df1 = df.copy()
    df1["similarities"] = df1["ada_search"].apply(lambda x: cosine_similarity(x, embedding))
    best_results = df1.sort_values("similarities", ascending=False).head(n)
    return best_results.drop(['similarities', 'ada_search'], axis=1).drop_duplicates(subset=['text'])


def create_embedding(query):
    if query == '': query = ' '
    query = query.encode(encoding='ASCII', errors='ignore').decode()
    return get_embedding(query, engine="text-embedding-ada-002")

def is_not_safe(text: str):
    response = openai.Moderation.create(input=text)
    return response["results"][0]['flagged']

def gpt3_call(prompt: str, tokens: int, top_p: float=1, presence_penalty: float=0, frequency_penalty:float=0, temperature: float=1, stop=None):
    prompt = [
        {'role': 'system', 'content': prompt}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=tokens,
            stop=stop,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty
        )
        
        text = response["choices"][0]['message']["content"]
        tokens_used = response['usage']['total_tokens']

        return text, tokens_used
    except:
        warning("There was a problem when trying to connect with OpenAI's API.")
        raise    