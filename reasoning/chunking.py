import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

def chunk_text(text, max_tokens=500):
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens])

def filter_retrieved(doc_ids, id_map, min_tokens=30, max_docs=5):
    filtered_docs = []
    noise_patterns = ["cookies", "zaloguj się", "anuluj pisanie"]
    
    for doc_id in doc_ids:
        text = id_map.get(doc_id, "")
        if len(encoding.encode(text)) < min_tokens: continue
        if any(p in text.lower() for p in noise_patterns): continue
        filtered_docs.append(text)
        if len(filtered_docs) >= max_docs: break
    return filtered_docs