import re
import pandas as pd
from datetime import datetime
from bot.gpt_api import find_top_similar_results, gpt3_call, create_embedding, is_not_safe
from bot.utils import num_of_tokens
from bot.internet_search import *
from bot.regions import regions_inverted as regions


def add_conversation_entry(new_entry, chat_history):
    text_length = len(new_entry)
    data = pd.DataFrame({'text': new_entry, 'text_length': text_length}, index=[0])
    data['ada_search'] = data['text'].apply(lambda x: create_embedding(x))
    return pd.concat([chat_history, data], ignore_index=True)
        

def create_prompt(settings,
                  user_chat_text,
                  chat_history,
                  similar_google_results,
                  similar_conversation,
                  current_time,
                  current_date_and_time):
    
    name = settings['archetype']['setting_name']
    mood = settings['archetype']['mood']
    warn_assistant = settings['archetype']['warn_assistant']
    
    region = '[region missing]'
    if 'region' in settings:
        region = regions[settings['region']]
    
    prompt = mood + current_date_and_time
    prompt += f'\n\nUser information:\nLocation: {region}\n\n'
    
    if similar_google_results.empty:
        prompt += "You were not provided more information.\n"
    else:
        prompt += "Here are your findings from the internet:  \n" + \
            '\n'.join(similar_google_results['text'].to_list()) + "\n"
    prompt += 'These are the relevant entries from the conversation so far (in order of importance):\n' + \
            '\n'.join(similar_conversation['text'].to_list()) + '\nThese are the last four messages:\n' + warn_assistant + \
                 '\n'.join(chat_history['text'].iloc[-2:]) + '\nUser: ' +  user_chat_text + current_time + f'\n{name}:'
    
    return prompt       


def submit_user_message(user_chat_text, chat_history, search_history, settings):
    
    # Knowing the current time and date may be important for interpreting news articles.
    if settings['include_time']:
        date = datetime.now()
        current_time = f' ({date.strftime("%I:%M:%S %p")})\n'
        current_date_and_time = f'Current time is {date.strftime("%I:%M %p %A %B %d %Y")}.\n'
    else:
        current_time = ''
        current_date_and_time = ''

    if settings['moderate']:
        if is_not_safe(user_chat_text):
            answer = 'Sorry, your message was flagged by auto-moderation. Please try again.'
            chat_history = add_conversation_entry('User: ' + user_chat_text + current_time, chat_history)
            chat_history = add_conversation_entry(f"{settings['archetype']['setting_name']}: " + answer + current_time, chat_history)
            return answer, chat_history, search_history, '', pd.DataFrame(), 0
    
    if num_of_tokens(user_chat_text) > 1000:
        answer = "I apologise, but I cannot read that much text all at once. Please send me more concise messages."
        chat_history = add_conversation_entry('User: ' + user_chat_text + current_time, chat_history)
        chat_history = add_conversation_entry(f"{settings['archetype']['setting_name']}: " + answer + current_time, chat_history)
        return answer, chat_history, search_history, '', pd.DataFrame(), 0
    
    # Find relevant search results and conversation entries to craft the AI prompt
    similar_conversation = find_top_similar_results(chat_history, user_chat_text, 4)
    similar_google_results, search_history, tokens_used_for_search = get_info_from_internet(user_chat_text, search_history, settings, chat_history, similar_conversation)
    
    prompt = create_prompt(settings,
                           user_chat_text,
                           chat_history,
                           similar_google_results,
                           similar_conversation,
                           current_time,
                           current_date_and_time)
    
    tokens = num_of_tokens(prompt)
    
    if tokens > 3950:
        answer = "I apologise, but I have a lot in my head all at once. Can you please send me more concise messages?"
        chat_history = add_conversation_entry('User: ' + user_chat_text + current_time, chat_history)
        chat_history = add_conversation_entry(f'{settings["archetype"]["setting_name"]}: ' + answer + current_time, chat_history)
        return answer, chat_history, search_history, prompt, similar_google_results, tokens
    
    answer, tokens_used = gpt3_call(
        prompt,
        tokens=settings['max_tokens'],
        temperature=settings['temperature'],
        stop='User:',
        top_p=settings['top_p'],
        presence_penalty=settings['presence_penalty'],
        frequency_penalty=settings['frequency_penalty']
    )
    tokens_used += tokens_used_for_search
    answer = remove_timestamp(answer)
    
    #if settings['moderate']:
    #    if not is_not_safe(answer):
    #        answer = f'Sorry, my answer was flagged by auto-moderation. Please try again. (Moderated message: {answer})'
    
    if settings['style_pass']:
        print(answer)
        answer, style_tokens = style_pass(prompt, answer, settings)
        tokens += style_tokens

    chat_history = add_conversation_entry('User: ' + user_chat_text + current_time, chat_history) 
    if settings['include_time']:
        date = datetime.now()
        current_time = f' ({date.strftime("%I:%M:%S %p")})\n'
    chat_history = add_conversation_entry(f'{settings["archetype"]["setting_name"]}: ' + answer + current_time, chat_history)
    
    return answer, chat_history, search_history, prompt, similar_google_results, tokens_used


