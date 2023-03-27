# Assistant microservice

## Inputs

The assistant API is stateless and requires that all states are handled outside of it. Things like conversation history and settings must be stored and sent to this API via a state manager. Currently, the API expects the entire conversation history to be provided, including the vectorized version of each entry. This can be improved in the future by simply sending conversation entry IDs that can be used to retrieve information from a database directly nearby this microservice.

In its current iteration, the API expects a dictionary input in the following format:

>### **input_text**
>What the user has just said. **(string)**
>### **conversation_history**
> A table *(pandas DataFrame)* containing three columns:
>1. **text**: An entry in the conversation. **(string)**
>2. **text_length**: How many characters that entry contains. **(int)**
>3. **ada_search**: The vector representation of this entry. **(list of floats)**
>- The expected order is from top-down. The top entry being the oldest and the bottom being the newest.
>### **search_history** *(Optional)*
>This setting allows the assistant to 'know' facts. Any item in this option will be accessible by the assistant when it searches its **Search History**. This optional input will only be used if the *consult_search_history* option is enabled.
>The format expected for this input is a table **(pandas DataFrame)** with six columns:
>1.  **title**: Name/pointer for this fact. **(string)**
>2.  **link**: Url/origin from where this fact came. **(string)**
>3. **text**: Fact that the assistant should know. **(string)**
>4.  **query**: If searched from the internet, the query used to obtain this fact, otherwise can be a copy of the title. **(string)**
>5.  **text_length**: Character count of *'text'*. **(int)**
>6.  **ada_search**: Vector representation of *'text'*. **(list of floats)**
>### **region**
>Specifies the **country code** for use in the internet search. All country codes can be found [here](bot/regions.py). **(string)**
>### **additional_searches** *(Optional)*
>List of search queries that will be used to find additional information from the internet. **(list of stings)**
>### **settings**
>A dictionary containing various parameters that define the behaviour of the assistant. **(dict)**
>1. **answer_with_search**: Determines whether the assistant should perform an internet search to respond to the user's message. **(bool)**
>2. **max_tokens**: Maximum number of tokens that the LLM should output. **(int)**
>3. **temperature**: LLM's temperature setting. **(float)**
>4. **top_p**: LLM's top_p setting. **(float)**
>5. **presence_penalty**: LLM's presence_penalty setting. **(float)**
>6. **frequency_penalty**: LLM's frequency_penalty setting. **(float)**
>7. **num_of_excerpts**: Maximum number of internet results to use when answering. **(int)**
>8. **consult_search_history**: Whether the assistant should use a predefined or otherwise search history when answering a message. **(bool)**
>9. **moderate**: Whether the user's message gets auto moderated when sending a message. **(bool)**
>10. **style_pass**: Whether the assistant uses a style pass to improve the response style to a message. **(bool)**
>11. **include_time**: Whether the assistant should be aware of time. This setting will slightly increase the use of tokens and is not useful most times. **(bool)**
>12. **specify_sources**: Whether the assistant should research a particular link or a series of links to find answers to the user's message. **(string)** *with links separated with a comma and a space [`, `]*
>13. **archetype**: A dictionary that determines the assistant's style. A more detailed explanation is provided below. **(dict)**

#### Archetype
This setting will shape the assistant's personality. It is a dictionary composed of the following parts:
1. **setting_name**: Name that the assistant will know as itself and be refered as. **(string)**
2. **mood**: A descriptive introduction to who/what the assistant is and how it should behave. **(string)**
3. **warn_assistant**: A statement of what the assistant should absolutely stick with or avoid. **(string)**

## Outputs

As mentioned before, since the assistant microservice is stateless, it will not keep things like conversation history, but it return its updated version after a response is generated so it can be kept somewhere else. Here are the things that the assistant microservice will output:

>### **answer**
>The final answer generated to the user's message. **(string)**
>### **conversation_history**
>Same format as input but updated with new conversation entries. A table *(pandas DataFrame)* containing three columns:
>1. **text**: An entry in the conversation. **(string)**
>2. **text_length**: How many characters that entry contains. **(int)**
>3. **ada_search**: The vector representation of this entry. **(list of floats)**
>- The expected order is from top-down. The top entry being the oldest and the bottom being the newest.
>### **search_history**
>Same format as input but updated with new search entries. This setting allows the assistant to 'know' facts. Any item in this option will be accessible by the assistant when it searches its **Search History**. This optional input will only be used if the *consult_search_history* option is enabled.
>The format expected for this input is a table **(pandas DataFrame)** with six columns:
>1.  **title**: Name/pointer for this fact. **(string)**
>2.  **link**: Url/origin from where this fact came. **(string)**
>3. **text**: Fact that the assistant should know how to reference. **(string)**
>4.  **query**: If searched from the internet, the query used to obtain this fact, otherwise can be a copy of the title. **(string)**
>5.  **text_length**: Character count of *'text'*. **(int)**
>6.  **ada_search**: Vector representation of *'text'*. **(list of floats)**
>### **prompt**
>Full prompt used to ask the LLM for a response. Useful for debugging and trying to figure out why the model is behaving in a certain way. **(string)**
>### **similar_search_results**
>Facts used to compose the prompt and add context to improve the answer's accuracy. Useful for debugging and trying to figure out why the model is behaving in a certain way. **(string)**
>### **tokens_used**
>Final sum of all the tokens used by the LLM.