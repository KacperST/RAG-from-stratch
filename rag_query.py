from retrieval.qdrant import search_qdrant
from retrieval.elastic import search_elasticsearch
from retrieval.fusion import choose_weights, weighted_fusion
from reasoning.chunking import filter_retrieved
from reasoning.prompt import create_prompt, create_strict_prompt, call_llm
from reasoning.validation import validate_answer
import json
import os
import json
from datetime import datetime
from retrieval.indexing import prepare_data_from_ndjson

def save_to_memory(query, status, file_path="memory/pending.json"):
    """
    Zapisuje zapytanie do pliku JSON jeśli LLM jest niepewny lub jest brak informacji.
    """
    memory = {"pending_queries": []}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                memory = json.load(f)
        except:
            pass
            
    if any(q["query"] == query for q in memory["pending_queries"]):
        return "Zapytanie już istnieje w pamięci."

    new_id = len(memory["pending_queries"]) + 1
    new_entry = {
        "id": new_id,
        "query": query,
        "status": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    memory["pending_queries"].append(new_entry)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
        
    return f"Dodano do pamięci: ID {new_id} ({status})"

def show_unresolved_queries(file_path="pending.json"):
    """
    Umożliwia użytkownikowi wyświetlenie listy nierozwiązanych zapytań.
    """
    if not os.path.exists(file_path):
        print("Brak nierozwiązanych pytań.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"\n{'ID':<5} | {'Status':<20} | {'Zapytanie'}")
        print("-" * 70)
        for q in data["pending_queries"]:
            print(f"{q['id']:<5} | {q['status']:<20} | {q['query']}")

def rag_query_safe(user_query, id_maps):
    # Konfiguracja strategii zgodnie z Zadaniem 2 Etapu IV
    retry_strategies = ["standard", "modify_prompt", "retry_retrieval", "save_to_memory"]
    
    current_docs = []
    best_answer = "BRAK INFORMACJI"

    for strategy in retry_strategies:
        print(f"--- Strategia: {strategy.upper()} ---")

        if strategy == "standard":
            weights = choose_weights(user_query)
            es_r = search_elasticsearch(user_query, top_k=5)
            qd_r = search_qdrant(user_query, top_k=5)
            fused = weighted_fusion(es_r, qd_r, weights)
            current_docs = filter_retrieved([id for id, _ in fused], id_maps)
            prompt = create_prompt(current_docs, user_query)

        elif strategy == "modify_prompt":
            # Użycie RESTRICTIVE PROMPT na tym samym kontekście
            prompt = create_strict_prompt(current_docs, user_query)

        elif strategy == "retry_retrieval":
            # Zmiana interpretacji (szerszy retrieval)
            es_r = search_elasticsearch(user_query, top_k=15)
            qd_r = search_qdrant(user_query, top_k=15)
            fused = weighted_fusion(es_r, qd_r, {"es": 0.5, "qdrant": 0.5})
            current_docs = filter_retrieved([id for id, _ in fused], id_maps, max_docs=10)
            prompt = create_prompt(current_docs, user_query)

        elif strategy == "save_to_memory":
            save_to_memory(user_query, status="unresolved_after_all_strategies")
            return f"PRZEPRASZAM: Nie udało się zweryfikować odpowiedzi. Pytanie zapisane."

        # Wywołanie LLM i Weryfikacja
        answer = call_llm(prompt)
        
        if validate_answer(answer, current_docs):
            if "BRAK INFORMACJI" not in answer.upper():
                return answer # Sukces merytoryczny!
            else:
                print("-> Strategia zwróciła brak danych. Próbuję następnej...")
        else:
            print("-> Wykryto halucynację/błąd formatu. Próbuję następnej strategii...")

    return best_answer

def main():
    query = "Kto jest autorem teorii względności?"
    id_maps = prepare_data_from_ndjson("/home/kacper/DataScience/nlp/bulk_dataset_processed.ndjson") 
    response = rag_query_safe(query, id_maps)
    print(f"\n💬 FINALNA ODPOWIEDŹ:\n{response}\n{'='*100}")

if __name__ == "__main__":
    main()