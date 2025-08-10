#!/usr/bin/env python3
"""
Fuzzy Medicine Search Module
Provides fuzzy matching capabilities for medicine names without modifying existing code.
This is a standalone module that can be safely added alongside existing functionality.
"""

import re
import sqlite3
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz, process
from medicine_database_manager import MedicineDatabaseManager

class FuzzyMedicineSearch:
    """
    Standalone fuzzy search for medicine names.
    Safe to use alongside existing exact search functionality.
    """
    
    def __init__(self, db_path: str = "medicines.db"):
        """Initialize fuzzy search with database connection."""
        self.db_path = db_path
        self.db_manager = MedicineDatabaseManager(db_path)
        self._medicine_cache = None
        self._cache_valid = False
        
    def _normalize_name(self, name: str) -> str:
        """
        Normalize medicine name for better matching.
        
        Args:
            name (str): Raw medicine name
            
        Returns:
            str: Normalized name
        """
        if not name:
            return ""
            
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove dosage information (500mg, 10ml, etc.)
        dosage_patterns = [
            r'\d+\s*mg\b',
            r'\d+\s*ml\b', 
            r'\d+\s*g\b',
            r'\d+\s*mcg\b',
            r'\d+\s*tablets?\b',
            r'\d+\s*capsules?\b',
            r'\d+\s*tab\b',
            r'\d+\s*cap\b'
        ]
        
        for pattern in dosage_patterns:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Remove extra spaces and special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Handle common abbreviations
        abbreviations = {
            'tab': 'tablet',
            'tabs': 'tablets', 
            'cap': 'capsule',
            'caps': 'capsules',
            'paracet': 'paracetamol',
            'ibupro': 'ibuprofen'
        }
        
        for abbrev, full in abbreviations.items():
            if normalized == abbrev or normalized.startswith(abbrev + ' '):
                normalized = normalized.replace(abbrev, full, 1)
        
        return normalized
    
    def _load_medicine_names(self) -> List[Dict]:
        """
        Load all medicine names from database for fuzzy matching.
        
        Returns:
            List[Dict]: List of medicine records with names
        """
        if self._cache_valid and self._medicine_cache:
            return self._medicine_cache
            
        try:
            if not self.db_manager.connect():
                return []
                
            # Get all medicines from database
            cursor = self.db_manager.cursor
            cursor.execute("""
                SELECT name, generic_name, manufacturer, class, price, stock_quantity
                FROM medicines 
                WHERE name IS NOT NULL AND name != ''
            """)
            
            medicines = []
            for row in cursor.fetchall():
                medicines.append({
                    'name': row[0],
                    'generic_name': row[1] or '',
                    'manufacturer': row[2] or '',
                    'class': row[3] or '',
                    'price': row[4] or 0,
                    'stock_quantity': row[5] or 0,
                    'normalized_name': self._normalize_name(row[0])
                })
            
            self._medicine_cache = medicines
            self._cache_valid = True
            
            return medicines
            
        except Exception as e:
            print(f"Error loading medicine names: {e}")
            return []
        finally:
            if self.db_manager.conn:
                self.db_manager.close()
    
    def search_fuzzy(self, query: str, limit: int = 5, min_score: int = 60) -> List[Dict]:
        """
        Perform fuzzy search for medicine names.
        
        Args:
            query (str): Search query (medicine name)
            limit (int): Maximum number of results to return
            min_score (int): Minimum similarity score (0-100)
            
        Returns:
            List[Dict]: List of matching medicines with similarity scores
        """
        if not query or not query.strip():
            return []
        
        # Normalize the search query
        normalized_query = self._normalize_name(query)
        if not normalized_query:
            return []
        
        # Load all medicine names
        medicines = self._load_medicine_names()
        if not medicines:
            return []
        
        # Perform fuzzy matching
        matches = []
        
        for medicine in medicines:
            # Calculate similarity scores using different algorithms
            name_score = fuzz.ratio(normalized_query, medicine['normalized_name'])
            partial_score = fuzz.partial_ratio(normalized_query, medicine['normalized_name'])
            token_score = fuzz.token_sort_ratio(normalized_query, medicine['normalized_name'])
            
            # Use the highest score
            best_score = max(name_score, partial_score, token_score)
            
            # Also check against generic name if available
            if medicine['generic_name']:
                normalized_generic = self._normalize_name(medicine['generic_name'])
                generic_score = fuzz.ratio(normalized_query, normalized_generic)
                best_score = max(best_score, generic_score)
            
            # Add to matches if above minimum score
            if best_score >= min_score:
                matches.append({
                    'name': medicine['name'],
                    'generic_name': medicine['generic_name'],
                    'manufacturer': medicine['manufacturer'],
                    'class': medicine['class'],
                    'price': medicine['price'],
                    'stock_quantity': medicine['stock_quantity'],
                    'similarity_score': best_score,
                    'match_type': 'fuzzy'
                })
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return matches[:limit]
    
    def search_with_suggestions(self, query: str, limit: int = 5) -> Dict:
        """
        Enhanced search with suggestions and confidence levels.
        
        Args:
            query (str): Search query
            limit (int): Maximum results
            
        Returns:
            Dict: Search results with metadata
        """
        # First try exact match (using existing database functionality)
        exact_matches = []
        try:
            if self.db_manager.connect():
                db_info = self.db_manager.get_medicine_info(query)
                if db_info:
                    exact_matches.append({
                        'name': db_info['name'],
                        'generic_name': db_info['generic_name'],
                        'manufacturer': db_info['manufacturer'],
                        'class': db_info['class'],
                        'price': db_info['price'],
                        'stock_quantity': db_info['stock_quantity'],
                        'similarity_score': 100,
                        'match_type': 'exact'
                    })
        except:
            pass
        finally:
            if self.db_manager.conn:
                self.db_manager.close()
        
        # If exact match found, return it first
        if exact_matches:
            fuzzy_matches = self.search_fuzzy(query, limit - 1, min_score=60)
            all_matches = exact_matches + fuzzy_matches
        else:
            # No exact match, get fuzzy matches
            all_matches = self.search_fuzzy(query, limit, min_score=60)
        
        # Determine confidence level
        confidence = "high" if exact_matches else "medium" if all_matches else "low"
        
        return {
            'query': query,
            'normalized_query': self._normalize_name(query),
            'matches': all_matches[:limit],
            'total_found': len(all_matches),
            'confidence': confidence,
            'has_exact_match': len(exact_matches) > 0,
            'suggestions': [match['name'] for match in all_matches[:3]]
        }
    
    def get_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions for autocomplete.
        
        Args:
            partial_query (str): Partial medicine name
            limit (int): Maximum suggestions
            
        Returns:
            List[str]: List of suggested medicine names
        """
        if len(partial_query) < 2:  # Too short for meaningful suggestions
            return []
        
        medicines = self._load_medicine_names()
        suggestions = []
        
        normalized_query = self._normalize_name(partial_query)
        
        for medicine in medicines:
            # Check if medicine name starts with the query
            if medicine['normalized_name'].startswith(normalized_query):
                suggestions.append(medicine['name'])
            # Also check partial matches
            elif normalized_query in medicine['normalized_name']:
                suggestions.append(medicine['name'])
        
        # Remove duplicates and sort
        suggestions = list(set(suggestions))
        suggestions.sort()
        
        return suggestions[:limit]

# Convenience function for easy integration
def search_medicine_fuzzy(query: str, limit: int = 5) -> Dict:
    """
    Convenience function for fuzzy medicine search.
    
    Args:
        query (str): Medicine name to search
        limit (int): Maximum results
        
    Returns:
        Dict: Search results
    """
    searcher = FuzzyMedicineSearch()
    return searcher.search_with_suggestions(query, limit)

# Test function
def test_fuzzy_search():
    """Test the fuzzy search functionality."""
    print("🧪 Testing Fuzzy Medicine Search...")
    
    test_queries = [
        "paracetamol",      # Exact match
        "paracetmol",       # Typo
        "paracet",          # Partial
        "paracetamol 500mg", # With dosage
        "ibuprofen",        # Another exact
        "ibuprofn",         # Typo
        "tylenol",          # Brand name (might not be in DB)
        "xyz123"            # Non-existent
    ]
    
    searcher = FuzzyMedicineSearch()
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = searcher.search_with_suggestions(query, 3)
        
        print(f"  Confidence: {results['confidence']}")
        print(f"  Found {results['total_found']} matches")
        
        for i, match in enumerate(results['matches'], 1):
            print(f"  {i}. {match['name']} (Score: {match['similarity_score']}%, Type: {match['match_type']})")

if __name__ == "__main__":
    test_fuzzy_search() 