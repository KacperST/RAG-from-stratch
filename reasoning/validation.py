import re

def validate_answer(answer, retrieved_docs):
    if "BRAK INFORMACJI" in answer.upper():
        return True
    match = re.search(r"\[CYTAT:\s*(.*?)\]", answer, re.DOTALL)
    if not match: return False
    
    # Oczyszczanie cytatu z wielokropków modelu
    quote = match.group(1).replace("...", "").replace("[...]", "").strip()
    if len(quote) < 10: return False
    
    return any(quote.lower() in doc.lower() for doc in retrieved_docs)