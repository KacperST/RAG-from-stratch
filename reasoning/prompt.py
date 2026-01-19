import json
import ollama
from dotenv import load_dotenv
load_dotenv()
import os

def create_prompt(context_list, query):
    context = "\n\n".join(context_list)
    return f"""
    SYSTEM: Jesteś asystentem. Odpowiadaj wyłącznie na podstawie kontekstu.
    Jeśli nie znajdziesz odpowiedzi, napisz: "BRAK INFORMACJI".
    ZASADY: 1. Musisz dodać dosłowny cytat w formacie [CYTAT: tekst].
    
    CONTEXT: {context}
    QUESTION: {query}
    ANSWER:
    """

def create_strict_prompt(context_list, query):
    """To jest Twój RESTRICTIVE PROMPT do Safe Mode."""
    context = "\n\n".join(context_list)
    return f"""
    SYSTEM: TRYB KRYTYCZNEJ WERYFIKACJI. Poprzednia próba zawierała błędy.
    ZADANIE: Odpowiedz używając TYLKO I WYŁĄCZNIE faktów z tekstu. 
    Jeśli nie jesteś pewien na 100%, napisz "BRAK INFORMACJI".
    BEZWZGLĘDNA ZASADA: Odpowiedź musi kończyć się [CYTAT: dokładnie_tekst_ze_źródła].
    
    CONTEXT: {context}
    QUESTION: {query}
    """

def decompose_query_llm(user_input, call_llm_func):
    prompt = f"Rozbij to pytanie na podzapytania w formacie JSON: {{'main_question': '...', 'sub_questions': [...]}}. Pytanie: {user_input}"
    res = call_llm_func(prompt)
    try:
        return json.loads(res[res.find('{'):res.rfind('}')+1])
    except:
        return {"sub_questions": [user_input]}
    
def call_llm(prompt):
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11435')
    ollama_client = ollama.Client(host=OLLAMA_HOST) 
    response = ollama_client.generate(model="llama3.1:8b", prompt=prompt)
    return response.get("response", "")