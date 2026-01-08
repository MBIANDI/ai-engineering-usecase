import chromadb
from chromadb.utils import embedding_functions
# Define embedding function
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
# Create client
client = chromadb.Client()

# Create collection with embedding function
collection = client.create_collection(
    name="my_collection_name",
    metadata={"topic": "query testing"},
    configuration={
        "hnsw": {
            "space": "cosine",    # Distance metric
        },
        "embedding_function": ef
    }
)

collection.add(
    documents=[
        "Document text 1",
        "Document text 2"
    ],
    metadatas=[
        {"source": "source1", "category": "type1"},
        {"source": "source2", "category": "type2"}
    ],
    ids=["id1", "id2"]
)

# Get all documents
all_items = collection.get()
# Get with metadata filter
filtered_items = collection.get(
    where={"source": "source1"}
)

# Basic equality
where={"key": "value"}
# Equivalent to
where={"key": {"$eq": "value"}}
# Comparison operators
"$eq"   # equal to (string, int, float)
"$ne"   # not equal to
"$gt"   # greater than (int, float)
"$gte"  # greater than or equal to
"$lt"   # less than (int, float)
"$lte"  # less than or equal to
"$in"   # in list
"$nin"  # not in list

# AND operation; you can replace `$and` with `$or` to make this an OR operation
collection.get(
    where={
        "$and": [
            {"source": {"$eq": "langchain.com"}}, 
            {"version": {"$lt": 0.3}}
        ]
    }
)
# Using a list to perform an OR operation on the values of a metadata key
collection.get(
    where={
        "$and": [
            {"source": {"$in": ["langchain.com", "llamaindex.ai"]}}, 
            {"version": {"$lt": 0.3}}
        ]
    }
)

# Contains text
where_document={"$contains": "pandas"}
# Does not contain text
where_document={"$not_contains": "library"}
# Combined with logical operators
where_document={
    "$or": [
        {"$contains": "LangChain"},
        {"$contains": "Python"}
    ]
}
# With metadata filter
results = collection.query(
    query_texts=["polar bear"],
    n_results=1,
    where={'topic': 'animals'}
)
# With document filter
results = collection.query(
    query_texts=["polar bear"],
    n_results=1,
    where_document={'$not_contains': 'library'}
)
# Combined filters
results = collection.query(
    query_texts=["polar bear"],
    n_results=1,
    where={'topic': 'animals'},
    where_document={'$not_contains': 'library'}
)