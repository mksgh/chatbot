import os
import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import  PromptTemplate # ChatPromptTemplate, MessagesPlaceholder,

from dotenv import load_dotenv

# access environment variables
load_dotenv(dotenv_path=r"C:\Users\mksgh\OneDrive - Vestas Wind Systems A S\Documents\Github\llm-applications\.env")


# azure key 
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")  # type: ignore
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT") # type: ignore
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") # type: ignore
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION") # type: ignore

# langchain tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY") # type: ignore
os.environ["LANGCHAIN_PROJECT"] = "azure-chatbot"  # type: ignore


# initializing the llm deployed in azure
llm= AzureChatOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                     azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
                     openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"], # type: ignore
                    )


# Prompt Template
# template with chat hostory
prompt = PromptTemplate( 
    input_variables=["chat_history", "question"],
    template="""You a a wonderful AI assistant and you name is Mr. PowerX. Please answer the query appropriately as asked by human counterpart

                chat_history: {chat_history}

                Human: {question}"""
  
)

# Persiting chat history in memory using streamlit state 
if "memory" not in st.session_state:
    st.session_state["memory"]=ConversationBufferWindowMemory(memory_key="chat_history", k=10)

output_parser=StrOutputParser()

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=st.session_state["memory"],
    output_parser = output_parser,
    verbose=True
)

## streamlit application
st.title(f'Chantbot- Azure ({os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")})')
st.header('Built using Langchain :sparkles:')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"assistant", "content":"Hello, Please ask your query"}
    ]

#Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
         st.write(message["content"])
        #  st.write(message["content"])

# Accept user input
if user_prompt := st.chat_input("What's' up?"):

    # Add user message to chat history
    st.session_state.messages.append({"role":"user", "content":user_prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(user_prompt)

# Get reposne from llm
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Loading...."):
            ai_response = chain.predict(question=user_prompt)
            st.write(ai_response)
        
        new_ai_message = {"role":"assistant", "content":ai_response}
        st.session_state.messages.append(new_ai_message)        

if st.button("New Chat Session"):
    
    st.session_state.clear()
    st.rerun()
    