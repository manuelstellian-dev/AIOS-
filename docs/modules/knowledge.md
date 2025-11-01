# Knowledge Management Module

The Knowledge module provides document storage, semantic search, and knowledge graph capabilities.

## Components

### Document Store

Store and manage documents with metadata.

```python
from venom.knowledge import DocumentStore

# Initialize store
store = DocumentStore()

# Add document
doc_id = store.add_document(
    content="VENOM is a universal AI operating system with comprehensive features",
    metadata={
        "title": "VENOM Overview",
        "category": "documentation",
        "version": "1.0.0",
        "author": "VENOM Team",
        "created_at": "2024-11-01"
    }
)

# Retrieve document
document = store.get_document(doc_id)
print(f"Title: {document['metadata']['title']}")
print(f"Content: {document['content']}")

# Update document
store.update_document(
    doc_id,
    metadata={"version": "1.0.1"}
)

# Delete document
store.delete_document(doc_id)

# List all documents
all_docs = store.list_documents()

# Search by metadata
results = store.search_by_metadata({"category": "documentation"})
```

### Semantic Search

Find relevant documents using semantic similarity.

```python
from venom.knowledge import SemanticSearch

# Initialize search engine
search = SemanticSearch()

# Search for documents
results = search.search(
    query="How do I deploy to the cloud?",
    top_k=5,
    threshold=0.7  # Minimum similarity score
)

# Process results
for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Document: {result['doc_id']}")
    print(f"Content: {result['content'][:100]}...")
    print()

# Search with filters
results = search.search(
    query="security features",
    top_k=10,
    filters={"category": "security", "version": "1.0.0"}
)

# Get similar documents
similar = search.find_similar(doc_id="doc_123", top_k=5)
```

### Knowledge Graph

Build and query knowledge graphs with relationships.

```python
from venom.knowledge import KnowledgeGraph

# Initialize graph
graph = KnowledgeGraph()

# Add nodes
graph.add_node(
    node_id="ai",
    properties={
        "name": "Artificial Intelligence",
        "type": "concept",
        "description": "Computer systems that simulate human intelligence"
    }
)

graph.add_node(
    node_id="ml",
    properties={
        "name": "Machine Learning",
        "type": "concept",
        "description": "Subset of AI that learns from data"
    }
)

graph.add_node(
    node_id="dl",
    properties={
        "name": "Deep Learning",
        "type": "concept",
        "description": "ML using neural networks"
    }
)

# Add relationships
graph.add_edge(
    source="ai",
    target="ml",
    properties={"relation": "includes", "strength": 1.0}
)

graph.add_edge(
    source="ml",
    target="dl",
    properties={"relation": "includes", "strength": 0.9}
)

# Query graph
neighbors = graph.get_neighbors("ai")
print(f"AI includes: {neighbors}")

# Find path
path = graph.find_path("ai", "dl")
print(f"Path from AI to DL: {path}")

# Get subgraph
subgraph = graph.get_subgraph("ai", depth=2)

# Traverse graph
def visit_node(node_id, properties):
    print(f"Visiting: {properties['name']}")

graph.traverse(start_node="ai", visit_fn=visit_node)

# Query by properties
results = graph.query_nodes({"type": "concept"})
```

## CLI Usage

```bash
# Add document
venom knowledge add --doc ./docs/guide.md --metadata '{"category":"guide"}'

# Add multiple documents
venom knowledge add --doc ./docs/api.md --metadata '{"category":"api"}'
venom knowledge add --doc ./docs/tutorial.md --metadata '{"category":"tutorial"}'

# Search knowledge base
venom knowledge search --query "deployment guide"

# Search with specific terms
venom knowledge search --query "security encryption features"
```

## Configuration

Add to `~/.venomrc`:

```json
{
  "knowledge": {
    "storage_path": "~/.venom/knowledge",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "index_type": "faiss",
    "similarity_threshold": 0.7,
    "max_results": 10,
    "graph": {
      "backend": "networkx",
      "max_depth": 5
    }
  }
}
```

## Advanced Usage

### Building a Knowledge Base

