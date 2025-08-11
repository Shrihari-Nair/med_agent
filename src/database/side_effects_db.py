"""
Side Effects Database Manager
Creates and manages adverse reaction tracking for medicines.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class SideEffectsManager:
    """Manages side effects database for adverse reaction tracking."""
    
    def __init__(self, db_path: str = "data/side_effects.db"):
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
        """Create the side effects tables."""
        cursor = self.conn.cursor()
        
        # Create side_effects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS side_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL,
                side_effect TEXT NOT NULL,
                frequency_percentage REAL,
                frequency_category TEXT CHECK (frequency_category IN ('very_common', 'common', 'uncommon', 'rare', 'very_rare')),
                severity TEXT CHECK (severity IN ('mild', 'moderate', 'severe', 'life_threatening')),
                onset_timing TEXT,
                affected_population TEXT,
                description TEXT,
                management_advice TEXT,
                when_to_seek_help TEXT,
                reversible BOOLEAN,
                dose_related BOOLEAN,
                system_affected TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(medicine_name, side_effect)
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_side_effects_medicine ON side_effects(medicine_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_side_effects_severity ON side_effects(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_side_effects_frequency ON side_effects(frequency_category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_side_effects_system ON side_effects(system_affected)')
        
        self.conn.commit()
        print("✅ Side effects tables created successfully")
    
    def populate_side_effects(self):
        """Populate the database with comprehensive side effects data."""
        
        # Comprehensive side effects data based on medical literature
        side_effects_data = [
            # Aspirin side effects
            {
                "medicine": "Aspirin", "effect": "Gastrointestinal upset", "frequency": 15.0, "category": "common",
                "severity": "mild", "onset": "Within hours", "population": "All ages",
                "description": "Stomach pain, nausea, indigestion, heartburn",
                "management": "Take with food or milk, use enteric-coated formulation",
                "seek_help": "If severe stomach pain or black stools", "reversible": True, "dose_related": True,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Aspirin", "effect": "Increased bleeding risk", "frequency": 8.0, "category": "common",
                "severity": "moderate", "onset": "Days to weeks", "population": "All ages",
                "description": "Easy bruising, prolonged bleeding from cuts, nosebleeds",
                "management": "Avoid other blood thinners, inform healthcare providers",
                "seek_help": "If unusual bleeding or bruising", "reversible": True, "dose_related": True,
                "system": "Hematologic"
            },
            {
                "medicine": "Aspirin", "effect": "Ringing in ears (tinnitus)", "frequency": 5.0, "category": "common",
                "severity": "mild", "onset": "Hours to days", "population": "High-dose users",
                "description": "Ringing, buzzing, or humming in ears",
                "management": "Reduce dose if possible, usually dose-related",
                "seek_help": "If hearing loss accompanies tinnitus", "reversible": True, "dose_related": True,
                "system": "Neurological"
            },
            {
                "medicine": "Aspirin", "effect": "Reye's syndrome", "frequency": 0.01, "category": "very_rare",
                "severity": "life_threatening", "onset": "Days", "population": "Children under 16",
                "description": "Brain and liver damage in children with viral infections",
                "management": "CONTRAINDICATED in children under 16 with viral infections",
                "seek_help": "Emergency medical attention needed", "reversible": False, "dose_related": False,
                "system": "Neurological"
            },
            
            # Amoxicillin side effects
            {
                "medicine": "Amoxicillin", "effect": "Diarrhea", "frequency": 12.0, "category": "common",
                "severity": "mild", "onset": "Days", "population": "All ages",
                "description": "Loose, watery stools due to altered gut bacteria",
                "management": "Stay hydrated, probiotics may help",
                "seek_help": "If severe, bloody, or persistent", "reversible": True, "dose_related": False,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Amoxicillin", "effect": "Nausea and vomiting", "frequency": 8.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Stomach upset, nausea, occasional vomiting",
                "management": "Take with food, smaller frequent doses",
                "seek_help": "If unable to keep fluids down", "reversible": True, "dose_related": True,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Amoxicillin", "effect": "Skin rash", "frequency": 5.0, "category": "common",
                "severity": "mild", "onset": "Days", "population": "All ages",
                "description": "Red, itchy skin rash, may be allergic reaction",
                "management": "Discontinue medication, antihistamines for itching",
                "seek_help": "Immediately if breathing difficulties or swelling", "reversible": True, "dose_related": False,
                "system": "Dermatologic"
            },
            {
                "medicine": "Amoxicillin", "effect": "Allergic reaction", "frequency": 1.0, "category": "uncommon",
                "severity": "severe", "onset": "Minutes to hours", "population": "Penicillin-allergic patients",
                "description": "Hives, swelling, difficulty breathing, anaphylaxis",
                "management": "Discontinue immediately, epinephrine if severe",
                "seek_help": "Emergency medical attention if breathing problems", "reversible": True, "dose_related": False,
                "system": "Immunologic"
            },
            
            # Atenolol side effects
            {
                "medicine": "Atenolol", "effect": "Fatigue", "frequency": 20.0, "category": "common",
                "severity": "mild", "onset": "Days to weeks", "population": "All ages",
                "description": "Tiredness, lack of energy, reduced exercise tolerance",
                "management": "Usually improves with time, adjust timing of dose",
                "seek_help": "If severely limiting daily activities", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            {
                "medicine": "Atenolol", "effect": "Cold hands and feet", "frequency": 15.0, "category": "common",
                "severity": "mild", "onset": "Days", "population": "All ages",
                "description": "Reduced circulation to extremities",
                "management": "Wear warm clothing, avoid cold exposure",
                "seek_help": "If severe pain or color changes in fingers/toes", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            {
                "medicine": "Atenolol", "effect": "Dizziness", "frequency": 10.0, "category": "common",
                "severity": "mild", "onset": "Hours to days", "population": "All ages",
                "description": "Lightheadedness, especially when standing",
                "management": "Rise slowly from sitting/lying position",
                "seek_help": "If fainting or severe dizziness", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            {
                "medicine": "Atenolol", "effect": "Depression", "frequency": 3.0, "category": "uncommon",
                "severity": "moderate", "onset": "Weeks to months", "population": "Elderly, predisposed individuals",
                "description": "Mood changes, sadness, loss of interest",
                "management": "Monitor mood, consider alternative medication",
                "seek_help": "If thoughts of self-harm", "reversible": True, "dose_related": False,
                "system": "Neurological"
            },
            
            # Azithromycin side effects
            {
                "medicine": "Azithromycin", "effect": "Nausea", "frequency": 12.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Stomach upset, nausea, mild abdominal discomfort",
                "management": "Take with food if stomach upset occurs",
                "seek_help": "If unable to keep medication down", "reversible": True, "dose_related": True,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Azithromycin", "effect": "Diarrhea", "frequency": 8.0, "category": "common",
                "severity": "mild", "onset": "Days", "population": "All ages",
                "description": "Loose stools due to changes in gut bacteria",
                "management": "Stay hydrated, probiotics may help",
                "seek_help": "If severe, bloody, or persistent", "reversible": True, "dose_related": False,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Azithromycin", "effect": "QT prolongation", "frequency": 2.0, "category": "uncommon",
                "severity": "severe", "onset": "Hours to days", "population": "Cardiac patients, elderly",
                "description": "Abnormal heart rhythm that can be dangerous",
                "management": "Monitor ECG in high-risk patients",
                "seek_help": "If palpitations, dizziness, or fainting", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            
            # Alprazolam side effects
            {
                "medicine": "Alprazolam", "effect": "Drowsiness", "frequency": 35.0, "category": "very_common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Sedation, sleepiness, reduced alertness",
                "management": "Avoid driving, start with low doses",
                "seek_help": "If excessive sedation interferes with safety", "reversible": True, "dose_related": True,
                "system": "Neurological"
            },
            {
                "medicine": "Alprazolam", "effect": "Memory problems", "frequency": 15.0, "category": "common",
                "severity": "moderate", "onset": "Hours to days", "population": "All ages",
                "description": "Short-term memory impairment, forgetfulness",
                "management": "Use lowest effective dose, monitor closely",
                "seek_help": "If severe memory problems", "reversible": True, "dose_related": True,
                "system": "Neurological"
            },
            {
                "medicine": "Alprazolam", "effect": "Dependence and withdrawal", "frequency": 25.0, "category": "common",
                "severity": "severe", "onset": "Weeks to months", "population": "Long-term users",
                "description": "Physical dependence, withdrawal symptoms when stopping",
                "management": "Taper slowly, never stop abruptly",
                "seek_help": "If withdrawal symptoms occur", "reversible": True, "dose_related": True,
                "system": "Neurological"
            },
            {
                "medicine": "Alprazolam", "effect": "Confusion", "frequency": 8.0, "category": "common",
                "severity": "moderate", "onset": "Hours", "population": "Elderly",
                "description": "Disorientation, difficulty thinking clearly",
                "management": "Use lower doses in elderly, monitor closely",
                "seek_help": "If severe confusion or agitation", "reversible": True, "dose_related": True,
                "system": "Neurological"
            },
            
            # Cetirizine side effects
            {
                "medicine": "Cetirizine", "effect": "Drowsiness", "frequency": 14.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Mild sedation, sleepiness",
                "management": "Take at bedtime, avoid alcohol",
                "seek_help": "If severely impairs daily activities", "reversible": True, "dose_related": True,
                "system": "Neurological"
            },
            {
                "medicine": "Cetirizine", "effect": "Dry mouth", "frequency": 6.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Reduced saliva production, thirst",
                "management": "Stay hydrated, sugar-free gum may help",
                "seek_help": "If severe or causing dental problems", "reversible": True, "dose_related": True,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Cetirizine", "effect": "Headache", "frequency": 5.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Mild to moderate headache",
                "management": "Adequate hydration, pain relievers if needed",
                "seek_help": "If severe or persistent headaches", "reversible": True, "dose_related": False,
                "system": "Neurological"
            },
            
            # Amlodipine side effects
            {
                "medicine": "Amlodipine", "effect": "Ankle swelling", "frequency": 18.0, "category": "common",
                "severity": "mild", "onset": "Days to weeks", "population": "All ages",
                "description": "Fluid retention in ankles and feet",
                "management": "Elevate feet, compression stockings",
                "seek_help": "If severe swelling or breathing difficulties", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            {
                "medicine": "Amlodipine", "effect": "Dizziness", "frequency": 12.0, "category": "common",
                "severity": "mild", "onset": "Hours to days", "population": "All ages",
                "description": "Lightheadedness, especially when standing",
                "management": "Rise slowly, stay hydrated",
                "seek_help": "If fainting or severe dizziness", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            {
                "medicine": "Amlodipine", "effect": "Flushing", "frequency": 8.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Facial redness, feeling of warmth",
                "management": "Usually temporary, avoid triggers",
                "seek_help": "If accompanied by difficulty breathing", "reversible": True, "dose_related": True,
                "system": "Cardiovascular"
            },
            
            # Ciprofloxacin side effects
            {
                "medicine": "Ciprofloxacin", "effect": "Tendon rupture", "frequency": 0.1, "category": "rare",
                "severity": "severe", "onset": "Days to months", "population": "Elderly, corticosteroid users",
                "description": "Achilles tendon rupture, other tendon damage",
                "management": "Discontinue immediately, avoid exercise",
                "seek_help": "Immediately if sudden tendon pain", "reversible": False, "dose_related": False,
                "system": "Musculoskeletal"
            },
            {
                "medicine": "Ciprofloxacin", "effect": "Nausea", "frequency": 15.0, "category": "common",
                "severity": "mild", "onset": "Hours", "population": "All ages",
                "description": "Stomach upset, nausea, abdominal discomfort",
                "management": "Take with food, stay hydrated",
                "seek_help": "If severe vomiting or unable to keep fluids down", "reversible": True, "dose_related": True,
                "system": "Gastrointestinal"
            },
            {
                "medicine": "Ciprofloxacin", "effect": "Photosensitivity", "frequency": 5.0, "category": "common",
                "severity": "moderate", "onset": "Hours", "population": "All ages",
                "description": "Increased sensitivity to sunlight, sunburn",
                "management": "Avoid sun exposure, use sunscreen",
                "seek_help": "If severe burns or blistering", "reversible": True, "dose_related": False,
                "system": "Dermatologic"
            },
            
            # Atorvastatin side effects
            {
                "medicine": "Atorvastatin", "effect": "Muscle pain", "frequency": 10.0, "category": "common",
                "severity": "mild", "onset": "Weeks", "population": "All ages",
                "description": "Muscle aches, pain, weakness",
                "management": "Monitor CK levels, CoQ10 supplements may help",
                "seek_help": "If severe muscle pain or weakness", "reversible": True, "dose_related": True,
                "system": "Musculoskeletal"
            },
            {
                "medicine": "Atorvastatin", "effect": "Liver enzyme elevation", "frequency": 3.0, "category": "uncommon",
                "severity": "moderate", "onset": "Weeks to months", "population": "All ages",
                "description": "Elevated liver function tests",
                "management": "Monitor liver function regularly",
                "seek_help": "If symptoms of liver problems", "reversible": True, "dose_related": True,
                "system": "Hepatic"
            },
            {
                "medicine": "Atorvastatin", "effect": "Rhabdomyolysis", "frequency": 0.01, "category": "very_rare",
                "severity": "life_threatening", "onset": "Weeks to months", "population": "High-dose users, drug interactions",
                "description": "Severe muscle breakdown, kidney damage",
                "management": "Discontinue immediately, hospitalization may be needed",
                "seek_help": "Emergency care if severe muscle pain and dark urine", "reversible": True, "dose_related": True,
                "system": "Musculoskeletal"
            },
            
            # Budesonide side effects
            {
                "medicine": "Budesonide", "effect": "Oral thrush", "frequency": 8.0, "category": "common",
                "severity": "mild", "onset": "Days to weeks", "population": "All ages",
                "description": "Fungal infection in mouth and throat",
                "management": "Rinse mouth after use, antifungal treatment",
                "seek_help": "If white patches in mouth or throat pain", "reversible": True, "dose_related": True,
                "system": "Infectious"
            },
            {
                "medicine": "Budesonide", "effect": "Hoarse voice", "frequency": 12.0, "category": "common",
                "severity": "mild", "onset": "Days", "population": "All ages",
                "description": "Voice changes, hoarseness",
                "management": "Rinse mouth after use, voice rest",
                "seek_help": "If persistent voice changes", "reversible": True, "dose_related": True,
                "system": "Respiratory"
            },
            {
                "medicine": "Budesonide", "effect": "Growth suppression", "frequency": 5.0, "category": "common",
                "severity": "moderate", "onset": "Months", "population": "Children",
                "description": "Reduced growth rate in children",
                "management": "Monitor growth regularly, use lowest effective dose",
                "seek_help": "If significant growth retardation", "reversible": True, "dose_related": True,
                "system": "Endocrine"
            }
        ]
        
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM side_effects')
        
        # Insert side effects data
        for effect in side_effects_data:
            cursor.execute('''
                INSERT INTO side_effects 
                (medicine_name, side_effect, frequency_percentage, frequency_category, severity,
                 onset_timing, affected_population, description, management_advice, 
                 when_to_seek_help, reversible, dose_related, system_affected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                effect["medicine"], effect["effect"], effect["frequency"], effect["category"],
                effect["severity"], effect["onset"], effect["population"], effect["description"],
                effect["management"], effect["seek_help"], effect["reversible"], 
                effect["dose_related"], effect["system"]
            ))
        
        self.conn.commit()
        
        # Get count
        cursor.execute('SELECT COUNT(*) FROM side_effects')
        count = cursor.fetchone()[0]
        print(f"✅ Inserted {count} side effects")
    
    def get_side_effects_for_medicine(self, medicine_name: str) -> List[Dict]:
        """Get all side effects for a specific medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM side_effects 
            WHERE medicine_name = ?
            ORDER BY frequency_percentage DESC
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_common_side_effects(self, medicine_name: str) -> List[Dict]:
        """Get common side effects (≥5% frequency) for a medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM side_effects 
            WHERE medicine_name = ? AND frequency_percentage >= 5.0
            ORDER BY frequency_percentage DESC
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_severe_side_effects(self, medicine_name: str) -> List[Dict]:
        """Get severe and life-threatening side effects for a medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM side_effects 
            WHERE medicine_name = ? AND severity IN ('severe', 'life_threatening')
            ORDER BY severity DESC, frequency_percentage DESC
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pediatric_concerns(self, medicine_name: str) -> List[Dict]:
        """Get side effects of particular concern in children."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM side_effects 
            WHERE medicine_name = ? 
            AND (affected_population LIKE '%child%' OR affected_population LIKE '%pediatric%'
                 OR side_effect LIKE '%growth%' OR side_effect LIKE '%development%'
                 OR side_effect = 'Reye''s syndrome')
            ORDER BY severity DESC, frequency_percentage DESC
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_side_effects_by_symptom(self, symptom: str) -> List[Dict]:
        """Search for medicines that could cause a specific symptom."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM side_effects 
            WHERE side_effect LIKE ? OR description LIKE ?
            ORDER BY frequency_percentage DESC
        ''', (f'%{symptom}%', f'%{symptom}%'))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_side_effects_summary(self, medicine_name: str) -> Dict:
        """Get a summary of side effects for a medicine."""
        if not self.conn:
            return {}
        
        all_effects = self.get_side_effects_for_medicine(medicine_name)
        if not all_effects:
            return {"medicine": medicine_name, "total_effects": 0}
        
        # Categorize by frequency
        very_common = [e for e in all_effects if e['frequency_category'] == 'very_common']
        common = [e for e in all_effects if e['frequency_category'] == 'common']
        uncommon = [e for e in all_effects if e['frequency_category'] == 'uncommon']
        rare = [e for e in all_effects if e['frequency_category'] in ['rare', 'very_rare']]
        
        # Categorize by severity
        severe = [e for e in all_effects if e['severity'] in ['severe', 'life_threatening']]
        
        return {
            "medicine": medicine_name,
            "total_effects": len(all_effects),
            "very_common": len(very_common),
            "common": len(common),
            "uncommon": len(uncommon),
            "rare": len(rare),
            "severe_effects": len(severe),
            "most_common_effects": [e['side_effect'] for e in all_effects[:3]],
            "severe_effects_list": [e['side_effect'] for e in severe]
        }


def create_side_effects_database():
    """Create and populate the side effects database."""
    print("🔄 Creating side effects database...")
    
    db = SideEffectsManager()
    if db.connect():
        db.create_tables()
        db.populate_side_effects()
        
        # Test the database
        print("\n📊 Database Statistics:")
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM side_effects")
        total_effects = cursor.fetchone()[0]
        print(f"  Total side effects: {total_effects}")
        
        cursor.execute("SELECT medicine_name, COUNT(*) FROM side_effects GROUP BY medicine_name ORDER BY COUNT(*) DESC")
        medicine_counts = cursor.fetchall()
        print("\n💊 Side effects by medicine:")
        for medicine, count in medicine_counts:
            print(f"  {medicine}: {count} side effects")
        
        cursor.execute("SELECT severity, COUNT(*) FROM side_effects GROUP BY severity ORDER BY COUNT(*) DESC")
        severity_counts = cursor.fetchall()
        print("\n⚠️ Side effects by severity:")
        for severity, count in severity_counts:
            print(f"  {severity}: {count}")
        
        cursor.execute("SELECT frequency_category, COUNT(*) FROM side_effects GROUP BY frequency_category ORDER BY COUNT(*) DESC")
        frequency_counts = cursor.fetchall()
        print("\n📈 Side effects by frequency:")
        for frequency, count in frequency_counts:
            print(f"  {frequency}: {count}")
        
        # Test some lookups
        print("\n🧪 Testing lookups:")
        
        aspirin_effects = db.get_common_side_effects("Aspirin")
        print(f"  ✅ Aspirin common side effects: {len(aspirin_effects)} found")
        if aspirin_effects:
            print(f"      Most common: {aspirin_effects[0]['side_effect']} ({aspirin_effects[0]['frequency_percentage']}%)")
        
        severe_effects = db.get_severe_side_effects("Aspirin")
        print(f"  ✅ Aspirin severe side effects: {len(severe_effects)} found")
        
        pediatric_concerns = db.get_pediatric_concerns("Aspirin")
        print(f"  ✅ Aspirin pediatric concerns: {len(pediatric_concerns)} found")
        
        summary = db.get_side_effects_summary("Alprazolam")
        print(f"  ✅ Alprazolam summary: {summary['total_effects']} total effects, {summary['severe_effects']} severe")
        
        db.close()
        print("✅ Side effects database created successfully!")
        return True
    else:
        print("❌ Failed to create side effects database")
        return False


if __name__ == "__main__":
    create_side_effects_database() 