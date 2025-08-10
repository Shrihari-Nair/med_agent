#!/usr/bin/env python3
"""
Medicine Database Creator
Creates a SQLite database with 500 medicines for cost-effective alternative suggestions.
"""

import sqlite3
import random
from typing import List, Tuple

class MedicineDatabaseCreator:
    """Creates and populates a medicine database with comprehensive medicine data."""
    
    def __init__(self, db_path: str = "medicines.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    def create_table(self):
        """Create the medicines table."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            stock_quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            generic_name TEXT,
            dosage_form TEXT,
            strength TEXT,
            manufacturer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_sql)
        self.conn.commit()
        
    def get_medicine_data(self) -> List[Tuple]:
        """Generate comprehensive medicine data with realistic names, classes, and prices."""
        
        # Medicine classes with their common medicines
        medicine_classes = {
            "Antibiotics": [
                ("Amoxicillin", "Amoxicillin", "Capsule", "500mg", "Cipla"),
                ("Azithromycin", "Azithromycin", "Tablet", "250mg", "Sun Pharma"),
                ("Ciprofloxacin", "Ciprofloxacin", "Tablet", "500mg", "Dr. Reddy's"),
                ("Doxycycline", "Doxycycline", "Capsule", "100mg", "Lupin"),
                ("Cephalexin", "Cephalexin", "Capsule", "500mg", "Aurobindo"),
                ("Metronidazole", "Metronidazole", "Tablet", "400mg", "Zydus"),
                ("Clarithromycin", "Clarithromycin", "Tablet", "250mg", "Glenmark"),
                ("Levofloxacin", "Levofloxacin", "Tablet", "500mg", "Torrent"),
                ("Erythromycin", "Erythromycin", "Tablet", "250mg", "Alkem"),
                ("Tetracycline", "Tetracycline", "Capsule", "250mg", "Mankind")
            ],
            "Pain Relievers": [
                ("Paracetamol", "Acetaminophen", "Tablet", "500mg", "GSK"),
                ("Ibuprofen", "Ibuprofen", "Tablet", "400mg", "Pfizer"),
                ("Aspirin", "Acetylsalicylic Acid", "Tablet", "100mg", "Bayer"),
                ("Diclofenac", "Diclofenac", "Tablet", "50mg", "Novartis"),
                ("Naproxen", "Naproxen", "Tablet", "250mg", "Roche"),
                ("Ketorolac", "Ketorolac", "Tablet", "10mg", "Abbott"),
                ("Mefenamic Acid", "Mefenamic Acid", "Capsule", "250mg", "Sanofi"),
                ("Tramadol", "Tramadol", "Tablet", "50mg", "Janssen"),
                ("Codeine", "Codeine", "Tablet", "30mg", "Mallinckrodt"),
                ("Morphine", "Morphine", "Tablet", "10mg", "Purdue")
            ],
            "Antihistamines": [
                ("Cetirizine", "Cetirizine", "Tablet", "10mg", "UCB"),
                ("Loratadine", "Loratadine", "Tablet", "10mg", "Merck"),
                ("Fexofenadine", "Fexofenadine", "Tablet", "120mg", "Sanofi"),
                ("Diphenhydramine", "Diphenhydramine", "Tablet", "25mg", "Johnson & Johnson"),
                ("Chlorpheniramine", "Chlorpheniramine", "Tablet", "4mg", "GSK"),
                ("Desloratadine", "Desloratadine", "Tablet", "5mg", "Merck"),
                ("Levocetirizine", "Levocetirizine", "Tablet", "5mg", "UCB"),
                ("Bilastine", "Bilastine", "Tablet", "20mg", "Menarini"),
                ("Rupatadine", "Rupatadine", "Tablet", "10mg", "J. Uriach"),
                ("Ebastine", "Ebastine", "Tablet", "10mg", "Almirall")
            ],
            "Antacids": [
                ("Omeprazole", "Omeprazole", "Capsule", "20mg", "AstraZeneca"),
                ("Pantoprazole", "Pantoprazole", "Tablet", "40mg", "Pfizer"),
                ("Esomeprazole", "Esomeprazole", "Capsule", "20mg", "AstraZeneca"),
                ("Lansoprazole", "Lansoprazole", "Capsule", "30mg", "Takeda"),
                ("Rabeprazole", "Rabeprazole", "Tablet", "20mg", "Eisai"),
                ("Ranitidine", "Ranitidine", "Tablet", "150mg", "GSK"),
                ("Famotidine", "Famotidine", "Tablet", "20mg", "Merck"),
                ("Cimetidine", "Cimetidine", "Tablet", "200mg", "GSK"),
                ("Aluminum Hydroxide", "Aluminum Hydroxide", "Tablet", "500mg", "Bayer"),
                ("Calcium Carbonate", "Calcium Carbonate", "Tablet", "500mg", "GSK")
            ],
            "Antihypertensives": [
                ("Amlodipine", "Amlodipine", "Tablet", "5mg", "Pfizer"),
                ("Lisinopril", "Lisinopril", "Tablet", "10mg", "Merck"),
                ("Losartan", "Losartan", "Tablet", "50mg", "Merck"),
                ("Metoprolol", "Metoprolol", "Tablet", "50mg", "AstraZeneca"),
                ("Atenolol", "Atenolol", "Tablet", "50mg", "AstraZeneca"),
                ("Valsartan", "Valsartan", "Tablet", "80mg", "Novartis"),
                ("Irbesartan", "Irbesartan", "Tablet", "150mg", "Sanofi"),
                ("Candesartan", "Candesartan", "Tablet", "8mg", "AstraZeneca"),
                ("Telmisartan", "Telmisartan", "Tablet", "40mg", "Boehringer"),
                ("Olmesartan", "Olmesartan", "Tablet", "20mg", "Daiichi Sankyo")
            ],
            "Antidiabetics": [
                ("Metformin", "Metformin", "Tablet", "500mg", "Merck"),
                ("Glibenclamide", "Glibenclamide", "Tablet", "5mg", "Sanofi"),
                ("Glimepiride", "Glimepiride", "Tablet", "1mg", "Sanofi"),
                ("Pioglitazone", "Pioglitazone", "Tablet", "15mg", "Takeda"),
                ("Sitagliptin", "Sitagliptin", "Tablet", "100mg", "Merck"),
                ("Linagliptin", "Linagliptin", "Tablet", "5mg", "Boehringer"),
                ("Saxagliptin", "Saxagliptin", "Tablet", "5mg", "AstraZeneca"),
                ("Vildagliptin", "Vildagliptin", "Tablet", "50mg", "Novartis"),
                ("Dapagliflozin", "Dapagliflozin", "Tablet", "10mg", "AstraZeneca"),
                ("Empagliflozin", "Empagliflozin", "Tablet", "10mg", "Boehringer")
            ],
            "Statins": [
                ("Atorvastatin", "Atorvastatin", "Tablet", "10mg", "Pfizer"),
                ("Simvastatin", "Simvastatin", "Tablet", "20mg", "Merck"),
                ("Rosuvastatin", "Rosuvastatin", "Tablet", "10mg", "AstraZeneca"),
                ("Pravastatin", "Pravastatin", "Tablet", "20mg", "Bristol-Myers"),
                ("Fluvastatin", "Fluvastatin", "Capsule", "40mg", "Novartis"),
                ("Lovastatin", "Lovastatin", "Tablet", "20mg", "Merck"),
                ("Pitavastatin", "Pitavastatin", "Tablet", "2mg", "Kowa"),
                ("Cerivastatin", "Cerivastatin", "Tablet", "0.3mg", "Bayer"),
                ("Mevastatin", "Mevastatin", "Tablet", "20mg", "Merck"),
                ("Compactin", "Compactin", "Tablet", "20mg", "Merck")
            ],
            "Antidepressants": [
                ("Sertraline", "Sertraline", "Tablet", "50mg", "Pfizer"),
                ("Fluoxetine", "Fluoxetine", "Capsule", "20mg", "Eli Lilly"),
                ("Escitalopram", "Escitalopram", "Tablet", "10mg", "Lundbeck"),
                ("Paroxetine", "Paroxetine", "Tablet", "20mg", "GSK"),
                ("Citalopram", "Citalopram", "Tablet", "20mg", "Lundbeck"),
                ("Venlafaxine", "Venlafaxine", "Capsule", "75mg", "Pfizer"),
                ("Duloxetine", "Duloxetine", "Capsule", "30mg", "Eli Lilly"),
                ("Bupropion", "Bupropion", "Tablet", "150mg", "GSK"),
                ("Mirtazapine", "Mirtazapine", "Tablet", "15mg", "Merck"),
                ("Trazodone", "Trazodone", "Tablet", "50mg", "Pfizer")
            ],
            "Antipsychotics": [
                ("Risperidone", "Risperidone", "Tablet", "2mg", "Janssen"),
                ("Olanzapine", "Olanzapine", "Tablet", "5mg", "Eli Lilly"),
                ("Quetiapine", "Quetiapine", "Tablet", "25mg", "AstraZeneca"),
                ("Aripiprazole", "Aripiprazole", "Tablet", "10mg", "Otsuka"),
                ("Ziprasidone", "Ziprasidone", "Capsule", "40mg", "Pfizer"),
                ("Paliperidone", "Paliperidone", "Tablet", "3mg", "Janssen"),
                ("Asenapine", "Asenapine", "Tablet", "5mg", "Merck"),
                ("Lurasidone", "Lurasidone", "Tablet", "40mg", "Sunovion"),
                ("Iloperidone", "Iloperidone", "Tablet", "2mg", "Vanda"),
                ("Cariprazine", "Cariprazine", "Capsule", "1.5mg", "Allergan")
            ],
            "Benzodiazepines": [
                ("Alprazolam", "Alprazolam", "Tablet", "0.5mg", "Pfizer"),
                ("Diazepam", "Diazepam", "Tablet", "5mg", "Roche"),
                ("Lorazepam", "Lorazepam", "Tablet", "1mg", "Wyeth"),
                ("Clonazepam", "Clonazepam", "Tablet", "0.5mg", "Roche"),
                ("Temazepam", "Temazepam", "Capsule", "15mg", "Mallinckrodt"),
                ("Oxazepam", "Oxazepam", "Tablet", "15mg", "Wyeth"),
                ("Chlordiazepoxide", "Chlordiazepoxide", "Capsule", "10mg", "Roche"),
                ("Flurazepam", "Flurazepam", "Capsule", "15mg", "Roche"),
                ("Triazolam", "Triazolam", "Tablet", "0.25mg", "Upjohn"),
                ("Estazolam", "Estazolam", "Tablet", "1mg", "Abbott")
            ],
            "Corticosteroids": [
                ("Prednisone", "Prednisone", "Tablet", "5mg", "Merck"),
                ("Methylprednisolone", "Methylprednisolone", "Tablet", "4mg", "Pfizer"),
                ("Dexamethasone", "Dexamethasone", "Tablet", "0.5mg", "Merck"),
                ("Hydrocortisone", "Hydrocortisone", "Tablet", "20mg", "Pfizer"),
                ("Betamethasone", "Betamethasone", "Tablet", "0.5mg", "Merck"),
                ("Triamcinolone", "Triamcinolone", "Tablet", "4mg", "Bristol-Myers"),
                ("Fludrocortisone", "Fludrocortisone", "Tablet", "0.1mg", "Merck"),
                ("Cortisone", "Cortisone", "Tablet", "25mg", "Merck"),
                ("Budesonide", "Budesonide", "Capsule", "3mg", "AstraZeneca"),
                ("Fluticasone", "Fluticasone", "Inhaler", "50mcg", "GSK")
            ],
            "Anticoagulants": [
                ("Warfarin", "Warfarin", "Tablet", "5mg", "Bristol-Myers"),
                ("Heparin", "Heparin", "Injection", "5000U", "Pfizer"),
                ("Enoxaparin", "Enoxaparin", "Injection", "40mg", "Sanofi"),
                ("Dabigatran", "Dabigatran", "Capsule", "150mg", "Boehringer"),
                ("Rivaroxaban", "Rivaroxaban", "Tablet", "20mg", "Bayer"),
                ("Apixaban", "Apixaban", "Tablet", "5mg", "Bristol-Myers"),
                ("Fondaparinux", "Fondaparinux", "Injection", "2.5mg", "GSK"),
                ("Dalteparin", "Dalteparin", "Injection", "5000U", "Pfizer"),
                ("Tinzaparin", "Tinzaparin", "Injection", "4500U", "Leo Pharma"),
                ("Argatroban", "Argatroban", "Injection", "100mg", "Mitsubishi")
            ],
            "Diuretics": [
                ("Furosemide", "Furosemide", "Tablet", "40mg", "Sanofi"),
                ("Hydrochlorothiazide", "Hydrochlorothiazide", "Tablet", "25mg", "Merck"),
                ("Spironolactone", "Spironolactone", "Tablet", "25mg", "Pfizer"),
                ("Chlorthalidone", "Chlorthalidone", "Tablet", "25mg", "Merck"),
                ("Bumetanide", "Bumetanide", "Tablet", "1mg", "Roche"),
                ("Torsemide", "Torsemide", "Tablet", "10mg", "Roche"),
                ("Amiloride", "Amiloride", "Tablet", "5mg", "Merck"),
                ("Triamterene", "Triamterene", "Capsule", "50mg", "Merck"),
                ("Indapamide", "Indapamide", "Tablet", "2.5mg", "Servier"),
                ("Metolazone", "Metolazone", "Tablet", "2.5mg", "Pfizer")
            ],
            "Bronchodilators": [
                ("Salbutamol", "Albuterol", "Inhaler", "100mcg", "GSK"),
                ("Terbutaline", "Terbutaline", "Tablet", "5mg", "AstraZeneca"),
                ("Formoterol", "Formoterol", "Inhaler", "12mcg", "AstraZeneca"),
                ("Salmeterol", "Salmeterol", "Inhaler", "25mcg", "GSK"),
                ("Ipratropium", "Ipratropium", "Inhaler", "20mcg", "Boehringer"),
                ("Tiotropium", "Tiotropium", "Inhaler", "18mcg", "Boehringer"),
                ("Umeclidinium", "Umeclidinium", "Inhaler", "62.5mcg", "GSK"),
                ("Glycopyrrolate", "Glycopyrrolate", "Inhaler", "15.6mcg", "Sunovion"),
                ("Indacaterol", "Indacaterol", "Inhaler", "75mcg", "Novartis"),
                ("Vilanterol", "Vilanterol", "Inhaler", "25mcg", "GSK")
            ],
            "Antiemetics": [
                ("Ondansetron", "Ondansetron", "Tablet", "4mg", "GSK"),
                ("Metoclopramide", "Metoclopramide", "Tablet", "10mg", "Baxter"),
                ("Prochlorperazine", "Prochlorperazine", "Tablet", "5mg", "GSK"),
                ("Domperidone", "Domperidone", "Tablet", "10mg", "Janssen"),
                ("Granisetron", "Granisetron", "Tablet", "1mg", "Roche"),
                ("Palonosetron", "Palonosetron", "Injection", "0.25mg", "Eisai"),
                ("Dolasetron", "Dolasetron", "Tablet", "100mg", "Sanofi"),
                ("Tropisetron", "Tropisetron", "Capsule", "5mg", "Novartis"),
                ("Ramosetron", "Ramosetron", "Tablet", "0.1mg", "Astellas"),
                ("Aprepitant", "Aprepitant", "Capsule", "125mg", "Merck")
            ],
            "Laxatives": [
                ("Bisacodyl", "Bisacodyl", "Tablet", "5mg", "Boehringer"),
                ("Senna", "Senna", "Tablet", "8.6mg", "GSK"),
                ("Lactulose", "Lactulose", "Syrup", "10g", "Solvay"),
                ("Polyethylene Glycol", "PEG", "Powder", "17g", "Bayer"),
                ("Docusate", "Docusate", "Capsule", "100mg", "Purdue"),
                ("Glycerin", "Glycerin", "Suppository", "2g", "Baxter"),
                ("Milk of Magnesia", "Magnesium Hydroxide", "Liquid", "400mg", "Bayer"),
                ("Mineral Oil", "Mineral Oil", "Liquid", "15ml", "Baxter"),
                ("Psyllium", "Psyllium", "Powder", "3.4g", "Metamucil"),
                ("Methylcellulose", "Methylcellulose", "Powder", "2g", "Citrucel")
            ],
            "Antifungals": [
                ("Fluconazole", "Fluconazole", "Capsule", "150mg", "Pfizer"),
                ("Itraconazole", "Itraconazole", "Capsule", "100mg", "Janssen"),
                ("Ketoconazole", "Ketoconazole", "Tablet", "200mg", "Janssen"),
                ("Terbinafine", "Terbinafine", "Tablet", "250mg", "Novartis"),
                ("Griseofulvin", "Griseofulvin", "Tablet", "500mg", "GSK"),
                ("Amphotericin B", "Amphotericin B", "Injection", "50mg", "Bristol-Myers"),
                ("Caspofungin", "Caspofungin", "Injection", "50mg", "Merck"),
                ("Micafungin", "Micafungin", "Injection", "100mg", "Astellas"),
                ("Anidulafungin", "Anidulafungin", "Injection", "100mg", "Pfizer"),
                ("Voriconazole", "Voriconazole", "Tablet", "200mg", "Pfizer")
            ],
            "Antivirals": [
                ("Acyclovir", "Acyclovir", "Tablet", "400mg", "GSK"),
                ("Valacyclovir", "Valacyclovir", "Tablet", "500mg", "GSK"),
                ("Oseltamivir", "Oseltamivir", "Capsule", "75mg", "Roche"),
                ("Zanamivir", "Zanamivir", "Inhaler", "5mg", "GSK"),
                ("Ganciclovir", "Ganciclovir", "Capsule", "250mg", "Roche"),
                ("Valganciclovir", "Valganciclovir", "Tablet", "450mg", "Roche"),
                ("Famciclovir", "Famciclovir", "Tablet", "250mg", "Novartis"),
                ("Ribavirin", "Ribavirin", "Capsule", "200mg", "Merck"),
                ("Interferon", "Interferon", "Injection", "3MU", "Merck"),
                ("Lamivudine", "Lamivudine", "Tablet", "100mg", "GSK")
            ],
            "Vitamins": [
                ("Vitamin C", "Ascorbic Acid", "Tablet", "500mg", "Bayer"),
                ("Vitamin D", "Cholecalciferol", "Capsule", "1000IU", "Pfizer"),
                ("Vitamin B12", "Cyanocobalamin", "Tablet", "1000mcg", "Merck"),
                ("Vitamin B6", "Pyridoxine", "Tablet", "50mg", "Bayer"),
                ("Vitamin B1", "Thiamine", "Tablet", "100mg", "Merck"),
                ("Vitamin B2", "Riboflavin", "Tablet", "50mg", "Bayer"),
                ("Vitamin B3", "Niacin", "Tablet", "500mg", "Merck"),
                ("Vitamin B5", "Pantothenic Acid", "Tablet", "100mg", "Bayer"),
                ("Vitamin B7", "Biotin", "Tablet", "1000mcg", "Merck"),
                ("Vitamin B9", "Folic Acid", "Tablet", "5mg", "Bayer")
            ],
            "Minerals": [
                ("Calcium", "Calcium Carbonate", "Tablet", "500mg", "Bayer"),
                ("Iron", "Ferrous Sulfate", "Tablet", "325mg", "Merck"),
                ("Zinc", "Zinc Sulfate", "Tablet", "50mg", "Bayer"),
                ("Magnesium", "Magnesium Oxide", "Tablet", "250mg", "Merck"),
                ("Potassium", "Potassium Chloride", "Tablet", "20mEq", "Bayer"),
                ("Selenium", "Selenium", "Tablet", "100mcg", "Merck"),
                ("Copper", "Copper Sulfate", "Tablet", "2mg", "Bayer"),
                ("Manganese", "Manganese Sulfate", "Tablet", "5mg", "Merck"),
                ("Chromium", "Chromium Picolinate", "Tablet", "200mcg", "Bayer"),
                ("Molybdenum", "Molybdenum", "Tablet", "75mcg", "Merck")
            ]
        }
        
        medicines = []
        medicine_id = 1
        
        for class_name, class_medicines in medicine_classes.items():
            for brand_name, generic_name, dosage_form, strength, manufacturer in class_medicines:
                # Generate multiple variants with different prices and stock levels
                for variant in range(5):  # 5 variants per medicine = 50 medicines per class
                    # Price variation based on brand vs generic
                    base_price = random.uniform(5.0, 50.0)
                    if "generic" in generic_name.lower():
                        price = base_price * 0.3  # Generic is cheaper
                    else:
                        price = base_price * random.uniform(0.8, 1.5)  # Brand variation
                    
                    # Stock quantity variation
                    stock = random.randint(10, 500)
                    
                    # Create variant name
                    if variant == 0:
                        name = brand_name
                    else:
                        name = f"{brand_name} {chr(65 + variant)}"  # A, B, C, D variants
                    
                    medicines.append((
                        name,
                        class_name,
                        stock,
                        round(price, 2),
                        generic_name,
                        dosage_form,
                        strength,
                        manufacturer
                    ))
                    medicine_id += 1
        
        return medicines
    
    def insert_medicines(self, medicines: List[Tuple]):
        """Insert medicines into the database."""
        insert_sql = """
        INSERT INTO medicines (name, class, stock_quantity, price, generic_name, dosage_form, strength, manufacturer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.executemany(insert_sql, medicines)
        self.conn.commit()
        
    def create_database(self):
        """Create and populate the medicine database."""
        try:
            print("🔧 Creating Medicine Database...")
            
            self.connect()
            self.create_table()
            print("   ✅ Table created successfully")
            
            medicines = self.get_medicine_data()
            print(f"   📊 Generated {len(medicines)} medicines across {len(set(med[1] for med in medicines))} classes")
            
            self.insert_medicines(medicines)
            print("   ✅ Medicines inserted successfully")
            
            # Verify the data
            self.cursor.execute("SELECT COUNT(*) FROM medicines")
            count = self.cursor.fetchone()[0]
            print(f"   📋 Total medicines in database: {count}")
            
            # Show sample data
            print("\n📋 Sample Medicines:")
            print("=" * 80)
            self.cursor.execute("""
                SELECT name, class, stock_quantity, price, generic_name 
                FROM medicines 
                LIMIT 10
            """)
            
            for row in self.cursor.fetchall():
                print(f"  {row[0]:<20} | {row[1]:<15} | Stock: {row[2]:<3} | ${row[3]:<6} | {row[4]}")
            
            print("\n✅ Database created successfully!")
            print(f"📁 Database file: {self.db_path}")
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
        finally:
            self.close()

def main():
    """Main function to create the medicine database."""
    creator = MedicineDatabaseCreator()
    creator.create_database()

if __name__ == "__main__":
    main() 