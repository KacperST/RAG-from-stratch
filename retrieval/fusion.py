import re

def choose_weights(query):
    has_numbers = bool(re.search(r'\d+', query))
    has_acronyms = bool(re.search(r'\b[A-Z]{2,}\b', query))
    if has_numbers or has_acronyms:
        return {"es": 0.8, "qdrant": 0.2}
    return {"es": 0.4, "qdrant": 0.6}

def weighted_fusion(es_results, qdrant_results, weights, k=60):
    scores = {}
    for doc_id, _, rank in es_results:
        scores[doc_id] = scores.get(doc_id, 0) + weights["es"] * (1.0 / (k + rank))
    for doc_id, _, rank in qdrant_results:
        scores[doc_id] = scores.get(doc_id, 0) + weights["qdrant"] * (1.0 / (k + rank))
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)