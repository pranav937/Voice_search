import streamlit as st
import pandas as pd
import os
import json
import uuid
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from streamlit_mic_recorder import speech_to_text
from rapidfuzz import fuzz

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, "all_data_final.csv")
HISTORY_FILE_PATH = os.path.join(BASE_DIR, "chat_history.json")

# API Key Configuration
# Set this in your environment variables or Streamlit secrets
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY_HERE"

# Streamlit UI Configuration
st.set_page_config(page_title="JaxMart AI Chatbot welcome nfur ", page_icon="🤖", layout="wide")

# Custom CSS for Creative UI
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    
    /* Title Styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .sub-title {
        text-align: center;
        color: #B0BEC5;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Chat Message Bubbles */
    .stChatMessage {
        background-color: rgba(20, 30, 40, 0.7) !important;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 201, 255, 0.2);
        margin-bottom: 15px;
    }

    /* Table Styling for Product Results */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    th {
        background-color: rgba(0, 201, 255, 0.2);
        color: #00C9FF !important;
        padding: 10px;
        text-align: left;
        border-bottom: 2px solid #00C9FF;
    }
    td {
        padding: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: #E0E0E0;
    }

    /* Force text color in chat */
    .stChatMessage p, .stChatMessage li {
        color: #FFFFFF !important;
        font-size: 1.05rem;
    }

    /* Input box styling */
    .stChatInputContainer {
        border-radius: 15px;
        border: 1px solid #00C9FF !important;
        box-shadow: 0 4px 15px rgba(0, 201, 255, 0.15);
        background-color: rgba(10, 20, 30, 0.9);
    }
    
    .stChatInputContainer textarea {
        color: white !important;
    }

    /* CSS to float the STT iframe to bottom right, near the send button */
    iframe[title="streamlit_mic_recorder.streamlit_mic_recorder"] {
        position: fixed !important;
        bottom: 22px !important;
        right: 60px !important;
        width: 100px !important;
        height: 45px !important;
        z-index: 999999 !important;
    }
    
    /* Make the button wrapper zero-height so it doesn't take space in the normal flow */
    div[data-testid="stVerticalBlock"] > div:has(iframe[title="streamlit_mic_recorder.streamlit_mic_recorder"]) {
        margin: 0 !important;
        padding: 0 !important;
        height: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load History from File
def load_history():
    if os.path.exists(HISTORY_FILE_PATH):
        try:
            with open(HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {} # Reset if it was the old list format
        except:
            return {}
    return {}

# Save History to File
def save_history(sessions):
    with open(HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=4)

# Initialize Memory
if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = load_history()
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.header("⚙️ JaxMart Settings")
    st.success("✅ AI Engine Online (Groq)")
    
    mic_lang_name = st.selectbox(
        "🎙️ Voice Language",
        [
            "English (India)",
            "Hindi",
            "Gujarati",
            "Marathi",
            "Bengali",
            "Tamil",
            "Telugu",
            "Kannada",
            "Malayalam",
            "Punjabi",
            "Urdu (Pakistan)",
            "English (US)",
        ]
    )
    lang_codes = {
        "English (India)": "en-IN",
        "Hindi":           "hi-IN",
        "Gujarati":        "gu-IN",
        "Marathi":         "mr-IN",
        "Bengali":         "bn-IN",
        "Tamil":           "ta-IN",
        "Telugu":          "te-IN",
        "Kannada":         "kn-IN",
        "Malayalam":       "ml-IN",
        "Punjabi":         "pa-IN",
        "Urdu (Pakistan)": "ur-PK",
        "English (US)":    "en-US",
    }
    mic_lang = lang_codes[mic_lang_name]
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
        
    st.markdown("---")
    
    st.header("📜 Past Chats")
    
    # Display previous sessions as buttons
    if len(st.session_state.all_sessions) == 0:
        st.info("No previous chats.")
    else:
        for session_id, session_data in reversed(list(st.session_state.all_sessions.items())):
            title = session_data.get("title", "Unknown Chat")
            if st.button(f"💬 {title}", key=session_id, use_container_width=True):
                st.session_state.current_session_id = session_id
                st.session_state.messages = session_data.get("messages", [])
                st.session_state.chat_history = session_data.get("messages", [])
                st.rerun()
            
    st.markdown("---")
    if st.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.all_sessions = {}
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.session_state.chat_history = []
        save_history({})
        st.rerun()
st.markdown('<div class="main-title">🤖 JaxMart AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Product & Market Search Engine</div>', unsafe_allow_html=True)
st.markdown("---")

import psycopg2
from sqlalchemy import create_engine

# Database connection
DB_URI = "postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db"
engine = create_engine(DB_URI)

@st.cache_data
def load_dataset():
    try:
        query = """
        SELECT 
            l.title AS "Product Name",
            c.name AS "Category",
            u."fullName" AS "Company Name",
            pd."pricePerUnit" AS "Price",
            'India' AS "Location"
        FROM listings l
        LEFT JOIN categories c ON l."categoryId" = c.id
        LEFT JOIN users u ON l."sellerId" = u.id
        LEFT JOIN product_details pd ON l.id = pd."listingId"
        WHERE l.title IS NOT NULL
        """
        df = pd.read_sql(query, engine)
        df = df[['Product Name', 'Category', 'Company Name', 'Price', 'Location']].dropna(subset=['Product Name'])
        df = df.astype(str)
        return df
    except Exception as e:
        st.error(f"Error loading from Database: {e}")
        return pd.DataFrame()

# Load Dataset (Once)
df_global = load_dataset()

def search_products(query, df, top_n=100):
    if df.empty:
        return ""
    
    query_lower = query.lower()
    
    if query_lower == 'none' or not query_lower:
        return ""

    def calculate_score(row):
        text = (str(row['Product Name']) + " " + str(row['Category']) + " " + str(row['Location'])).lower()
        score = fuzz.partial_ratio(query_lower, text)
        
        # Priority 1: Exact match in Product Name
        if query_lower in str(row['Product Name']).lower():
            score += 50
            
        # Priority 2: Match in Category
        elif query_lower in str(row['Category']).lower():
            score += 20
            
        return score
        
    df['search_score'] = df.apply(calculate_score, axis=1)
    results = df[df['search_score'] > 80].sort_values(by='search_score', ascending=False).head(top_n)
    # If no matches, do not fall back to random sample
    if len(results) == 0:
        return ""
        
    context_string = ""
    for index, row in results.iterrows():
        context_string += f"- Product: {row['Product Name']}, Category: {row['Category']}, Company: {row['Company Name']}, Price: {row['Price']}, Location: {row['Location']}\n"
    return context_string

# Initialize LLM via Groq API
llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
    temperature=0.3
)

# Setup Memory specific to user session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Prompt Template
system_prompt_text = """You are an AI assistant for JaxMart B2B marketplace. 
Below is the relevant product dataset based on the user's query:

{context_data}

Instructions:
1. ONLY return products if the user's query strictly matches the 'Product Name' or 'Category' in the dataset. If they ask for a specific product, do NOT show unrelated items.
2. ALWAYS format the matching products properly using a clear Markdown TABLE. The table must have columns for: Product Name, Category, Company, Price, and Location. Show ALL matching products in this single table.
3. For greetings, ALWAYS use exactly "Hello! How can I help you find products today?" translated strictly into the user's language. Do not add any other extra cultural greetings.
4. STRICT DATABASE RULE: If the user asks ANY question that is NOT about the products in the dataset (e.g., general knowledge, math, casual conversation beyond greetings), you MUST politely refuse. Say exactly: "I can only provide information about products available in our database." (Translate this to their language).
5. NEVER make up information. If the requested product is not present in {context_data}, or if {context_data} is completely empty, you MUST say: "Sorry, I cannot find this product in our current dataset." (Translate this).
6. CRITICAL LANGUAGE RULE: First, identify the language the user is speaking or typing (e.g., Gujarati, Hindi, English). You MUST generate your ENTIRE response in that EXACT same language. If the user asks in Gujarati script, reply in Gujarati script. If the user asks in Hindi, reply in Hindi script. NEVER reply in English if the user asks in another language. All headers, conversational text, and explanations must be translated. NEVER mix languages. Whatever language the prompt is in, use that exact language.
7. ALWAYS provide a text response. NEVER return an empty or blank message.

Chat History:
{history}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    ("human", "{input}")
])

# Define the main response chain
chain = prompt | llm | StrOutputParser()

# Define the keyword extraction & translation chain
keyword_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at extracting search keywords. Read the user's query and extract the main product name, category, and location. Translate these extracted keywords into English. Map common synonyms to a single standard English term (e.g., if they say 'mobile' or 'smart phone' -> output 'smartphone'). Return ONLY the English keywords separated by spaces, with NO extra words, NO punctuation, and NO explanations. For example, if the query is 'અમદાવાદમાં નદીની રેતી', return 'River Sand Ahmedabad'. If the query is just a greeting or unrelated to products, return 'none'."),
    ("human", "{input}")
])
keyword_chain = keyword_prompt | llm | StrOutputParser()

# Create a stable placeholder for the mic to prevent React crashes without clipping
mic_placeholder = st.empty()

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with mic_placeholder:       
    text_from_mic = speech_to_text(language=mic_lang, start_prompt="🎤 Speak", stop_prompt="🛑 Stop", just_once=True, key=f'STT_{mic_lang}')


user_input = st.chat_input("Ask something (e.g., 'Ahmedabad ma river sand su price ma male che?'): ")

if text_from_mic:
    user_input = text_from_mic

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Format history for prompt
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history[-6:]]) # Keep last 6 messages
                
                # Step 1: Translate and extract keywords to English
                english_keywords = keyword_chain.invoke({"input": user_input}).strip()
                
                # Step 2: Search for relevant products based on English keywords
                if english_keywords.lower() == 'none' or not english_keywords:
                    relevant_context = ""
                else:
                    relevant_context = search_products(english_keywords, df_global)
                
                # Hidden language instruction for the LLM to strictly follow the language
                strict_input = user_input + "\n\n[SYSTEM RULE: You MUST reply in the exact same language I just used above. If I used English, reply in English. If I used Hindi, reply in Hindi. If I used Gujarati, reply in Gujarati.]"
                
                # Invoke chain
                answer = chain.invoke({"input": strict_input, "history": history_text, "context_data": relevant_context})
                
                # Display response
                st.markdown(answer)
                
                # Save to memory
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Handle Session ID
                if st.session_state.current_session_id is None:
                    st.session_state.current_session_id = str(uuid.uuid4())
                    title = user_input[:25] + "..." if len(user_input) > 25 else user_input
                    st.session_state.all_sessions[st.session_state.current_session_id] = {"title": title, "messages": []}
                
                # Persist to JSON file
                st.session_state.all_sessions[st.session_state.current_session_id]["messages"] = st.session_state.messages
                save_history(st.session_state.all_sessions)
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")
