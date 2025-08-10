#!/usr/bin/env python3
"""
Medicine Database Manager
Handles database operations for finding cost-effective alternatives.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
import json

class MedicineDatabaseManager:
    """Manages medicine database operations for finding alternatives."""
    
    def __init__(self, db_path: str = "medicines.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
            
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def get_medicine_info(self, medicine_name: str) -> Optional[Dict]:
        """Get medicine information from database."""
        try:
            # Try exact match first
            self.cursor.execute("""
                SELECT name, class, price, stock_quantity, generic_name, manufacturer
                FROM medicines 
                WHERE LOWER(name) = LOWER(?)
                LIMIT 1
            """, (medicine_name,))
            
            result = self.cursor.fetchone()
            if result:
                return {
                    "name": result[0],
                    "class": result[1],
                    "price": result[2],
                    "stock_quantity": result[3],
                    "generic_name": result[4],
                    "manufacturer": result[5]
                }
            
            # Try partial match
            self.cursor.execute("""
                SELECT name, class, price, stock_quantity, generic_name, manufacturer
                FROM medicines 
                WHERE LOWER(name) LIKE LOWER(?)
                LIMIT 1
            """, (f"%{medicine_name}%",))
            
            result = self.cursor.fetchone()
            if result:
                return {
                    "name": result[0],
                    "class": result[1],
                    "price": result[2],
                    "stock_quantity": result[3],
                    "generic_name": result[4],
                    "manufacturer": result[5]
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting medicine info: {e}")
            return None
    
    def get_medicines_by_generic(self, generic_name: str, min_stock: int = 10) -> List[Dict]:
        """Get all medicines with the same generic name and sufficient stock."""
        try:
            self.cursor.execute("""
                SELECT name, price, stock_quantity, generic_name, manufacturer, class
                FROM medicines 
                WHERE generic_name = ? AND stock_quantity >= ?
                ORDER BY price ASC
            """, (generic_name, min_stock))
            
            medicines = []
            for row in self.cursor.fetchall():
                medicines.append({
                    "name": row[0],
                    "price": row[1],
                    "stock_quantity": row[2],
                    "generic_name": row[3],
                    "manufacturer": row[4],
                    "class": row[5]
                })
            
            return medicines
            
        except Exception as e:
            print(f"❌ Error getting medicines by generic: {e}")
            return []
    
    def find_cheapest_alternatives(self, medicine_name: str, generic_name: str, 
                                 original_price: float, quantity_needed: str, 
                                 min_stock: int = 10, limit: int = 3) -> List[Dict]:
        """Find cheapest alternatives with the same generic name."""
        try:
            # Get all medicines with the same generic name and sufficient stock
            medicines = self.get_medicines_by_generic(generic_name, min_stock)
            
            # Filter out the original medicine and sort by price
            alternatives = []
            for medicine in medicines:
                # Skip if it's the same medicine (case-insensitive)
                if medicine["name"].lower() != medicine_name.lower():
                    alternatives.append(medicine)
            
            # Sort by price (ascending) and filter only cheaper alternatives
            alternatives.sort(key=lambda x: x["price"])
            
            # Filter only alternatives that are cheaper than original
            cheaper_alternatives = []
            for alt in alternatives:
                if alt["price"] < original_price:
                    cheaper_alternatives.append(alt)
            
            # Take top alternatives (up to limit, but only if they're cheaper)
            top_alternatives = cheaper_alternatives[:limit]
            
            # Calculate savings for each alternative
            for alt in top_alternatives:
                savings_amount = original_price - alt["price"]
                savings_percent = (savings_amount / original_price) * 100 if original_price > 0 else 0
                
                # Calculate total savings based on quantity needed
                quantity_number = self.extract_quantity_number(quantity_needed)
                total_savings = savings_amount * quantity_number
                
                alt["savings_amount"] = round(savings_amount, 2)
                alt["savings_percent"] = round(savings_percent, 1)
                alt["total_savings"] = round(total_savings, 2)
                alt["quantity_needed"] = quantity_needed
            
            return top_alternatives
            
        except Exception as e:
            print(f"❌ Error finding alternatives: {e}")
            return []
    
    def get_market_price_estimate(self, medicine_name: str, generic_name: str) -> float:
        """Estimate market price based on generic average."""
        try:
            self.cursor.execute("""
                SELECT AVG(price) as avg_price
                FROM medicines 
                WHERE generic_name = ?
            """, (generic_name,))
            
            result = self.cursor.fetchone()
            if result and result[0]:
                return round(result[0], 2)
            else:
                # Default price if no data available
                return 25.0
                
        except Exception as e:
            print(f"❌ Error getting market price: {e}")
            return 25.0
    
    def extract_quantity_number(self, quantity_str: str) -> int:
        """Extract numeric quantity from quantity string."""
        import re
        try:
            # Extract numbers from quantity string (e.g., "10 tablets" -> 10)
            numbers = re.findall(r'\d+', quantity_str)
            if numbers:
                return int(numbers[0])
            return 1  # Default to 1 if no number found
        except:
            return 1
    
    def check_stock_availability(self, medicine_name: str, required_quantity: int) -> bool:
        """Check if medicine has sufficient stock."""
        try:
            self.cursor.execute("""
                SELECT stock_quantity
                FROM medicines 
                WHERE LOWER(name) = LOWER(?)
                LIMIT 1
            """, (medicine_name,))
            
            result = self.cursor.fetchone()
            if result:
                return result[0] >= required_quantity
            return False
            
        except Exception as e:
            print(f"❌ Error checking stock: {e}")
            return False 