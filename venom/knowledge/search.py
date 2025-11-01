"""Advanced search engine with ranking"""
import re
from typing import Dict, List, Set
from collections import defaultdict
import math


class SearchEngine:
    """Advanced search with inverted index and BM25 ranking"""
    
    def __init__(self, document_store):
        """
        Initialize search engine
        
        Args:
            document_store: DocumentStore instance
        """
        self.document_store = document_store
        self.inverted_index = defaultdict(lambda: defaultdict(list))  # term -> {doc_id: [positions]}
        self.doc_lengths = {}  # doc_id -> document length
        self.avg_doc_length = 0
        self.build_index()
    
    def build_index(self) -> None:
        """Build inverted index from document store"""
        self.inverted_index.clear()
        self.doc_lengths.clear()
        
        total_length = 0
        doc_count = 0
        
        for doc_id, doc_data in self.document_store.documents.items():
            content = doc_data['content'].lower()
            terms = self._tokenize(content)
            
            self.doc_lengths[doc_id] = len(terms)
            total_length += len(terms)
            doc_count += 1
            
            # Build inverted index with positions
            for position, term in enumerate(terms):
                self.inverted_index[term][doc_id].append(position)
        
        # Calculate average document length
        self.avg_doc_length = total_length / doc_count if doc_count > 0 else 0
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into terms
        
        Args:
            text: Input text
            
        Returns:
            List of terms
        """
        # Simple word tokenization
        text = text.lower()
        # Keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        terms = text.split()
        return [t for t in terms if len(t) > 1]  # Filter single characters
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search documents with BM25 ranking
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of ranked documents
        """
        if not query:
            return []
        
        query_terms = self._tokenize(query)
        if not query_terms:
            return []
        
        # Find matching documents
        matching_docs = set()
        for term in query_terms:
            if term in self.inverted_index:
                matching_docs.update(self.inverted_index[term].keys())
        
        if not matching_docs:
            return []
        
        # Score and rank documents
        results = []
        for doc_id in matching_docs:
            doc_data = self.document_store.documents.get(doc_id)
            if doc_data:
                results.append({
                    'doc_id': doc_id,
                    'content': doc_data['content'],
                    'metadata': doc_data['metadata'],
                    'score': 0.0  # Will be computed in ranking
                })
        
        # Rank results
        ranked_results = self.rank_results(results, query)
        
        return ranked_results[:top_k]
    
    def boolean_search(self, query: str) -> List[Dict]:
        """
        Boolean search with AND, OR, NOT operators
        
        Args:
            query: Boolean query (e.g., "term1 AND term2 OR term3 NOT term4")
            
        Returns:
            List of matching documents
        """
        # Parse boolean query
        query = query.upper()
        
        # Split by OR first (lowest precedence)
        or_parts = re.split(r'\s+OR\s+', query)
        
        all_results = set()
        
        for or_part in or_parts:
            # Split by AND
            and_parts = re.split(r'\s+AND\s+', or_part)
            
            and_results = None
            
            for and_part in and_parts:
                # Check for NOT
                if 'NOT' in and_part:
                    not_parts = re.split(r'\s+NOT\s+', and_part)
                    positive_term = not_parts[0].strip().lower()
                    negative_terms = [t.strip().lower() for t in not_parts[1:]]
                    
                    # Get docs with positive term
                    positive_docs = set()
                    term_tokens = self._tokenize(positive_term)
                    for token in term_tokens:
                        if token in self.inverted_index:
                            positive_docs.update(self.inverted_index[token].keys())
                    
                    # Remove docs with negative terms
                    for neg_term in negative_terms:
                        neg_tokens = self._tokenize(neg_term)
                        for token in neg_tokens:
                            if token in self.inverted_index:
                                positive_docs -= set(self.inverted_index[token].keys())
                    
                    part_results = positive_docs
                else:
                    # Regular term
                    term = and_part.strip().lower()
                    term_tokens = self._tokenize(term)
                    part_results = set()
                    for token in term_tokens:
                        if token in self.inverted_index:
                            part_results.update(self.inverted_index[token].keys())
                
                # AND operation
                if and_results is None:
                    and_results = part_results
                else:
                    and_results &= part_results
            
            # OR operation
            if and_results:
                all_results |= and_results
        
        # Build result list
        results = []
        for doc_id in all_results:
            doc_data = self.document_store.documents.get(doc_id)
            if doc_data:
                results.append({
                    'doc_id': doc_id,
                    'content': doc_data['content'],
                    'metadata': doc_data['metadata']
                })
        
        return results
    
    def phrase_search(self, phrase: str) -> List[Dict]:
        """
        Search for exact phrase
        
        Args:
            phrase: Phrase to search for
            
        Returns:
            List of documents containing the phrase
        """
        if not phrase:
            return []
        
        phrase_terms = self._tokenize(phrase)
        if not phrase_terms:
            return []
        
        # Get documents containing all terms
        first_term = phrase_terms[0]
        if first_term not in self.inverted_index:
            return []
        
        candidate_docs = set(self.inverted_index[first_term].keys())
        
        # Filter to docs containing all terms
        for term in phrase_terms[1:]:
            if term in self.inverted_index:
                candidate_docs &= set(self.inverted_index[term].keys())
            else:
                return []
        
        # Check for exact phrase in candidates
        results = []
        for doc_id in candidate_docs:
            if self._contains_phrase(doc_id, phrase_terms):
                doc_data = self.document_store.documents.get(doc_id)
                if doc_data:
                    results.append({
                        'doc_id': doc_id,
                        'content': doc_data['content'],
                        'metadata': doc_data['metadata']
                    })
        
        return results
    
    def _contains_phrase(self, doc_id: str, terms: List[str]) -> bool:
        """Check if document contains exact phrase"""
        if not terms:
            return False
        
        # Get positions of first term
        first_positions = self.inverted_index[terms[0]].get(doc_id, [])
        
        for start_pos in first_positions:
            # Check if subsequent terms follow in sequence
            match = True
            for i, term in enumerate(terms[1:], 1):
                expected_pos = start_pos + i
                term_positions = self.inverted_index[term].get(doc_id, [])
                if expected_pos not in term_positions:
                    match = False
                    break
            
            if match:
                return True
        
        return False
    
    def filter_by_metadata(self, filters: Dict) -> List[Dict]:
        """
        Filter documents by metadata
        
        Args:
            filters: Dictionary of metadata key-value pairs
            
        Returns:
            List of matching documents
        """
        if not filters:
            return []
        
        results = []
        
        for doc_id, doc_data in self.document_store.documents.items():
            metadata = doc_data.get('metadata', {})
            
            # Check if all filters match
            match = True
            for key, value in filters.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                results.append({
                    'doc_id': doc_id,
                    'content': doc_data['content'],
                    'metadata': metadata
                })
        
        return results
    
    def rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rank results using BM25 algorithm
        
        Args:
            results: List of document results
            query: Query string
            
        Returns:
            Ranked list of documents
        """
        if not results or not query:
            return results
        
        query_terms = self._tokenize(query)
        if not query_terms:
            return results
        
        # BM25 parameters
        k1 = 1.5
        b = 0.75
        
        N = len(self.document_store.documents)  # Total documents
        
        for result in results:
            doc_id = result['doc_id']
            score = 0.0
            
            doc_length = self.doc_lengths.get(doc_id, 0)
            if doc_length == 0:
                continue
            
            for term in query_terms:
                if term not in self.inverted_index:
                    continue
                
                # Term frequency in document
                tf = len(self.inverted_index[term].get(doc_id, []))
                
                # Document frequency
                df = len(self.inverted_index[term])
                
                # IDF calculation
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
                
                # BM25 score component
                numerator = tf * (k1 + 1)
                # Prevent division by zero
                if self.avg_doc_length > 0:
                    denominator = tf + k1 * (1 - b + b * (doc_length / self.avg_doc_length))
                else:
                    denominator = tf + k1
                
                score += idf * (numerator / denominator)
            
            result['score'] = score
        
        # Sort by score descending
        results.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        return results
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the index
        
        Returns:
            Dictionary with index statistics
        """
        total_terms = len(self.inverted_index)
        total_docs = len(self.doc_lengths)
        
        # Calculate total postings
        total_postings = sum(
            len(doc_positions)
            for term_docs in self.inverted_index.values()
            for doc_positions in term_docs.values()
        )
        
        return {
            'total_terms': total_terms,
            'total_documents': total_docs,
            'total_postings': total_postings,
            'avg_doc_length': self.avg_doc_length
        }
