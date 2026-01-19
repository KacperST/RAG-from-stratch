from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

QDRANT_HOST = "http://localhost:6333"
COLLECTION_NAME = "culturax_semantic"

client = QdrantClient(url=QDRANT_HOST)
model = SentenceTransformer('intfloat/multilingual-e5-small', device='cpu')

def search_qdrant(query_text, top_k=20, filters=None):
    query_vector = model.encode(query_text).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    return [(hit.id, hit.score, rank+1) for rank, hit in enumerate(results.points)]