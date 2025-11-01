"""Document storage with embeddings and metadata"""
import json
import os
import time
from typing import Dict, List, Optional
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class DocumentStore:
    """Document storage with TF-IDF embeddings and metadata support"""
    
    def __init__(self, storage_path: str = 'knowledge_base'):
        """
        Initialize document store
        
        Args:
            storage_path: Directory path for storing documents
        """
        self.storage_path = storage_path
        self.documents = {}  # doc_id -> {content, metadata, embedding, timestamp}
        self.vectorizer = None
        self.doc_matrix = None
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
        # Try to load existing data
        self.load()
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None) -> bool:
        """
        Add a document to the store
        
        Args:
            doc_id: Unique document identifier
            content: Document text content
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not content:
                return False
                
            embedding = self.compute_embedding(content)
            
            self.documents[doc_id] = {
                'content': content,
                'metadata': metadata or {},
                'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                'timestamp': time.time()
            }
            
            # Rebuild vectorizer with new documents
            self._rebuild_vectorizer()
            
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Dict:
        """
        Get a document by ID
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document dictionary or empty dict if not found
        """
        return self.documents.get(doc_id, {})
    
    def update_document(self, doc_id: str, content: str, metadata: Dict = None) -> bool:
        """
        Update an existing document
        
        Args:
            doc_id: Document identifier
            content: New content
            metadata: Optional metadata (merged with existing)
            
        Returns:
            True if successful, False otherwise
        """
        if doc_id not in self.documents:
            return False
        
        try:
            # Merge metadata if provided
            existing_metadata = self.documents[doc_id].get('metadata', {})
            if metadata:
                existing_metadata.update(metadata)
            
            embedding = self.compute_embedding(content)
            
            self.documents[doc_id] = {
                'content': content,
                'metadata': existing_metadata,
                'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                'timestamp': time.time()
            }
            
            # Rebuild vectorizer
            self._rebuild_vectorizer()
            
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if successful, False otherwise
        """
        if doc_id not in self.documents:
            return False
        
        del self.documents[doc_id]
        self._rebuild_vectorizer()
        return True
    
    def list_documents(self, limit: int = 100) -> List[Dict]:
        """
        List all documents with their metadata
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of document dictionaries
        """
        result = []
        for doc_id, doc_data in list(self.documents.items())[:limit]:
            result.append({
                'doc_id': doc_id,
                'content': doc_data['content'],
                'metadata': doc_data['metadata'],
                'timestamp': doc_data['timestamp']
            })
        return result
    
    def compute_embedding(self, text: str) -> np.ndarray:
        """
        Compute embedding for text using TF-IDF
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if not text:
            return np.array([])
        
        if SKLEARN_AVAILABLE:
            # Use TF-IDF vectorizer
            if self.vectorizer is None:
                # Create new vectorizer if none exists
                self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
                try:
                    self.vectorizer.fit([text])
                except:
                    # If single text fails, use simple fallback
                    return self._simple_embedding(text)
            
            try:
                vec = self.vectorizer.transform([text])
                return vec.toarray()[0]
            except:
                return self._simple_embedding(text)
        else:
            # Fallback to simple word count embedding
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Simple word-based embedding as fallback"""
        words = text.lower().split()
        # Simple frequency-based embedding (first 100 unique words)
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Convert to fixed-size vector
        unique_words = sorted(word_freq.keys())[:100]
        embedding = [word_freq.get(w, 0) for w in unique_words]
        
        # Pad to length 100
        while len(embedding) < 100:
            embedding.append(0)
        
        return np.array(embedding[:100], dtype=float)
    
    def _rebuild_vectorizer(self):
        """Rebuild TF-IDF vectorizer with all documents"""
        if not SKLEARN_AVAILABLE or not self.documents:
            return
        
        try:
            all_contents = [doc['content'] for doc in self.documents.values()]
            if all_contents:
                self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
                self.doc_matrix = self.vectorizer.fit_transform(all_contents)
        except Exception as e:
            print(f"Warning: Could not rebuild vectorizer: {e}")
    
    def get_similar_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find documents similar to query using cosine similarity
        
        Args:
            query: Query text
            top_k: Number of top results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        if not query or not self.documents:
            return []
        
        try:
            query_embedding = self.compute_embedding(query)
            
            if query_embedding.size == 0:
                return []
            
            similarities = []
            
            if SKLEARN_AVAILABLE and self.doc_matrix is not None:
                # Use sklearn for efficient similarity computation
                try:
                    query_vec = self.vectorizer.transform([query])
                    sims = cosine_similarity(query_vec, self.doc_matrix)[0]
                    
                    for idx, (doc_id, doc_data) in enumerate(self.documents.items()):
                        similarities.append({
                            'doc_id': doc_id,
                            'content': doc_data['content'],
                            'metadata': doc_data['metadata'],
                            'similarity': float(sims[idx])
                        })
                except:
                    # Fallback to manual computation
                    similarities = self._manual_similarity(query_embedding)
            else:
                # Manual cosine similarity computation
                similarities = self._manual_similarity(query_embedding)
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def _manual_similarity(self, query_embedding: np.ndarray) -> List[Dict]:
        """Manually compute cosine similarity"""
        similarities = []
        
        for doc_id, doc_data in self.documents.items():
            doc_embedding = np.array(doc_data['embedding'])
            
            # Ensure same dimensions
            min_len = min(len(query_embedding), len(doc_embedding))
            if min_len == 0:
                continue
                
            q_vec = query_embedding[:min_len]
            d_vec = doc_embedding[:min_len]
            
            # Cosine similarity
            dot_product = np.dot(q_vec, d_vec)
            q_norm = np.linalg.norm(q_vec)
            d_norm = np.linalg.norm(d_vec)
            
            if q_norm > 0 and d_norm > 0:
                similarity = dot_product / (q_norm * d_norm)
            else:
                similarity = 0.0
            
            similarities.append({
                'doc_id': doc_id,
                'content': doc_data['content'],
                'metadata': doc_data['metadata'],
                'similarity': float(similarity)
            })
        
        return similarities
    
    def save(self) -> bool:
        """
        Save documents to disk
        
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.storage_path, 'documents.json')
            with open(filepath, 'w') as f:
                json.dump(self.documents, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving documents: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load documents from disk
        
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.storage_path, 'documents.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.documents = json.load(f)
                
                # Rebuild vectorizer with loaded documents
                self._rebuild_vectorizer()
                return True
            return False
        except Exception as e:
            print(f"Error loading documents: {e}")
            return False
