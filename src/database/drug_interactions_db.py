"""
Drug Interactions Database Manager
Creates and manages drug-drug interactions database for safety checks.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DrugInteractionsManager:
    """Manages drug interactions database for safety checking."""
    
    def __init__(self, db_path: str = "data/drug_interactions.db"):
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
        """Create the drug interactions table."""
        cursor = self.conn.cursor()
        
        # Create drug_interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drug_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug1_name TEXT NOT NULL,
                drug2_name TEXT NOT NULL,
                interaction_severity TEXT NOT NULL CHECK (interaction_severity IN ('mild', 'moderate', 'severe', 'contraindicated')),
                description TEXT NOT NULL,
                symptoms TEXT,
                recommendation TEXT NOT NULL,
                mechanism TEXT,
                clinical_significance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(drug1_name, drug2_name)
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_drug1 ON drug_interactions(drug1_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_drug2 ON drug_interactions(drug2_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON drug_interactions(interaction_severity)')
        
        self.conn.commit()
        print("✅ Drug interactions tables created successfully")
    
    def populate_interactions(self):
        """Populate the database with realistic drug interaction data."""
        
        # Comprehensive drug interaction data based on real medical literature
        interactions = [
            # Anticoagulant interactions (Very common and dangerous)
            {
                "drug1": "Warfarin", "drug2": "Aspirin", "severity": "severe",
                "description": "Increased risk of bleeding due to synergistic anticoagulant effects",
                "symptoms": "Unusual bleeding, bruising, nosebleeds, blood in urine/stool",
                "recommendation": "Avoid combination if possible. If necessary, monitor INR closely and reduce doses",
                "mechanism": "Synergistic anticoagulant effects",
                "clinical_significance": "Major interaction requiring close monitoring"
            },
            {
                "drug1": "Warfarin", "drug2": "Amoxicillin", "severity": "moderate",
                "description": "Antibiotics may potentiate warfarin effect by reducing vitamin K producing bacteria",
                "symptoms": "Increased bleeding tendency, elevated INR",
                "recommendation": "Monitor INR more frequently during antibiotic course",
                "mechanism": "Reduced vitamin K synthesis by gut bacteria",
                "clinical_significance": "Moderate interaction requiring monitoring"
            },
            {
                "drug1": "Warfarin", "drug2": "Azithromycin", "severity": "moderate",
                "description": "Macrolide antibiotics can increase warfarin levels",
                "symptoms": "Increased bleeding risk, elevated INR",
                "recommendation": "Monitor INR closely, consider dose adjustment",
                "mechanism": "CYP450 enzyme inhibition",
                "clinical_significance": "Moderate interaction"
            },
            
            # Antibiotic interactions
            {
                "drug1": "Amoxicillin", "drug2": "Atenolol", "severity": "mild",
                "description": "Minimal interaction, may slightly reduce antibiotic absorption",
                "symptoms": "Possible reduced antibiotic effectiveness",
                "recommendation": "Take medications 2 hours apart",
                "mechanism": "Possible chelation or absorption interference",
                "clinical_significance": "Minor interaction"
            },
            {
                "drug1": "Ciprofloxacin", "drug2": "Calcium", "severity": "moderate",
                "description": "Calcium significantly reduces ciprofloxacin absorption",
                "symptoms": "Reduced antibiotic effectiveness, treatment failure",
                "recommendation": "Take ciprofloxacin 2 hours before or 6 hours after calcium",
                "mechanism": "Chelation complex formation",
                "clinical_significance": "Moderate interaction affecting efficacy"
            },
            {
                "drug1": "Azithromycin", "drug2": "Aluminum", "severity": "moderate",
                "description": "Aluminum antacids reduce azithromycin absorption",
                "symptoms": "Decreased antibiotic levels, potential treatment failure",
                "recommendation": "Separate administration by at least 2 hours",
                "mechanism": "Chelation complex formation",
                "clinical_significance": "Moderate interaction"
            },
            
            # Cardiovascular drug interactions
            {
                "drug1": "Atenolol", "drug2": "Amlodipine", "severity": "mild",
                "description": "Synergistic blood pressure lowering effect",
                "symptoms": "Excessive hypotension, dizziness, fatigue",
                "recommendation": "Monitor blood pressure closely, adjust doses if needed",
                "mechanism": "Additive cardiovascular effects",
                "clinical_significance": "Minor interaction, often therapeutic"
            },
            {
                "drug1": "Atorvastatin", "drug2": "Amlodipine", "severity": "moderate",
                "description": "Amlodipine increases atorvastatin levels",
                "symptoms": "Increased risk of muscle pain, rhabdomyolysis",
                "recommendation": "Consider lower atorvastatin dose, monitor for muscle symptoms",
                "mechanism": "CYP3A4 inhibition",
                "clinical_significance": "Moderate interaction"
            },
            {
                "drug1": "Aspirin", "drug2": "Atenolol", "severity": "mild",
                "description": "Aspirin may reduce antihypertensive effect of beta-blockers",
                "symptoms": "Reduced blood pressure control",
                "recommendation": "Monitor blood pressure, may need dose adjustment",
                "mechanism": "Prostaglandin synthesis inhibition",
                "clinical_significance": "Minor interaction"
            },
            
            # Psychiatric medication interactions
            {
                "drug1": "Alprazolam", "drug2": "Azithromycin", "severity": "moderate",
                "description": "Azithromycin may increase alprazolam levels",
                "symptoms": "Increased sedation, confusion, respiratory depression",
                "recommendation": "Monitor for increased benzodiazepine effects, consider dose reduction",
                "mechanism": "CYP3A4 inhibition",
                "clinical_significance": "Moderate interaction"
            },
            {
                "drug1": "Aripiprazole", "drug2": "Azithromycin", "severity": "moderate",
                "description": "Potential increased risk of QT prolongation",
                "symptoms": "Cardiac arrhythmias, dizziness, fainting",
                "recommendation": "Monitor ECG if combination necessary",
                "mechanism": "Additive QT prolongation",
                "clinical_significance": "Moderate cardiac risk"
            },
            
            # Antifungal interactions
            {
                "drug1": "Amphotericin", "drug2": "Amiloride", "severity": "severe",
                "description": "Increased risk of severe nephrotoxicity",
                "symptoms": "Kidney damage, elevated creatinine, electrolyte imbalances",
                "recommendation": "Avoid combination if possible, monitor kidney function closely",
                "mechanism": "Additive nephrotoxic effects",
                "clinical_significance": "Major interaction"
            },
            {
                "drug1": "Caspofungin", "drug2": "Atorvastatin", "severity": "mild",
                "description": "Possible increased statin levels",
                "symptoms": "Muscle pain, weakness",
                "recommendation": "Monitor for muscle symptoms",
                "mechanism": "Possible enzyme inhibition",
                "clinical_significance": "Minor interaction"
            },
            
            # Antihistamine interactions
            {
                "drug1": "Cetirizine", "drug2": "Alprazolam", "severity": "moderate",
                "description": "Increased sedation and CNS depression",
                "symptoms": "Excessive drowsiness, impaired coordination, confusion",
                "recommendation": "Avoid driving, reduce doses if necessary",
                "mechanism": "Additive CNS depressant effects",
                "clinical_significance": "Moderate interaction"
            },
            {
                "drug1": "Bilastine", "drug2": "Azithromycin", "severity": "mild",
                "description": "Minimal interaction potential",
                "symptoms": "None expected",
                "recommendation": "No special precautions needed",
                "mechanism": "No significant interaction",
                "clinical_significance": "Minimal interaction"
            },
            
            # Gastrointestinal drug interactions
            {
                "drug1": "Bisacodyl", "drug2": "Calcium", "severity": "mild",
                "description": "Calcium may reduce laxative effectiveness",
                "symptoms": "Reduced bowel movement, constipation",
                "recommendation": "Take calcium 2 hours after laxative",
                "mechanism": "Ionic binding interference",
                "clinical_significance": "Minor interaction"
            },
            
            # Diuretic interactions
            {
                "drug1": "Bumetanide", "drug2": "Amiloride", "severity": "moderate",
                "description": "Risk of electrolyte imbalances",
                "symptoms": "Potassium abnormalities, dehydration, kidney dysfunction",
                "recommendation": "Monitor electrolytes and kidney function regularly",
                "mechanism": "Opposing effects on potassium",
                "clinical_significance": "Moderate interaction"
            },
            
            # Anticoagulant combinations (very important)
            {
                "drug1": "Apixaban", "drug2": "Aspirin", "severity": "severe",
                "description": "Significantly increased bleeding risk",
                "symptoms": "Severe bleeding, hemorrhage, bruising",
                "recommendation": "Avoid combination unless absolutely necessary, monitor closely",
                "mechanism": "Additive anticoagulant effects",
                "clinical_significance": "Major bleeding risk"
            },
            {
                "drug1": "Argatroban", "drug2": "Warfarin", "severity": "contraindicated",
                "description": "Extremely high bleeding risk with dual anticoagulation",
                "symptoms": "Life-threatening bleeding, hemorrhage",
                "recommendation": "Do not combine. Use only during transition periods under strict monitoring",
                "mechanism": "Dual anticoagulation",
                "clinical_significance": "Contraindicated combination"
            },
            
            # Steroid interactions
            {
                "drug1": "Betamethasone", "drug2": "Aspirin", "severity": "moderate",
                "description": "Increased risk of gastrointestinal bleeding",
                "symptoms": "Stomach pain, blood in stool, nausea",
                "recommendation": "Use gastroprotective agents, monitor for GI bleeding",
                "mechanism": "Additive GI irritation",
                "clinical_significance": "Moderate GI risk"
            },
            {
                "drug1": "Budesonide", "drug2": "Azithromycin", "severity": "mild",
                "description": "Possible increased steroid levels",
                "symptoms": "Increased steroid side effects",
                "recommendation": "Monitor for steroid side effects",
                "mechanism": "CYP3A4 inhibition",
                "clinical_significance": "Minor interaction"
            },
            
            # Additional important interactions
            {
                "drug1": "Bupropion", "drug2": "Alprazolam", "severity": "moderate",
                "description": "Bupropion may reduce alprazolam effectiveness",
                "symptoms": "Reduced anxiety control, potential seizure risk",
                "recommendation": "Monitor therapeutic response, avoid in seizure-prone patients",
                "mechanism": "CYP450 induction and seizure threshold lowering",
                "clinical_significance": "Moderate interaction"
            },
            {
                "drug1": "Candesartan", "drug2": "Amiloride", "severity": "moderate",
                "description": "Risk of hyperkalemia",
                "symptoms": "High potassium levels, cardiac arrhythmias, muscle weakness",
                "recommendation": "Monitor potassium levels regularly",
                "mechanism": "Additive potassium-sparing effects",
                "clinical_significance": "Moderate electrolyte risk"
            },
            {
                "drug1": "Cephalexin", "drug2": "Warfarin", "severity": "moderate",
                "description": "Possible potentiation of anticoagulant effect",
                "symptoms": "Increased bleeding risk, elevated INR",
                "recommendation": "Monitor INR more frequently during antibiotic course",
                "mechanism": "Altered gut flora affecting vitamin K",
                "clinical_significance": "Moderate interaction"
            }
        ]
        
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM drug_interactions')
        
        # Insert interaction data
        for interaction in interactions:
            try:
                cursor.execute('''
                    INSERT INTO drug_interactions 
                    (drug1_name, drug2_name, interaction_severity, description, symptoms, 
                     recommendation, mechanism, clinical_significance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction["drug1"], interaction["drug2"], interaction["severity"],
                    interaction["description"], interaction["symptoms"], interaction["recommendation"],
                    interaction["mechanism"], interaction["clinical_significance"]
                ))
                
                # Also insert the reverse combination for bidirectional lookup
                if interaction["drug1"] != interaction["drug2"]:
                    cursor.execute('''
                        INSERT OR IGNORE INTO drug_interactions 
                        (drug1_name, drug2_name, interaction_severity, description, symptoms, 
                         recommendation, mechanism, clinical_significance)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        interaction["drug2"], interaction["drug1"], interaction["severity"],
                        interaction["description"], interaction["symptoms"], interaction["recommendation"],
                        interaction["mechanism"], interaction["clinical_significance"]
                    ))
                
            except sqlite3.IntegrityError:
                # Skip duplicates
                pass
        
        self.conn.commit()
        
        # Get count of inserted interactions
        cursor.execute('SELECT COUNT(*) FROM drug_interactions')
        count = cursor.fetchone()[0]
        print(f"✅ Inserted {count} drug interactions")
    
    def check_interactions(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Check for interactions between two drugs."""
        if not self.conn:
            return None
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM drug_interactions 
            WHERE (drug1_name = ? AND drug2_name = ?) OR (drug1_name = ? AND drug2_name = ?)
        ''', (drug1, drug2, drug2, drug1))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None
    
    def check_multiple_interactions(self, drug_list: List[str]) -> List[Dict]:
        """Check for interactions among multiple drugs."""
        interactions = []
        
        for i in range(len(drug_list)):
            for j in range(i + 1, len(drug_list)):
                interaction = self.check_interactions(drug_list[i], drug_list[j])
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def get_drug_interactions(self, drug_name: str) -> List[Dict]:
        """Get all known interactions for a specific drug."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM drug_interactions 
            WHERE drug1_name = ? OR drug2_name = ?
            ORDER BY interaction_severity DESC
        ''', (drug_name, drug_name))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_severe_interactions(self) -> List[Dict]:
        """Get all severe and contraindicated interactions."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM drug_interactions 
            WHERE interaction_severity IN ('severe', 'contraindicated')
            ORDER BY interaction_severity DESC, drug1_name
        ''')
        
        return [dict(row) for row in cursor.fetchall()]


def create_drug_interactions_database():
    """Create and populate the drug interactions database."""
    print("🔄 Creating drug interactions database...")
    
    db = DrugInteractionsManager()
    if db.connect():
        db.create_tables()
        db.populate_interactions()
        
        # Test the database
        print("\n📊 Database Statistics:")
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM drug_interactions")
        total_interactions = cursor.fetchone()[0]
        print(f"  Total interactions: {total_interactions}")
        
        cursor.execute("SELECT interaction_severity, COUNT(*) FROM drug_interactions GROUP BY interaction_severity")
        severity_counts = cursor.fetchall()
        for severity, count in severity_counts:
            print(f"  {severity.capitalize()}: {count}")
        
        # Test some lookups
        print("\n🧪 Testing lookups:")
        test_interaction = db.check_interactions("Warfarin", "Aspirin")
        if test_interaction:
            print(f"  ✅ Warfarin + Aspirin: {test_interaction['interaction_severity']} - {test_interaction['description'][:50]}...")
        
        multi_test = db.check_multiple_interactions(["Warfarin", "Aspirin", "Atenolol"])
        print(f"  ✅ Multi-drug check found {len(multi_test)} interactions")
        
        db.close()
        print("✅ Drug interactions database created successfully!")
        return True
    else:
        print("❌ Failed to create drug interactions database")
        return False


if __name__ == "__main__":
    create_drug_interactions_database() 