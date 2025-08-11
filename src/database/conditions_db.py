"""
Medical Conditions Database Manager
Creates and manages medical conditions linked to medicines for treatment matching.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class MedicalConditionsManager:
    """Manages medical conditions database for treatment recommendations."""
    
    def __init__(self, db_path: str = "data/conditions.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self) -> bool:
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self):
        """Create the medical conditions tables."""
        cursor = self.conn.cursor()
        
        # Create conditions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition_name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                description TEXT,
                symptoms TEXT,
                prevalence TEXT,
                severity_level TEXT CHECK (severity_level IN ('mild', 'moderate', 'severe', 'critical')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create condition_treatments table (many-to-many relationship)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS condition_treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition_name TEXT NOT NULL,
                medicine_name TEXT NOT NULL,
                effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 100),
                dosage_recommendations TEXT,
                treatment_line TEXT CHECK (treatment_line IN ('first-line', 'second-line', 'third-line', 'alternative')),
                contraindications TEXT,
                special_considerations TEXT,
                evidence_level TEXT CHECK (evidence_level IN ('high', 'moderate', 'low', 'expert_opinion')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (condition_name) REFERENCES conditions(condition_name),
                UNIQUE(condition_name, medicine_name)
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_condition_name ON conditions(condition_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_condition_category ON conditions(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_treatment_condition ON condition_treatments(condition_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_treatment_medicine ON condition_treatments(medicine_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_effectiveness ON condition_treatments(effectiveness_rating)')
        
        self.conn.commit()
        print("✅ Medical conditions tables created successfully")
    
    def populate_conditions(self):
        """Populate the database with medical conditions and treatment data."""
        
        # Medical conditions data
        conditions_data = [
            # Cardiovascular conditions
            {
                "name": "Hypertension", "category": "Cardiovascular",
                "description": "High blood pressure, a common cardiovascular condition",
                "symptoms": "Often asymptomatic, headaches, dizziness, vision problems",
                "prevalence": "Very common - affects 30-40% of adults",
                "severity": "moderate"
            },
            {
                "name": "Angina", "category": "Cardiovascular",
                "description": "Chest pain due to reduced blood flow to the heart muscle",
                "symptoms": "Chest pain, shortness of breath, fatigue, nausea",
                "prevalence": "Common in older adults",
                "severity": "moderate"
            },
            {
                "name": "Atrial Fibrillation", "category": "Cardiovascular",
                "description": "Irregular heart rhythm increasing stroke risk",
                "symptoms": "Palpitations, shortness of breath, fatigue, chest pain",
                "prevalence": "Common, especially in elderly",
                "severity": "severe"
            },
            {
                "name": "Heart Failure", "category": "Cardiovascular",
                "description": "Heart cannot pump blood effectively",
                "symptoms": "Shortness of breath, fatigue, leg swelling, rapid heartbeat",
                "prevalence": "Common in elderly",
                "severity": "severe"
            },
            
            # Infectious diseases
            {
                "name": "Bacterial Pneumonia", "category": "Infectious",
                "description": "Bacterial infection of the lungs",
                "symptoms": "Cough, fever, chest pain, difficulty breathing, fatigue",
                "prevalence": "Common respiratory infection",
                "severity": "moderate"
            },
            {
                "name": "Urinary Tract Infection", "category": "Infectious",
                "description": "Bacterial infection of the urinary system",
                "symptoms": "Burning urination, frequent urination, pelvic pain, fever",
                "prevalence": "Very common, especially in women",
                "severity": "mild"
            },
            {
                "name": "Skin and Soft Tissue Infection", "category": "Infectious",
                "description": "Bacterial infection of skin and underlying tissues",
                "symptoms": "Redness, swelling, warmth, pain, pus formation",
                "prevalence": "Common",
                "severity": "mild"
            },
            {
                "name": "Respiratory Tract Infection", "category": "Infectious",
                "description": "Bacterial infection of respiratory system",
                "symptoms": "Cough, sore throat, fever, congestion, fatigue",
                "prevalence": "Very common",
                "severity": "mild"
            },
            
            # Neurological conditions
            {
                "name": "Anxiety Disorder", "category": "Neurological",
                "description": "Excessive worry and fear affecting daily functioning",
                "symptoms": "Excessive worry, restlessness, fatigue, difficulty concentrating",
                "prevalence": "Very common - affects 18% of adults annually",
                "severity": "moderate"
            },
            {
                "name": "Depression", "category": "Neurological",
                "description": "Persistent sadness and loss of interest",
                "symptoms": "Persistent sadness, loss of interest, fatigue, sleep changes",
                "prevalence": "Common - affects 8% of adults annually",
                "severity": "moderate"
            },
            {
                "name": "Bipolar Disorder", "category": "Neurological",
                "description": "Mood disorder with alternating manic and depressive episodes",
                "symptoms": "Mood swings, manic episodes, depressive episodes, sleep changes",
                "prevalence": "Less common - affects 2-3% of adults",
                "severity": "severe"
            },
            {
                "name": "Schizophrenia", "category": "Neurological",
                "description": "Chronic mental disorder affecting perception and behavior",
                "symptoms": "Hallucinations, delusions, disorganized thinking, social withdrawal",
                "prevalence": "Rare - affects 1% of population",
                "severity": "severe"
            },
            
            # Metabolic conditions
            {
                "name": "Type 2 Diabetes", "category": "Metabolic",
                "description": "Insulin resistance leading to high blood sugar",
                "symptoms": "Increased thirst, frequent urination, fatigue, blurred vision",
                "prevalence": "Very common - affects 10% of adults",
                "severity": "moderate"
            },
            {
                "name": "Hyperlipidemia", "category": "Metabolic",
                "description": "Elevated cholesterol and triglyceride levels",
                "symptoms": "Usually asymptomatic until complications develop",
                "prevalence": "Very common - affects 35% of adults",
                "severity": "mild"
            },
            
            # Pain and inflammation
            {
                "name": "Osteoarthritis", "category": "Musculoskeletal",
                "description": "Degenerative joint disease causing pain and stiffness",
                "symptoms": "Joint pain, stiffness, reduced range of motion, swelling",
                "prevalence": "Very common in older adults",
                "severity": "moderate"
            },
            {
                "name": "Rheumatoid Arthritis", "category": "Autoimmune",
                "description": "Autoimmune inflammatory arthritis",
                "symptoms": "Joint pain, swelling, morning stiffness, fatigue",
                "prevalence": "Common - affects 1% of adults",
                "severity": "moderate"
            },
            {
                "name": "Acute Pain", "category": "Pain",
                "description": "Short-term pain from injury or medical procedures",
                "symptoms": "Localized pain, inflammation, reduced function",
                "prevalence": "Universal experience",
                "severity": "mild"
            },
            {
                "name": "Migraine", "category": "Neurological",
                "description": "Severe headaches often with nausea and light sensitivity",
                "symptoms": "Severe headache, nausea, vomiting, light sensitivity",
                "prevalence": "Common - affects 15% of adults",
                "severity": "moderate"
            },
            
            # Respiratory conditions
            {
                "name": "Asthma", "category": "Respiratory",
                "description": "Chronic inflammatory airway disease",
                "symptoms": "Wheezing, cough, shortness of breath, chest tightness",
                "prevalence": "Common - affects 8% of adults",
                "severity": "moderate"
            },
            {
                "name": "COPD", "category": "Respiratory",
                "description": "Chronic obstructive pulmonary disease",
                "symptoms": "Chronic cough, shortness of breath, excessive sputum",
                "prevalence": "Common in smokers",
                "severity": "severe"
            },
            
            # Allergic conditions
            {
                "name": "Allergic Rhinitis", "category": "Allergic",
                "description": "Seasonal or perennial nasal allergies",
                "symptoms": "Sneezing, runny nose, itchy eyes, nasal congestion",
                "prevalence": "Very common - affects 25% of adults",
                "severity": "mild"
            },
            {
                "name": "Urticaria", "category": "Allergic",
                "description": "Hives or raised, itchy skin welts",
                "symptoms": "Raised, itchy, red welts on skin",
                "prevalence": "Common",
                "severity": "mild"
            },
            
            # Gastrointestinal conditions
            {
                "name": "GERD", "category": "Gastrointestinal",
                "description": "Gastroesophageal reflux disease",
                "symptoms": "Heartburn, acid regurgitation, chest pain, difficulty swallowing",
                "prevalence": "Very common - affects 20% of adults",
                "severity": "mild"
            },
            {
                "name": "Constipation", "category": "Gastrointestinal",
                "description": "Difficulty with bowel movements",
                "symptoms": "Infrequent bowel movements, hard stools, straining",
                "prevalence": "Very common",
                "severity": "mild"
            }
        ]
        
        # Treatment relationships data
        treatments_data = [
            # Hypertension treatments
            {"condition": "Hypertension", "medicine": "Atenolol", "effectiveness": 85, "dosage": "25-100mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Hypertension", "medicine": "Amlodipine", "effectiveness": 88, "dosage": "2.5-10mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Hypertension", "medicine": "Candesartan", "effectiveness": 87, "dosage": "4-32mg daily", "line": "first-line", "evidence": "high"},
            
            # Angina treatments
            {"condition": "Angina", "medicine": "Atenolol", "effectiveness": 82, "dosage": "50-100mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Angina", "medicine": "Amlodipine", "effectiveness": 80, "dosage": "5-10mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Angina", "medicine": "Aspirin", "effectiveness": 75, "dosage": "75-100mg daily", "line": "first-line", "evidence": "high"},
            
            # Atrial Fibrillation treatments
            {"condition": "Atrial Fibrillation", "medicine": "Apixaban", "effectiveness": 90, "dosage": "5mg twice daily", "line": "first-line", "evidence": "high"},
            {"condition": "Atrial Fibrillation", "medicine": "Atenolol", "effectiveness": 70, "dosage": "25-100mg daily", "line": "second-line", "evidence": "moderate"},
            
            # Heart Failure treatments
            {"condition": "Heart Failure", "medicine": "Atenolol", "effectiveness": 78, "dosage": "6.25-25mg twice daily", "line": "first-line", "evidence": "high"},
            {"condition": "Heart Failure", "medicine": "Candesartan", "effectiveness": 82, "dosage": "4-32mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Heart Failure", "medicine": "Bumetanide", "effectiveness": 85, "dosage": "0.5-2mg daily", "line": "first-line", "evidence": "high"},
            
            # Bacterial Pneumonia treatments
            {"condition": "Bacterial Pneumonia", "medicine": "Amoxicillin", "effectiveness": 85, "dosage": "500mg three times daily", "line": "first-line", "evidence": "high"},
            {"condition": "Bacterial Pneumonia", "medicine": "Azithromycin", "effectiveness": 82, "dosage": "500mg daily for 3 days", "line": "first-line", "evidence": "high"},
            {"condition": "Bacterial Pneumonia", "medicine": "Cephalexin", "effectiveness": 80, "dosage": "500mg four times daily", "line": "second-line", "evidence": "high"},
            {"condition": "Bacterial Pneumonia", "medicine": "Ciprofloxacin", "effectiveness": 88, "dosage": "500mg twice daily", "line": "second-line", "evidence": "high"},
            
            # UTI treatments
            {"condition": "Urinary Tract Infection", "medicine": "Amoxicillin", "effectiveness": 75, "dosage": "500mg three times daily", "line": "second-line", "evidence": "moderate"},
            {"condition": "Urinary Tract Infection", "medicine": "Ciprofloxacin", "effectiveness": 92, "dosage": "250mg twice daily", "line": "first-line", "evidence": "high"},
            {"condition": "Urinary Tract Infection", "medicine": "Cephalexin", "effectiveness": 85, "dosage": "500mg four times daily", "line": "first-line", "evidence": "high"},
            
            # Skin infections
            {"condition": "Skin and Soft Tissue Infection", "medicine": "Amoxicillin", "effectiveness": 80, "dosage": "500mg three times daily", "line": "first-line", "evidence": "high"},
            {"condition": "Skin and Soft Tissue Infection", "medicine": "Cephalexin", "effectiveness": 88, "dosage": "500mg four times daily", "line": "first-line", "evidence": "high"},
            {"condition": "Skin and Soft Tissue Infection", "medicine": "Azithromycin", "effectiveness": 78, "dosage": "500mg daily", "line": "alternative", "evidence": "moderate"},
            
            # Respiratory infections
            {"condition": "Respiratory Tract Infection", "medicine": "Amoxicillin", "effectiveness": 82, "dosage": "500mg three times daily", "line": "first-line", "evidence": "high"},
            {"condition": "Respiratory Tract Infection", "medicine": "Azithromycin", "effectiveness": 85, "dosage": "500mg daily for 3 days", "line": "first-line", "evidence": "high"},
            {"condition": "Respiratory Tract Infection", "medicine": "Cephalexin", "effectiveness": 78, "dosage": "500mg four times daily", "line": "second-line", "evidence": "moderate"},
            
            # Anxiety treatments
            {"condition": "Anxiety Disorder", "medicine": "Alprazolam", "effectiveness": 85, "dosage": "0.25-0.5mg three times daily", "line": "second-line", "evidence": "high"},
            {"condition": "Anxiety Disorder", "medicine": "Atenolol", "effectiveness": 65, "dosage": "25-50mg daily", "line": "alternative", "evidence": "moderate"},
            
            # Depression treatments
            {"condition": "Depression", "medicine": "Bupropion", "effectiveness": 75, "dosage": "150mg twice daily", "line": "first-line", "evidence": "high"},
            
            # Bipolar disorder treatments
            {"condition": "Bipolar Disorder", "medicine": "Aripiprazole", "effectiveness": 78, "dosage": "10-30mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Bipolar Disorder", "medicine": "Asenapine", "effectiveness": 75, "dosage": "5-10mg twice daily", "line": "second-line", "evidence": "moderate"},
            {"condition": "Bipolar Disorder", "medicine": "Cariprazine", "effectiveness": 73, "dosage": "1.5-6mg daily", "line": "second-line", "evidence": "moderate"},
            
            # Schizophrenia treatments
            {"condition": "Schizophrenia", "medicine": "Aripiprazole", "effectiveness": 82, "dosage": "10-30mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Schizophrenia", "medicine": "Asenapine", "effectiveness": 78, "dosage": "5-10mg twice daily", "line": "first-line", "evidence": "high"},
            {"condition": "Schizophrenia", "medicine": "Cariprazine", "effectiveness": 80, "dosage": "1.5-6mg daily", "line": "first-line", "evidence": "high"},
            
            # Type 2 Diabetes treatments - Note: No direct medicines in our DB for diabetes
            # {"condition": "Type 2 Diabetes", "medicine": "Metformin", "effectiveness": 85, "dosage": "500-1000mg twice daily", "line": "first-line", "evidence": "high"},
            
            # Hyperlipidemia treatments
            {"condition": "Hyperlipidemia", "medicine": "Atorvastatin", "effectiveness": 88, "dosage": "10-80mg daily", "line": "first-line", "evidence": "high"},
            
            # Pain and inflammation
            {"condition": "Osteoarthritis", "medicine": "Aspirin", "effectiveness": 70, "dosage": "325-650mg four times daily", "line": "first-line", "evidence": "high"},
            {"condition": "Rheumatoid Arthritis", "medicine": "Aspirin", "effectiveness": 65, "dosage": "325-975mg four times daily", "line": "second-line", "evidence": "moderate"},
            {"condition": "Acute Pain", "medicine": "Aspirin", "effectiveness": 78, "dosage": "325-650mg every 4-6 hours", "line": "first-line", "evidence": "high"},
            {"condition": "Migraine", "medicine": "Aspirin", "effectiveness": 72, "dosage": "900-1000mg at onset", "line": "first-line", "evidence": "high"},
            
            # Respiratory conditions
            {"condition": "Asthma", "medicine": "Budesonide", "effectiveness": 85, "dosage": "200-800mcg twice daily", "line": "first-line", "evidence": "high"},
            {"condition": "COPD", "medicine": "Budesonide", "effectiveness": 75, "dosage": "400-800mcg twice daily", "line": "first-line", "evidence": "high"},
            
            # Allergic conditions
            {"condition": "Allergic Rhinitis", "medicine": "Cetirizine", "effectiveness": 88, "dosage": "10mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Allergic Rhinitis", "medicine": "Bilastine", "effectiveness": 85, "dosage": "20mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Urticaria", "medicine": "Cetirizine", "effectiveness": 90, "dosage": "10mg daily", "line": "first-line", "evidence": "high"},
            {"condition": "Urticaria", "medicine": "Bilastine", "effectiveness": 87, "dosage": "20mg daily", "line": "first-line", "evidence": "high"},
            
            # Gastrointestinal conditions - Note: Limited medicines in our DB for GI conditions
            {"condition": "Constipation", "medicine": "Bisacodyl", "effectiveness": 85, "dosage": "5-15mg daily", "line": "first-line", "evidence": "high"},
        ]
        
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM condition_treatments')
        cursor.execute('DELETE FROM conditions')
        
        # Insert conditions
        for condition in conditions_data:
            cursor.execute('''
                INSERT INTO conditions 
                (condition_name, category, description, symptoms, prevalence, severity_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                condition["name"], condition["category"], condition["description"],
                condition["symptoms"], condition["prevalence"], condition["severity"]
            ))
        
        # Insert treatments
        for treatment in treatments_data:
            cursor.execute('''
                INSERT INTO condition_treatments 
                (condition_name, medicine_name, effectiveness_rating, dosage_recommendations, 
                 treatment_line, evidence_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                treatment["condition"], treatment["medicine"], treatment["effectiveness"],
                treatment["dosage"], treatment["line"], treatment["evidence"]
            ))
        
        self.conn.commit()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) FROM conditions')
        conditions_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM condition_treatments')
        treatments_count = cursor.fetchone()[0]
        
        print(f"✅ Inserted {conditions_count} conditions and {treatments_count} treatments")
    
    def get_conditions_for_medicine(self, medicine_name: str) -> List[Dict]:
        """Get all conditions that can be treated with a specific medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.*, ct.effectiveness_rating, ct.dosage_recommendations, 
                   ct.treatment_line, ct.evidence_level
            FROM conditions c
            JOIN condition_treatments ct ON c.condition_name = ct.condition_name
            WHERE ct.medicine_name = ?
            ORDER BY ct.effectiveness_rating DESC
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_medicines_for_condition(self, condition_name: str) -> List[Dict]:
        """Get all medicines that can treat a specific condition."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT ct.*, c.category, c.severity_level
            FROM condition_treatments ct
            JOIN conditions c ON ct.condition_name = c.condition_name
            WHERE ct.condition_name = ?
            ORDER BY ct.effectiveness_rating DESC, ct.treatment_line
        ''', (condition_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_conditions(self, search_term: str) -> List[Dict]:
        """Search for conditions by name or symptoms."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conditions 
            WHERE condition_name LIKE ? OR symptoms LIKE ? OR description LIKE ?
            ORDER BY condition_name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_first_line_treatments(self, condition_name: str) -> List[Dict]:
        """Get first-line treatments for a condition."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM condition_treatments 
            WHERE condition_name = ? AND treatment_line = 'first-line'
            ORDER BY effectiveness_rating DESC
        ''', (condition_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_high_effectiveness_treatments(self, condition_name: str, min_effectiveness: int = 80) -> List[Dict]:
        """Get highly effective treatments for a condition."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM condition_treatments 
            WHERE condition_name = ? AND effectiveness_rating >= ?
            ORDER BY effectiveness_rating DESC
        ''', (condition_name, min_effectiveness))
        
        return [dict(row) for row in cursor.fetchall()]


def create_conditions_database():
    """Create and populate the medical conditions database."""
    print("🔄 Creating medical conditions database...")
    
    db = MedicalConditionsManager()
    if db.connect():
        db.create_tables()
        db.populate_conditions()
        
        # Test the database
        print("\n📊 Database Statistics:")
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conditions")
        conditions_count = cursor.fetchone()[0]
        print(f"  Total conditions: {conditions_count}")
        
        cursor.execute("SELECT COUNT(*) FROM condition_treatments")
        treatments_count = cursor.fetchone()[0]
        print(f"  Total treatments: {treatments_count}")
        
        cursor.execute("SELECT category, COUNT(*) FROM conditions GROUP BY category ORDER BY COUNT(*) DESC")
        category_counts = cursor.fetchall()
        print("\n📋 Conditions by category:")
        for category, count in category_counts:
            print(f"  {category}: {count}")
        
        cursor.execute("SELECT treatment_line, COUNT(*) FROM condition_treatments GROUP BY treatment_line")
        line_counts = cursor.fetchall()
        print("\n💊 Treatments by line:")
        for line, count in line_counts:
            print(f"  {line}: {count}")
        
        # Test some lookups
        print("\n🧪 Testing lookups:")
        hypertension_meds = db.get_medicines_for_condition("Hypertension")
        print(f"  ✅ Hypertension treatments: {len(hypertension_meds)} found")
        if hypertension_meds:
            best = hypertension_meds[0]
            print(f"      Best: {best['medicine_name']} ({best['effectiveness_rating']}% effective)")
        
        aspirin_conditions = db.get_conditions_for_medicine("Aspirin")
        print(f"  ✅ Aspirin treats: {len(aspirin_conditions)} conditions")
        
        first_line = db.get_first_line_treatments("Bacterial Pneumonia")
        print(f"  ✅ First-line pneumonia treatments: {len(first_line)} found")
        
        db.close()
        print("✅ Medical conditions database created successfully!")
        return True
    else:
        print("❌ Failed to create medical conditions database")
        return False


if __name__ == "__main__":
    create_conditions_database() 