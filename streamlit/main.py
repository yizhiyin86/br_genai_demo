import streamlit as st
# import vertexai
from streamlit_chat import message

from english2results import get_results
from timeit import default_timer as timer

# vertexai.init(project=st.secrets["GCP_PROJECT"], 
#               location=st.secrets["GCP_LOCATION"])

# Hardcoded UserID
USER_ID = "bot"

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
    </style>
    <div style='text-align: center; font-size: 2.5rem; font-weight: 600; font-family: "Roboto"; color: #018BFF; line-height:1; '>BBH Data360 Demo</div>
    <div style='text-align: center; font-size: 1.5rem; font-weight: 300; font-family: "Roboto"; color: rgb(179 185 182); line-height:0; '>
        Powered by <svg width="80" height="60" xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 200 75"><path d="M39.23,19c-10.58,0-17.68,6.16-17.68,18.11v8.52A8,8,0,0,1,25,44.81a7.89,7.89,0,0,1,3.46.8V37.07c0-7.75,4.28-11.73,10.8-11.73S50,29.32,50,37.07V55.69h6.89V37.07C56.91,25.05,49.81,19,39.23,19Z"/><path d="M60.66,37.8c0-10.87,8-18.84,19.27-18.84s19.13,8,19.13,18.84v2.53H67.9c1,6.38,5.8,9.93,12,9.93,4.64,0,7.9-1.45,10-4.56h7.6c-2.75,6.66-9.27,10.94-17.6,10.94C68.63,56.64,60.66,48.67,60.66,37.8Zm31.15-3.62c-1.38-5.73-6.08-8.84-11.88-8.84S69.5,28.53,68.12,34.18Z"/><path d="M102.74,37.8c0-10.86,8-18.83,19.27-18.83s19.27,8,19.27,18.83-8,18.84-19.27,18.84S102.74,48.67,102.74,37.8Zm31.59,0c0-7.24-4.93-12.46-12.32-12.46S109.7,30.56,109.7,37.8,114.62,50.26,122,50.26,134.33,45.05,134.33,37.8Z"/><path d="M180.64,62.82h.8c4.42,0,6.08-2,6.08-7V20.16h6.89v35.2c0,8.84-3.48,13.4-12.32,13.4h-1.45Z"/><path d="M177.2,59.14h-6.89V50.65H152.86A8.64,8.64,0,0,1,145,46.2a7.72,7.72,0,0,1,.94-8.16L161.6,17.49a8.65,8.65,0,0,1,15.6,5.13V44.54h5.17v6.11H177.2ZM151.67,41.8a1.76,1.76,0,0,0-.32,1,1.72,1.72,0,0,0,1.73,1.73h17.23V22.45a1.7,1.7,0,0,0-1.19-1.68,2.36,2.36,0,0,0-.63-.09,1.63,1.63,0,0,0-1.36.73L151.67,41.8Z"/><path d="M191,5.53a5.9,5.9,0,1,0,5.89,5.9A5.9,5.9,0,0,0,191,5.53Z" fill="#018bff"/><path d="M24.7,47a5.84,5.84,0,0,0-3.54,1.2l-6.48-4.43a6,6,0,0,0,.22-1.59A5.89,5.89,0,1,0,9,48a5.81,5.81,0,0,0,3.54-1.2L19,51.26a5.89,5.89,0,0,0,0,3.19l-6.48,4.43A5.81,5.81,0,0,0,9,57.68a5.9,5.9,0,1,0,5.89,5.89A6,6,0,0,0,14.68,62l6.48-4.43a5.84,5.84,0,0,0,3.54,1.2A5.9,5.9,0,0,0,24.7,47Z" fill="#018bff"/></svg> | 
        OpenAI
    </div>
""", unsafe_allow_html=True)


def generate_context(prompt, context_data='generated'):
    context = []
    # If any history exists
    if st.session_state['generated']:
        # Add the last three exchanges
        size = len(st.session_state['generated'])
        for i in range(max(size-3, 0), size):
            context.append(st.session_state['user_input'][i])
            if len(st.session_state[context_data]) > i:
                context.append(st.session_state[context_data][i])
    # Add the latest user prompt
    context.append(str(prompt))
    return context


# Generated natural language
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
# Neo4j database results
if 'database_results' not in st.session_state:
    st.session_state['database_results'] = []
# User input
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
# Generated Cypher statements
if 'cypher' not in st.session_state:
    st.session_state['cypher'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


# Define columns
col1, col2 = st.columns([2, 1])

with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    start = timer()
    results = get_results(generate_context(user_input, 'database_results'))
    try:
        cypher_step = results['intermediate_steps']
        print('Total Time : {}'.format(timer() - start))
        if len(cypher_step) > 0 and 'query' in cypher_step[0]:
            st.session_state.cypher.append(cypher_step[0]['query'])
        else :
            st.session_state.cypher.append('')
        if len(cypher_step) > 1 and 'context' in cypher_step[1] and len(cypher_step[1]['context']) > 0:
            st.session_state.database_results.append(cypher_step[1]['context'][0])
        else:
            st.session_state.database_results.append('')
        st.session_state.user_input.append(user_input)
        st.session_state.generated.append(results['result'])
    except Exception as ex:
        print(ex)
        st.session_state.user_input.append(user_input)
        st.session_state.generated.append("Could not generate result due to an error or LLM Quota exceeded")
        st.session_state.cypher.append("")
        st.session_state.database_results.append('{}')


# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        size = len(st.session_state['generated'])
        # Display only the last three exchanges
        for i in range(max(size-3, 0), size):
            message(st.session_state['user_input'][i],
                    is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['cypher']:
        st.text_area("Latest generated Cypher statement",
                     st.session_state['cypher'][-1], height=240)