def style_pass(prompt, answer, settings):
    style_prompt = f"""{prompt}
    
The following is the initial response:
{answer}

Please rewrite the response so it better maintains the intended style."""

    return gpt3_call(
        style_prompt,
        tokens=settings['max_tokens'],
        temperature=settings['temperature'],
        stop='User:',
        top_p=settings['top_p'],
        presence_penalty=settings['presence_penalty'],
        frequency_penalty=settings['frequency_penalty']
    )


def get_info_from_internet(user_chat_text, search_history, settings, chat_history, similar_conversation):
    answer_with_search = settings['answer_with_search']
    additional_searches = settings['additional_searches']
    specify_sources = settings['specify_sources']
    consult_search_history = settings['consult_search_history']
    num_of_excerpts = settings['num_of_excerpts']
    tokens_used = 0

    conversation = ('\n'.join(similar_conversation['text'].to_list()) +
                    '\nThese are the last two messages:\n' +
                    chat_history['text'].iloc[-2:])
    
    region = None
    if 'region' in settings:
        region = settings['region']
        
    time_period = None
    if 'time_period' in settings:
        time_period = settings['time_period']
    
    sources_content = pd.DataFrame()
    if specify_sources != ['']:
        sources_content, search_history = search_new_links(user_chat_text, specify_sources, search_history, sources_content)
    
    if additional_searches != []:
        sources_content, search_history, tokens = search_new_queries(additional_searches, search_history, sources_content, region, time_period, conversation, settings)
        tokens_used += tokens
            
    if answer_with_search:       
        sources_content, search_history, tokens = search_new_queries([user_chat_text], search_history, sources_content, region, time_period, conversation, settings)
        tokens_used += tokens
        
    if not consult_search_history:
        if sources_content.empty: return sources_content, search_history, tokens_used
        return find_top_similar_results(sources_content, user_chat_text, num_of_excerpts), search_history, tokens_used
        
    return find_top_similar_results(search_history, user_chat_text, num_of_excerpts), search_history, tokens_used

def search_new_links(user_chat_text, specify_sources, search_history, sources_content):
    already_seen_results = search_history[search_history['link'].isin(specify_sources)]
    links_not_in_history = [value for value in specify_sources if value not in search_history['link'].values]
    if all_are_valid_links(links_not_in_history):
        try:
            sources_content = page_search(user_chat_text, len(links_not_in_history), search_history, links_not_in_history)
            search_history = update_history(sources_content, search_history)
            sources_content = pd.concat([sources_content, already_seen_results])
        except:
            warning("Something went wrong when trying to search in new links")
    return sources_content, search_history

def search_new_queries(additional_searches, search_history, sources_content, region ,time_period, conversation, settings):
    already_seen_results = search_history[search_history['query'].isin(additional_searches)]
    query_not_in_history = [value for value in additional_searches if value not in search_history['query'].values]
    sources_content = pd.concat([sources_content, already_seen_results])
    queries_results = pd.DataFrame()
    tokens_used = 0
    
    try:
        for search in query_not_in_history:
            query, tokens_used = generate_query(search, conversation, settings)
            query_results = ddg_search(query, 3, region, time_period)
            queries_results = pd.concat([queries_results,query_results])
        search_history = update_history(queries_results, search_history)
    except:
        warning("Something went wrong when making new searches.")
        
    sources_content = pd.concat([sources_content, queries_results])
    return sources_content, search_history, tokens_used

def remove_timestamp(string):
    # Compile a regex pattern to match the timestamp at the end of the string
    pattern = re.compile(r'\(\d\d:\d\d:\d\d [AP]M\)$')
    return pattern.sub('', string) # Use the regex to replace the timestamp with an empty string