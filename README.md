# RAG-from-stratch
Advanced Modular RAG System with Safe Mode
Projekt zaawansowanego systemu RAG (Retrieval-Augmented Generation) zbudowany w ramach laboratorium programowania agentów AI. System charakteryzuje się modułową architekturą, hybrydowym wyszukiwaniem oraz unikalną warstwą weryfikacji „Safe Mode”, która aktywnie przeciwdziała halucynacjom modelu LLM.

# 🚀 Kluczowe Funkcje
Hybrid Search (Elasticsearch + Qdrant): Połączenie wyszukiwania pełnotekstowego (BM25 z synonimami) oraz semantycznego (Vector Search - E5 Small).

Adaptive Weighted Fusion: Dynamiczne dobieranie wag dla silników wyszukiwania w zależności od intencji zapytania (factual vs. semantic).

Reasoning Layer: Dekompozycja zapytań złożonych oraz doprecyzowanie niejednoznaczności.

Safe Mode (Hallucination Defense): Automatyczna weryfikacja cytatów w odpowiedziach. Jeśli system wykryje halucynację, uruchamia pętlę strategii naprawczych:

modify_prompt: Ponowna próba z surowszą instrukcją.

retry_retrieval: Rozszerzenie kontekstu o dodatkowe dokumenty.

save_to_memory: Odłożenie nierozwiązanego pytania do analizy.

Systemic Memory: Rejestr zapytań pending.json pozwalający na identyfikację luk w bazie wiedzy.

# 📂 Struktura Projektu
```
rag/
├── retrieval/           # Moduły pobierania danych
│   ├── elastic.py       # Konfiguracja ES, schematy (mappings), wyszukiwanie słowne
│   ├── qdrant.py        # Konfiguracja Qdrant, wyszukiwanie wektorowe
│   ├── fusion.py        # Logika fuzji wyników (RRF/Weighted Fusion)
│   └── indexing.py      # Skrypt do budowania bazy z plików NDJSON
├── reasoning/           # Warstwa logiki i weryfikacji
│   ├── chunking.py      # Filtrowanie szumu, tokenizacja, zarządzanie kontekstem
│   ├── prompt.py        # Szablony promptów (Standard, Restrictive, Decomposition)
│   └── validation.py    # Silnik weryfikacji cytatów i komunikacja z LLM
├── memory/
│   └── pending.json     # Pamięć dla pytań bez odpowiedzi (statusy: pending, hallucination)
└── rag_query.py         # Główny orchestrator (Safe Mode Loop)
```
# 🛠️ Instalacja i Konfiguracja
Wymagania:

Docker (dla Elasticsearch i Qdrant)

Ollama (z modelem llama3.1:8b)

Python 3.10+

Uruchomienie baz danych:

Bash

docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.x
docker run -p 6333:6333 qdrant/qdrant
Inicjalizacja danych: W notebooku lub skrypcie uruchom proces indeksowania:

Python

from rag.retrieval.indexing import prepare_data_from_ndjson
id_maps = prepare_data_from_ndjson("your_dataset.ndjson")
📖 Przykłady Działania
Wykrycie halucynacji i Safe Mode
Gdy model próbuje zmyślić cytat, w logach zobaczysz:

[SAFE MODE] Strategia: STANDARD -> ALERT: HALUCYNACJA! Oczyszczony cytat nie istnieje w źródłach. [SAFE MODE] Strategia: MODIFY_PROMPT -> Sukces! Odpowiedź zweryfikowana pozytywnie.

Zapytania nierozwiązane
Jeśli system mimo prób nie znajdzie faktów, zapisze je w memory/pending.json:

JSON

{
  "id": 1,
  "query": "Jaki jest kod dostępu do dokumentu LP-999?",
  "status": "unresolved_after_all_strategies",
  "timestamp": "2026-01-20 12:00:00"
}
# 📝 Wnioski z Rozwoju (Benchmark)
Podczas testów na 16 zróżnicowanych zapytaniach system wykazał:

0% halucynacji dopuszczonych do użytkownika dzięki warstwie validation.py.

Wysoką skuteczność strategii retry_retrieval w przypadku zapytań wymagających szerokiego kontekstu.

Poprawną identyfikację luk w wiedzy przy zapytaniach o obiekty nieobecne w korpusie.
