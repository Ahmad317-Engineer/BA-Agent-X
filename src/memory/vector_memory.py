"""
Vector Memory System - Pure Python implementation (no PyTorch required)
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import Counter

class VectorMemory:
    """Pure Python vector database - no external ML dependencies"""
    
    def __init__(self, collection_name: str = "ba_knowledge", persist_dir: str = "./data/vectordb"):
        self.collection_name = collection_name
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.documents = {}
        
        # TF-IDF style word frequencies
        self.idf_cache = {}
        
        # Load existing data
        self._load_index()
        print(f"✅ VectorMemory initialized (pure Python mode)")
    
    def _load_index(self):
        """Load existing index from disk"""
        index_file = self.persist_dir / f"{self.collection_name}_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.documents = data.get('documents', {})
                print(f"✅ Loaded {len(self.documents)} documents from cache")
    
    def _save_index(self):
        """Save index to disk"""
        index_file = self.persist_dir / f"{self.collection_name}_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            # Don't save embeddings to save space
            docs_to_save = {}
            for doc_id, doc in self.documents.items():
                docs_to_save[doc_id] = {
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'word_freq': doc.get('word_freq', {})
                }
            json.dump({'documents': docs_to_save}, f, indent=2)
    
    def _get_word_freq(self, text: str) -> Dict[str, int]:
        """Get word frequency in text (simple bag-of-words)"""
        words = text.lower().split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return dict(Counter(words))
    
    def _compute_similarity(self, query: str, doc_text: str) -> float:
        """Compute simple similarity using word overlap"""
        query_words = set(query.lower().split())
        doc_words = set(doc_text.lower().split())
        
        if not query_words or not doc_words:
            return 0.0
        
        # Jaccard similarity
        intersection = query_words.intersection(doc_words)
        union = query_words.union(doc_words)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the store"""
        doc_id = hashlib.md5(content.encode()).hexdigest()[:16]
        
        self.documents[doc_id] = {
            'content': content,
            'metadata': metadata,
            'word_freq': self._get_word_freq(content),
            'timestamp': str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else ""
        }
        
        self._save_index()
        print(f"📄 Added: {metadata.get('title', 'Untitled')[:50]}")
        return doc_id
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.documents:
            return []
        
        results = []
        for doc_id, doc in self.documents.items():
            similarity = self._compute_similarity(query, doc['content'])
            results.append({
                'id': doc_id,
                'content': doc['content'],
                'metadata': doc['metadata'],
                'similarity': similarity
            })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:n_results]
    
    def delete_document(self, doc_id: str):
        """Delete a document"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_index()
            print(f"🗑️ Deleted: {doc_id}")
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        return [{'id': doc_id, **doc} for doc_id, doc in self.documents.items()]

# Test
if __name__ == "__main__":
    print("Testing Vector Memory (Pure Python)...")
    vm = VectorMemory("test")
    vm.add_document("User authentication and login system", {"title": "Auth"})
    vm.add_document("Inventory tracking for warehouse", {"title": "Inventory"})
    
    results = vm.search("login")
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r['metadata']['title']}: {r['similarity']:.3f}")
