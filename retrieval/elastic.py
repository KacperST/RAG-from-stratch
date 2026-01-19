from elasticsearch import Elasticsearch

ES_HOST = "http://localhost:9200"
ES_INDEX = "culturax_semantic"
es = Elasticsearch(ES_HOST)

ES_INDEX_BODY = {
    "settings": {
        "analysis": {
            "filter": {
                "pl_month_syn": {
                    "type": "synonym",
                    "synonyms": [
                        "styczeń, sty, i",
                        "luty, lut, ii",
                        "marzec, mar, iii",
                        "kwiecień, kwi, iv",
                        "maj, v",
                        "czerwiec, cze, vi",
                        "lipiec, lip, vii",
                        "sierpień, sie, viii",
                        "wrzesień, wrz, ix",
                        "październik, paź, paz, x",
                        "listopad, lis, xi",
                        "grudzień, gru, xii"
                    ]
                },
                "pl_morfologik": {
                    "type": "morfologik_stem"
                }
            },
            "analyzer": {
                "pl_syn_lemma": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "pl_month_syn",
                        "pl_morfologik"
                    ]
                },
                "pl_lemma": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "pl_morfologik"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},

            "text": {
                "type": "text",
                "analyzer": "pl_lemma"
            },

            "text_syn": {
                "type": "text",
                "analyzer": "pl_syn_lemma"
            },

            "timestamp": {
                "type": "date"
            },

            "sentyment": {
                "type": "keyword"
            },

            "styl": {
                "type": "keyword"
            },

            "domain": {
                "type": "keyword"
            },

            "author": {
                "type": "keyword"
            },

            "vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

def create_index():
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
    es.indices.create(index=ES_INDEX, body=ES_INDEX_BODY)


def search_elasticsearch(query_text, top_k=10, use_synonym=True):
    field = "text_syn" if use_synonym else "text"
    query = {"match": {field: {"query": query_text}}}
    res = es.search(index=ES_INDEX, query=query, size=top_k)
    return [(int(hit["_id"]), hit["_score"], i+1) for i, hit in enumerate(res["hits"]["hits"])]