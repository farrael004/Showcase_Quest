import bs4
import io
import re
import PyPDF2
import requests
from duckduckgo_search import ddg
from logging import warning
import pandas as pd
from bot.gpt_api import create_embedding, gpt3_call


def generate_query(last_user_message, conversation_history, settings):
    query_prompt = f"""{settings['archetype']['mood']}

You are having a conversation with a user. These are the relevant entries from the conversation so far (in order of importance):
{conversation_history}

The user's last message was:
{last_user_message}

Please write an internet query that would help in continuing the conversation. Only write one query.
Internet query:
"""

    query, tokens_used = gpt3_call(prompt=query_prompt,
                            tokens=250,
                            temperature=settings['temperature'])

    return query, tokens_used

def ddg_search(query: str, numResults: int, region: str=None, time_period=None):
    print(query)
    try:
        results = ddg(query, region, 'on', time_period, numResults)
        if results == None or results == []:
            return pd.DataFrame(columns=['title', 'link', 'text', 'query', 'text_length', 'ada_search'])
        results = pd.DataFrame(results)
        results.columns = ['title', 'link', 'text']
        results['query'] = [query for _ in results.index]
        results['text_length'] = results['text'].str.len()
        results['ada_search'] = results['text'].apply(lambda x: create_embedding(x))
    except Exception as e:
        print(e)
        return pd.DataFrame(columns=['title', 'link', 'text', 'query', 'text_length', 'ada_search'])

    return results
    

def google_search(search: str, search_depth: int):
    # Make a search request
    try:
        res = requests.get('https://google.com/search?q=' + search)
        res.raise_for_status() # Raise if a HTTPError occured
    except:
        warning("There was a problem with this services's internet")
        raise
    
    links = find_links_from_search(res)
    largest_results = page_search(search, search_depth, links)
    return largest_results


def find_links_from_search(res):
    # Extract link results from the search request
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    link_elements = soup.select('a')
    links = [link.get('href').split('&sa=U&ved=')[0].replace('/url?q=', '')
            for link in link_elements
            if '/url?q=' in link.get('href') and
            'accounts.google.com' not in link.get('href') and
            'support.google.com' not in link.get('href')]
    return list(set(links)) # Remove duplicates while maintaining the same order

def page_search(search, search_depth, search_history, links):
    # Explore the links
    links_attempted = -1
    links_explored = 0
    search_results = pd.DataFrame(columns=['text', 'link', 'query'])
    link_history = search_history['link'].unique().tolist()
    while links_explored < search_depth or links_attempted == len(links):
        links_attempted += 1
        if links == []:
            warning(f"No internet results found for \"{search}\"")
            raise
        if links[links_attempted] in link_history: continue
        # If this link does not work, go to the next one
        try:
            res = requests.get(links[links_attempted])
            res.raise_for_status()
        except:
            continue
        
        # Create a table with the useful texts from the page, the page's link, and the query used 
        useful_text = extract_useful_text(res)
        link_list = [links[links_attempted] for i in range(len(useful_text))] # Creates a list of the same link to match the length of useful_text
        query_list = [search for i in range(len(useful_text))] # Creates a list of the same query to match the length of useful_text
        link_results = pd.DataFrame({'text': useful_text, 'link': link_list, 'query': query_list})
        search_results = pd.concat([search_results, link_results])
        links_explored += 1
    
    # Filter for only the largest results
    search_results['text_length'] = search_results['text'].str.len()
    largest_results = search_results.nlargest(50, 'text_length')
    largest_results = largest_results.drop_duplicates()

    # Create embeddings
    largest_results['ada_search'] = largest_results['text'].apply(lambda x: create_embedding(x))
    return largest_results


def extract_useful_text(res):
    if res.headers['Content-Type'] == 'application/pdf':
        return extract_from_pdf(res)
    return extract_from_html(res)


def extract_from_html(res):
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    link_text = list(set(soup.get_text().splitlines())) # Separate all text by lines and remove duplicates
    useful_text = [s for s in link_text if len(s) > 30] # Get only strings above 30 characters
    useful_text = split_paragraphs(useful_text) # If the string is too long it will split it at full stops '. '
    return split_paragraphs(useful_text) # Do it again just for good measure (otherwise it wouldn't work for all strings for some reason. Try searching "Who is Elon Musk" to test this issue)


def extract_from_pdf(response):
    pdf_content = response.content
    pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(pdf_content)) # Open the PDF file using PyPDF2
    # Extract the text from the PDF file
    pdf_text = ''
    for page_num in range(pdf_reader.getNumPages()):
        pdf_text += pdf_reader.getPage(page_num).extractText()

    pdf_text = re.sub(r'\r\n|\r|\n', ' ', pdf_text) # Remove new lines 
    return split_paragraphs([pdf_text], 500)


def split_paragraphs(paragraphs, max_length=1000):
    split_paragraphs = []
    for paragraph in paragraphs:
        # Split the paragraph until no parts are larger than the max length
        while len(paragraph) > max_length:
            split_index = paragraph.find('. ', max_length)
            # If there's no '. ' after the max length, check for the next instance of '.['
            if split_index == -1:
                split_index = paragraph.find('.[', max_length)
                # If there's no instance of '.[' after the max length, just split at the max length
                if split_index == -1:
                    split_index = max_length
            split_paragraph = paragraph[:split_index]
            # Indicate where strings were split with '(...)'
            if split_paragraph.startswith('.'):
                split_paragraph = '(...)' + split_paragraph[1:]
            else:
                split_paragraph += '(...)'
            split_paragraphs.append(split_paragraph)
            paragraph = paragraph[split_index:]
        split_paragraphs.append(paragraph)
    return split_paragraphs
  
   
def update_history(results, history):
    if history.empty:
        history = results
    else:
        history = pd.concat([history, results]).drop_duplicates(subset=['text'])

    return history
 

def all_are_valid_links(links):
    for link in links:
        try:
            res = requests.get(link)
            res.raise_for_status()
            return True
        except:
            warning("One or more links specified are not valid.")
            return False