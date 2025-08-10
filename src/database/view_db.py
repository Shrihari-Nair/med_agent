#!/usr/bin/env python3
"""
Medicine Database Viewer
View and explore the contents of the medicine database.
"""

import sqlite3
import sys
from typing import List, Tuple

class MedicineDatabaseViewer:
    """Viewer for exploring the medicine database."""
    
    def __init__(self, db_path: str = "data/medicines.db"):
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
            
    def get_database_stats(self):
        """Get database statistics."""
        try:
            # Total medicines
            self.cursor.execute("SELECT COUNT(*) FROM medicines")
            total_medicines = self.cursor.fetchone()[0]
            
            # Total classes
            self.cursor.execute("SELECT COUNT(DISTINCT class) FROM medicines")
            total_classes = self.cursor.fetchone()[0]
            
            # Price range
            self.cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM medicines")
            min_price, max_price, avg_price = self.cursor.fetchone()
            
            # Stock range
            self.cursor.execute("SELECT MIN(stock_quantity), MAX(stock_quantity), AVG(stock_quantity) FROM medicines")
            min_stock, max_stock, avg_stock = self.cursor.fetchone()
            
            return {
                "total_medicines": total_medicines,
                "total_classes": total_classes,
                "price_range": (min_price, max_price, avg_price),
                "stock_range": (min_stock, max_stock, avg_stock)
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return None
    
    def show_all_classes(self):
        """Show all medicine classes with counts."""
        try:
            self.cursor.execute("""
                SELECT class, COUNT(*) as count, 
                       MIN(price) as min_price, 
                       MAX(price) as max_price,
                       AVG(price) as avg_price
                FROM medicines 
                GROUP BY class 
                ORDER BY count DESC
            """)
            
            classes = self.cursor.fetchall()
            
            print("\n📊 Medicine Classes Summary:")
            print("=" * 80)
            print(f"{'Class':<20} | {'Count':<6} | {'Min Price':<10} | {'Max Price':<10} | {'Avg Price':<10}")
            print("-" * 80)
            
            for class_name, count, min_price, max_price, avg_price in classes:
                print(f"{class_name:<20} | {count:<6} | ${min_price:<9.2f} | ${max_price:<9.2f} | ${avg_price:<9.2f}")
                
        except Exception as e:
            print(f"❌ Error showing classes: {e}")
    
    def show_medicines_by_class(self, class_name: str, limit: int = 10):
        """Show medicines from a specific class."""
        try:
            self.cursor.execute("""
                SELECT name, stock_quantity, price, generic_name, manufacturer
                FROM medicines 
                WHERE class = ? 
                ORDER BY price ASC
                LIMIT ?
            """, (class_name, limit))
            
            medicines = self.cursor.fetchall()
            
            if not medicines:
                print(f"❌ No medicines found in class: {class_name}")
                return
            
            print(f"\n💊 Medicines in '{class_name}' class (showing top {len(medicines)} by price):")
            print("=" * 100)
            print(f"{'Name':<25} | {'Stock':<6} | {'Price':<8} | {'Generic Name':<20} | {'Manufacturer':<20}")
            print("-" * 100)
            
            for name, stock, price, generic, manufacturer in medicines:
                print(f"{name:<25} | {stock:<6} | ${price:<7.2f} | {generic:<20} | {manufacturer:<20}")
                
        except Exception as e:
            print(f"❌ Error showing medicines by class: {e}")
    
    def search_medicines(self, search_term: str, limit: int = 10):
        """Search medicines by name or generic name."""
        try:
            search_pattern = f"%{search_term}%"
            self.cursor.execute("""
                SELECT name, class, stock_quantity, price, generic_name
                FROM medicines 
                WHERE name LIKE ? OR generic_name LIKE ?
                ORDER BY price ASC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
            
            medicines = self.cursor.fetchall()
            
            if not medicines:
                print(f"❌ No medicines found matching: {search_term}")
                return
            
            print(f"\n🔍 Search Results for '{search_term}' (showing top {len(medicines)}):")
            print("=" * 90)
            print(f"{'Name':<25} | {'Class':<15} | {'Stock':<6} | {'Price':<8} | {'Generic Name':<20}")
            print("-" * 90)
            
            for name, class_name, stock, price, generic in medicines:
                print(f"{name:<25} | {class_name:<15} | {stock:<6} | ${price:<7.2f} | {generic:<20}")
                
        except Exception as e:
            print(f"❌ Error searching medicines: {e}")
    
    def show_cheapest_alternatives(self, class_name: str, limit: int = 5):
        """Show cheapest medicines in a class."""
        try:
            self.cursor.execute("""
                SELECT name, stock_quantity, price, generic_name, manufacturer
                FROM medicines 
                WHERE class = ? 
                ORDER BY price ASC
                LIMIT ?
            """, (class_name, limit))
            
            medicines = self.cursor.fetchall()
            
            if not medicines:
                print(f"❌ No medicines found in class: {class_name}")
                return
            
            print(f"\n💰 Cheapest alternatives in '{class_name}' class:")
            print("=" * 90)
            print(f"{'Name':<25} | {'Stock':<6} | {'Price':<8} | {'Generic Name':<20} | {'Manufacturer':<20}")
            print("-" * 90)
            
            for name, stock, price, generic, manufacturer in medicines:
                print(f"{name:<25} | {stock:<6} | ${price:<7.2f} | {generic:<20} | {manufacturer:<20}")
                
        except Exception as e:
            print(f"❌ Error showing cheapest alternatives: {e}")
    
    def show_sample_data(self, limit: int = 20):
        """Show sample data from the database."""
        try:
            self.cursor.execute("""
                SELECT name, class, stock_quantity, price, generic_name
                FROM medicines 
                ORDER BY RANDOM()
                LIMIT ?
            """, (limit,))
            
            medicines = self.cursor.fetchall()
            
            print(f"\n📋 Random Sample Data ({len(medicines)} medicines):")
            print("=" * 90)
            print(f"{'Name':<25} | {'Class':<15} | {'Stock':<6} | {'Price':<8} | {'Generic Name':<20}")
            print("-" * 90)
            
            for name, class_name, stock, price, generic in medicines:
                print(f"{name:<25} | {class_name:<15} | {stock:<6} | ${price:<7.2f} | {generic:<20}")
                
        except Exception as e:
            print(f"❌ Error showing sample data: {e}")
    
    def interactive_menu(self):
        """Interactive menu for exploring the database."""
        while True:
            print("\n" + "="*60)
            print("🏥 MEDICINE DATABASE VIEWER")
            print("="*60)
            print("1. Show database statistics")
            print("2. Show all medicine classes")
            print("3. Show medicines by class")
            print("4. Search medicines")
            print("5. Show cheapest alternatives in a class")
            print("6. Show random sample data")
            print("7. Exit")
            print("-"*60)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                stats = self.get_database_stats()
                if stats:
                    print(f"\n📊 Database Statistics:")
                    print(f"   Total Medicines: {stats['total_medicines']}")
                    print(f"   Total Classes: {stats['total_classes']}")
                    print(f"   Price Range: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}")
                    print(f"   Average Price: ${stats['price_range'][2]:.2f}")
                    print(f"   Stock Range: {stats['stock_range'][0]} - {stats['stock_range'][1]}")
                    print(f"   Average Stock: {stats['stock_range'][2]:.0f}")
            
            elif choice == "2":
                self.show_all_classes()
            
            elif choice == "3":
                class_name = input("Enter class name (e.g., Antibiotics, Pain Relievers): ").strip()
                if class_name:
                    limit = input("Enter number of results (default 10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10
                    self.show_medicines_by_class(class_name, limit)
            
            elif choice == "4":
                search_term = input("Enter search term: ").strip()
                if search_term:
                    limit = input("Enter number of results (default 10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10
                    self.search_medicines(search_term, limit)
            
            elif choice == "5":
                class_name = input("Enter class name: ").strip()
                if class_name:
                    limit = input("Enter number of results (default 5): ").strip()
                    limit = int(limit) if limit.isdigit() else 5
                    self.show_cheapest_alternatives(class_name, limit)
            
            elif choice == "6":
                limit = input("Enter number of samples (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                self.show_sample_data(limit)
            
            elif choice == "7":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-7.")

def main():
    """Main function to run the database viewer."""
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "data/medicines.db"
    
    viewer = MedicineDatabaseViewer(db_path)
    
    if not viewer.connect():
        print(f"❌ Could not connect to database: {db_path}")
        print("   Make sure the database exists. Run 'python src/database/create_db.py' first.")
        return
    
    print(f"✅ Connected to database: {db_path}")
    
    # Show quick stats
    stats = viewer.get_database_stats()
    if stats:
        print(f"📊 Database contains {stats['total_medicines']} medicines across {stats['total_classes']} classes")
    
    # Start interactive menu
    viewer.interactive_menu()
    viewer.close()

if __name__ == "__main__":
    main() 