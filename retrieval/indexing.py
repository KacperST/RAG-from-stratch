import json
from elasticsearch import helpers
from qdrant_client.models import PointStruct, VectorParams, Distance
from .elastic import es, ES_INDEX, create_index
from .qdrant import client as qdrant, COLLECTION_NAME

def prepare_data_from_ndjson(file_path="bulk_dataset_processed.ndjson", batch_size=500):
    # 1. Inicjalizacja Qdrant
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # 2. Inicjalizacja Elasticsearch
    create_index()

    id_map = {}
    qdrant_batch, es_batch = [], []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line.strip())
            if "index" in doc or "vector" not in doc: continue

            doc_id = int(doc["id"])
            id_map[doc_id] = doc["text"]
            
            # Przygotowanie paczek (batches)
            qdrant_batch.append(PointStruct(id=doc_id, vector=doc["vector"], payload={k:v for k,v in doc.items() if k != "vector"}))
            es_batch.append({"_index": ES_INDEX, "_id": doc_id, "_source": doc})

            if len(qdrant_batch) >= batch_size:
                qdrant.upsert(collection_name=COLLECTION_NAME, points=qdrant_batch)
                helpers.bulk(es, es_batch)
                qdrant_batch.clear(); es_batch.clear()

    # Flush ostatnich danych
    if qdrant_batch:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=qdrant_batch)
        helpers.bulk(es, es_batch)

    es.indices.refresh(index=ES_INDEX)
    return id_map