```python
from venom.knowledge import DocumentStore, SemanticSearch, KnowledgeGraph

# Initialize components
store = DocumentStore()
search = SemanticSearch()
graph = KnowledgeGraph()

# Add documents
docs = [
    ("VENOM supports AWS, GCP, and Azure deployment", {"topic": "cloud"}),
    ("Security features include AES-256-GCM encryption", {"topic": "security"}),
    ("AutoML provides hyperparameter tuning", {"topic": "ml"})
]

doc_ids = []
for content, metadata in docs:
    doc_id = store.add_document(content, metadata)
    doc_ids.append(doc_id)

# Build knowledge graph from documents
for i, doc_id in enumerate(doc_ids):
    graph.add_node(doc_id, {"index": i, "topic": docs[i][1]["topic"]})

# Connect related documents
graph.add_edge(doc_ids[0], doc_ids[1], {"relation": "related"})
graph.add_edge(doc_ids[1], doc_ids[2], {"relation": "related"})

# Query the system
results = search.search("cloud security", top_k=3)
for result in results:
    # Find related documents
    related = graph.get_neighbors(result['doc_id'])
    print(f"Found: {result['content'][:50]}...")
    print(f"Related: {related}")
```

### Document Clustering

```python
from venom.knowledge import DocumentStore, SemanticSearch

store = DocumentStore()
search = SemanticSearch()

# Add documents
doc_ids = []
for doc in my_documents:
    doc_id = store.add_document(doc['content'], doc['metadata'])
    doc_ids.append(doc_id)

# Cluster documents by similarity
clusters = search.cluster_documents(doc_ids, n_clusters=5)

for i, cluster in enumerate(clusters):
    print(f"Cluster {i+1}:")
    for doc_id in cluster:
        doc = store.get_document(doc_id)
        print(f"  - {doc['content'][:50]}...")
```

### Question Answering

```python
from venom.knowledge import DocumentStore, SemanticSearch

store = DocumentStore()
search = SemanticSearch()

# Add knowledge base
for doc in knowledge_base:
    store.add_document(doc['content'], doc['metadata'])

# Answer questions
def answer_question(question: str) -> str:
    # Find relevant documents
    results = search.search(question, top_k=3)
    
    if not results:
        return "No relevant information found."
    
    # Use most relevant document
    best_match = results[0]
    return f"Answer: {best_match['content']}"

# Test
question = "How do I deploy to AWS?"
answer = answer_question(question)
print(answer)
```

## Integration with Other Modules

### With Security

```python
from venom.knowledge import DocumentStore
from venom.security import AdvancedEncryption

store = DocumentStore()
encryption = AdvancedEncryption(algorithm='aes-gcm')

# Encrypt sensitive documents
key = encryption.generate_key(algorithm='aes-gcm')
sensitive_data = b"Confidential information"
encrypted = encryption.encrypt(sensitive_data, key)

# Store encrypted
doc_id = store.add_document(
    encrypted.hex(),  # Store as hex string
    metadata={"encrypted": True, "algorithm": "aes-gcm"}
)

# Retrieve and decrypt
doc = store.get_document(doc_id)
decrypted = encryption.decrypt(bytes.fromhex(doc['content']), key)
```

### With AI/ML

```python
from venom.knowledge import DocumentStore, SemanticSearch
from venom.ml import TransformerBridge

store = DocumentStore()
search = SemanticSearch()
transformer = TransformerBridge(model_name="gpt2")

# Generate document summaries
for doc in documents:
    # Store original
    doc_id = store.add_document(doc['content'], doc['metadata'])
    
    # Generate summary
    summary = transformer.generate_text(
        f"Summarize: {doc['content'][:200]}",
        max_length=50
    )
    
    # Store summary
    store.update_document(
        doc_id,
        metadata={"summary": summary}
    )
```

## Best Practices

1. **Use Metadata**: Add rich metadata for better filtering
2. **Index Documents**: Regularly rebuild search indices
3. **Graph Structure**: Design meaningful relationships
4. **Backup**: Regularly backup knowledge base
5. **Version Control**: Track document versions
6. **Access Control**: Implement permissions for sensitive data

## Examples

See [examples/knowledge/](../examples/) for complete examples.

## API Reference

Full API documentation available at [docs/api/knowledge.md](../api/knowledge.md).
