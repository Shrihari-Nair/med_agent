"""
Dosage Guidelines Database Manager
Creates and manages age/weight-specific dosing information for medicines.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DosageGuidelinesManager:
    """Manages dosage guidelines database for age/weight-specific dosing."""
    
    def __init__(self, db_path: str = "data/dosage.db"):
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
        """Create the dosage guidelines tables."""
        cursor = self.conn.cursor()
        
        # Create dosage_guidelines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dosage_guidelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL,
                age_group TEXT NOT NULL,
                min_age_months INTEGER,
                max_age_months INTEGER,
                min_weight_kg REAL,
                max_weight_kg REAL,
                recommended_dose TEXT NOT NULL,
                max_daily_dose TEXT,
                frequency TEXT,
                administration_method TEXT,
                special_instructions TEXT,
                contraindications TEXT,
                renal_adjustment TEXT,
                hepatic_adjustment TEXT,
                indication TEXT,
                evidence_level TEXT CHECK (evidence_level IN ('high', 'moderate', 'low', 'expert_opinion')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dosage_medicine ON dosage_guidelines(medicine_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dosage_age_group ON dosage_guidelines(age_group)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dosage_age_range ON dosage_guidelines(min_age_months, max_age_months)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dosage_weight_range ON dosage_guidelines(min_weight_kg, max_weight_kg)')
        
        self.conn.commit()
        print("✅ Dosage guidelines tables created successfully")
    
    def populate_dosage_guidelines(self):
        """Populate the database with comprehensive dosage guidelines."""
        
        # Comprehensive dosage guidelines data
        dosage_data = [
            # Aspirin - Age-specific dosing (important for children)
            {
                "medicine": "Aspirin", "age_group": "Infants (0-2 years)", 
                "min_age": 0, "max_age": 24, "min_weight": 3, "max_weight": 12,
                "dose": "CONTRAINDICATED", "max_daily": "DO NOT USE", "frequency": "N/A",
                "method": "N/A", "indication": "All indications",
                "special": "Risk of Reye's syndrome in children under 16",
                "contraindications": "Viral infections, fever, all indications under 16 years",
                "evidence": "high"
            },
            {
                "medicine": "Aspirin", "age_group": "Children (2-16 years)", 
                "min_age": 24, "max_age": 192, "min_weight": 12, "max_weight": 50,
                "dose": "CONTRAINDICATED", "max_daily": "DO NOT USE", "frequency": "N/A",
                "method": "N/A", "indication": "All indications",
                "special": "Risk of Reye's syndrome",
                "contraindications": "All indications under 16 years",
                "evidence": "high"
            },
            {
                "medicine": "Aspirin", "age_group": "Adults (16+ years)", 
                "min_age": 192, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "75-100mg daily (cardioprotection) or 325-650mg q4-6h (pain/fever)", 
                "max_daily": "4g", "frequency": "Daily to QID",
                "method": "Oral with food", "indication": "Cardioprotection, pain, fever",
                "special": "Take with food to reduce GI irritation",
                "contraindications": "Active bleeding, severe liver disease",
                "evidence": "high"
            },
            {
                "medicine": "Aspirin", "age_group": "Elderly (65+ years)", 
                "min_age": 780, "max_age": 1500, "min_weight": 45, "max_weight": 120,
                "dose": "75-81mg daily (cardioprotection) or 325mg q6h (pain)", 
                "max_daily": "2.4g", "frequency": "Daily to QID",
                "method": "Oral with food", "indication": "Cardioprotection, pain",
                "special": "Increased bleeding risk, monitor closely",
                "contraindications": "Active bleeding, falls risk",
                "evidence": "high"
            },
            
            # Amoxicillin - Comprehensive age/weight dosing
            {
                "medicine": "Amoxicillin", "age_group": "Infants (0-3 months)", 
                "min_age": 0, "max_age": 3, "min_weight": 3, "max_weight": 6,
                "dose": "20-30mg/kg/day divided q12h", "max_daily": "30mg/kg/day", 
                "frequency": "Every 12 hours", "method": "Oral suspension",
                "indication": "Bacterial infections", "special": "Monitor for rash, diarrhea",
                "contraindications": "Penicillin allergy", "evidence": "high"
            },
            {
                "medicine": "Amoxicillin", "age_group": "Infants (3-12 months)", 
                "min_age": 3, "max_age": 12, "min_weight": 6, "max_weight": 10,
                "dose": "40-45mg/kg/day divided q8h", "max_daily": "45mg/kg/day", 
                "frequency": "Every 8 hours", "method": "Oral suspension",
                "indication": "Bacterial infections", "special": "Monitor for rash, diarrhea",
                "contraindications": "Penicillin allergy", "evidence": "high"
            },
            {
                "medicine": "Amoxicillin", "age_group": "Children (1-12 years)", 
                "min_age": 12, "max_age": 144, "min_weight": 10, "max_weight": 40,
                "dose": "25-45mg/kg/day divided q8h (mild) or 80-90mg/kg/day (severe)", 
                "max_daily": "90mg/kg/day or 3g", "frequency": "Every 8 hours",
                "method": "Oral suspension or chewable tablets", "indication": "Bacterial infections",
                "special": "Higher doses for resistant organisms",
                "contraindications": "Penicillin allergy", "evidence": "high"
            },
            {
                "medicine": "Amoxicillin", "age_group": "Adults", 
                "min_age": 144, "max_age": 1200, "min_weight": 40, "max_weight": 150,
                "dose": "250-500mg q8h (mild) or 875mg q12h (moderate) or 1g q8h (severe)", 
                "max_daily": "3g", "frequency": "Every 8-12 hours",
                "method": "Oral tablets or capsules", "indication": "Bacterial infections",
                "special": "Take with or without food",
                "contraindications": "Penicillin allergy", "evidence": "high"
            },
            
            # Atenolol - Cardiovascular dosing
            {
                "medicine": "Atenolol", "age_group": "Children (6+ years)", 
                "min_age": 72, "max_age": 216, "min_weight": 20, "max_weight": 80,
                "dose": "0.5-1mg/kg/day, max 50mg daily", "max_daily": "50mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Hypertension", "special": "Monitor heart rate and BP",
                "contraindications": "Asthma, heart block, severe heart failure",
                "evidence": "moderate"
            },
            {
                "medicine": "Atenolol", "age_group": "Adults", 
                "min_age": 216, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "25-100mg daily (hypertension) or 50-100mg daily (angina)", 
                "max_daily": "200mg", "frequency": "Once or twice daily",
                "method": "Oral tablets", "indication": "Hypertension, angina, post-MI",
                "special": "May be taken with or without food",
                "contraindications": "Asthma, COPD, heart block, severe heart failure",
                "evidence": "high"
            },
            {
                "medicine": "Atenolol", "age_group": "Elderly (65+ years)", 
                "min_age": 780, "max_age": 1500, "min_weight": 45, "max_weight": 120,
                "dose": "25-50mg daily, start low", "max_daily": "100mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Hypertension, angina", "special": "Start low, titrate slowly",
                "contraindications": "Asthma, COPD, heart block",
                "renal": "Reduce dose if CrCl < 50 mL/min", "evidence": "high"
            },
            
            # Azithromycin - Antibiotic dosing
            {
                "medicine": "Azithromycin", "age_group": "Infants (6+ months)", 
                "min_age": 6, "max_age": 144, "min_weight": 7, "max_weight": 40,
                "dose": "10mg/kg day 1, then 5mg/kg days 2-5", "max_daily": "500mg", 
                "frequency": "Once daily", "method": "Oral suspension",
                "indication": "Respiratory/skin infections", "special": "Take 1 hour before or 2 hours after meals",
                "contraindications": "Macrolide allergy, severe liver disease",
                "evidence": "high"
            },
            {
                "medicine": "Azithromycin", "age_group": "Adults", 
                "min_age": 144, "max_age": 1200, "min_weight": 40, "max_weight": 150,
                "dose": "500mg day 1, then 250mg days 2-5 OR 500mg daily x 3 days", 
                "max_daily": "500mg", "frequency": "Once daily",
                "method": "Oral tablets", "indication": "Respiratory/skin/STI infections",
                "special": "May be taken with or without food",
                "contraindications": "Macrolide allergy, severe liver disease",
                "evidence": "high"
            },
            
            # Alprazolam - Anxiety medication (careful dosing)
            {
                "medicine": "Alprazolam", "age_group": "Adults (18+ years)", 
                "min_age": 216, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "0.25-0.5mg TID, titrate by 0.5mg/day every 3-4 days", 
                "max_daily": "4mg", "frequency": "Three times daily",
                "method": "Oral tablets", "indication": "Anxiety, panic disorder",
                "special": "Start low, taper slowly when discontinuing",
                "contraindications": "Acute narrow-angle glaucoma, severe respiratory depression",
                "evidence": "high"
            },
            {
                "medicine": "Alprazolam", "age_group": "Elderly (65+ years)", 
                "min_age": 780, "max_age": 1500, "min_weight": 45, "max_weight": 120,
                "dose": "0.125-0.25mg BID-TID", "max_daily": "2mg", 
                "frequency": "2-3 times daily", "method": "Oral tablets",
                "indication": "Anxiety", "special": "Increased fall risk, start very low",
                "contraindications": "Dementia, falls risk, respiratory depression",
                "evidence": "moderate"
            },
            
            # Cetirizine - Antihistamine dosing
            {
                "medicine": "Cetirizine", "age_group": "Infants (6-12 months)", 
                "min_age": 6, "max_age": 12, "min_weight": 7, "max_weight": 10,
                "dose": "2.5mg once daily", "max_daily": "2.5mg", 
                "frequency": "Once daily", "method": "Oral drops",
                "indication": "Allergic rhinitis, urticaria", "special": "May cause drowsiness",
                "contraindications": "Hypersensitivity to cetirizine or hydroxyzine",
                "evidence": "high"
            },
            {
                "medicine": "Cetirizine", "age_group": "Children (1-5 years)", 
                "min_age": 12, "max_age": 60, "min_weight": 10, "max_weight": 20,
                "dose": "2.5mg once or twice daily", "max_daily": "5mg", 
                "frequency": "Once or twice daily", "method": "Oral drops or syrup",
                "indication": "Allergic rhinitis, urticaria", "special": "May cause drowsiness",
                "contraindications": "Hypersensitivity", "evidence": "high"
            },
            {
                "medicine": "Cetirizine", "age_group": "Children (6-11 years)", 
                "min_age": 60, "max_age": 132, "min_weight": 20, "max_weight": 40,
                "dose": "5-10mg once daily", "max_daily": "10mg", 
                "frequency": "Once daily", "method": "Oral syrup or tablets",
                "indication": "Allergic rhinitis, urticaria", "special": "May cause drowsiness",
                "contraindications": "Hypersensitivity", "evidence": "high"
            },
            {
                "medicine": "Cetirizine", "age_group": "Adults", 
                "min_age": 144, "max_age": 1200, "min_weight": 40, "max_weight": 150,
                "dose": "10mg once daily", "max_daily": "10mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Allergic rhinitis, urticaria", "special": "May be taken with or without food",
                "contraindications": "Hypersensitivity", "evidence": "high"
            },
            
            # Amlodipine - Cardiovascular medication
            {
                "medicine": "Amlodipine", "age_group": "Children (6+ years)", 
                "min_age": 72, "max_age": 216, "min_weight": 20, "max_weight": 80,
                "dose": "0.1-0.2mg/kg/day, max 5mg daily", "max_daily": "5mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Hypertension", "special": "Monitor BP and heart rate",
                "contraindications": "Severe aortic stenosis", "evidence": "moderate"
            },
            {
                "medicine": "Amlodipine", "age_group": "Adults", 
                "min_age": 216, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "2.5-10mg once daily", "max_daily": "10mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Hypertension, angina", "special": "May be taken with or without food",
                "contraindications": "Severe aortic stenosis", "evidence": "high"
            },
            {
                "medicine": "Amlodipine", "age_group": "Elderly (65+ years)", 
                "min_age": 780, "max_age": 1500, "min_weight": 45, "max_weight": 120,
                "dose": "2.5-5mg once daily", "max_daily": "10mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Hypertension, angina", "special": "Start low due to increased sensitivity",
                "contraindications": "Severe aortic stenosis", "evidence": "high"
            },
            
            # Ciprofloxacin - Antibiotic with important pediatric considerations
            {
                "medicine": "Ciprofloxacin", "age_group": "Children (limited use)", 
                "min_age": 12, "max_age": 216, "min_weight": 10, "max_weight": 80,
                "dose": "10-20mg/kg q12h (max 750mg/dose)", "max_daily": "1.5g", 
                "frequency": "Every 12 hours", "method": "Oral suspension or tablets",
                "indication": "Complicated UTI, anthrax exposure", 
                "special": "Limited to specific indications due to arthropathy risk",
                "contraindications": "History of tendon disorders, myasthenia gravis",
                "evidence": "moderate"
            },
            {
                "medicine": "Ciprofloxacin", "age_group": "Adults", 
                "min_age": 216, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "250-750mg q12h", "max_daily": "1.5g", 
                "frequency": "Every 12 hours", "method": "Oral tablets",
                "indication": "UTI, respiratory, GI, skin infections", 
                "special": "Take 2 hours before or 6 hours after dairy/antacids",
                "contraindications": "History of tendon disorders, myasthenia gravis",
                "evidence": "high"
            },
            
            # Atorvastatin - Cholesterol medication
            {
                "medicine": "Atorvastatin", "age_group": "Children (10+ years)", 
                "min_age": 120, "max_age": 216, "min_weight": 30, "max_weight": 80,
                "dose": "10-20mg once daily", "max_daily": "20mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Familial hypercholesterolemia", "special": "Monitor liver function",
                "contraindications": "Active liver disease, pregnancy", "evidence": "moderate"
            },
            {
                "medicine": "Atorvastatin", "age_group": "Adults", 
                "min_age": 216, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "10-80mg once daily", "max_daily": "80mg", 
                "frequency": "Once daily", "method": "Oral tablets",
                "indication": "Hyperlipidemia, cardiovascular protection", 
                "special": "May be taken with or without food, monitor liver function",
                "contraindications": "Active liver disease, pregnancy, nursing",
                "evidence": "high"
            },
            
            # Budesonide - Inhaled corticosteroid
            {
                "medicine": "Budesonide", "age_group": "Children (6+ years)", 
                "min_age": 72, "max_age": 216, "min_weight": 20, "max_weight": 80,
                "dose": "200-400mcg twice daily", "max_daily": "800mcg", 
                "frequency": "Twice daily", "method": "Inhalation",
                "indication": "Asthma, allergic rhinitis", "special": "Rinse mouth after use",
                "contraindications": "Respiratory infections", "evidence": "high"
            },
            {
                "medicine": "Budesonide", "age_group": "Adults", 
                "min_age": 216, "max_age": 1200, "min_weight": 50, "max_weight": 150,
                "dose": "200-800mcg twice daily", "max_daily": "1600mcg", 
                "frequency": "Twice daily", "method": "Inhalation",
                "indication": "Asthma, COPD, allergic rhinitis", "special": "Rinse mouth after use",
                "contraindications": "Respiratory infections", "evidence": "high"
            }
        ]
        
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM dosage_guidelines')
        
        # Insert dosage guidelines
        for guideline in dosage_data:
            cursor.execute('''
                INSERT INTO dosage_guidelines 
                (medicine_name, age_group, min_age_months, max_age_months, min_weight_kg, max_weight_kg,
                 recommended_dose, max_daily_dose, frequency, administration_method, 
                 special_instructions, contraindications, renal_adjustment, hepatic_adjustment,
                 indication, evidence_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guideline["medicine"], guideline["age_group"], guideline["min_age"], guideline["max_age"],
                guideline["min_weight"], guideline["max_weight"], guideline["dose"], guideline["max_daily"],
                guideline["frequency"], guideline["method"], guideline["special"], 
                guideline["contraindications"], guideline.get("renal"), guideline.get("hepatic"),
                guideline["indication"], guideline["evidence"]
            ))
        
        self.conn.commit()
        
        # Get count
        cursor.execute('SELECT COUNT(*) FROM dosage_guidelines')
        count = cursor.fetchone()[0]
        print(f"✅ Inserted {count} dosage guidelines")
    
    def get_dosage_for_age_weight(self, medicine_name: str, age_months: int, weight_kg: float) -> List[Dict]:
        """Get appropriate dosage for specific age and weight."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM dosage_guidelines 
            WHERE medicine_name = ? 
            AND (min_age_months <= ? AND max_age_months >= ?)
            AND (min_weight_kg <= ? AND max_weight_kg >= ?)
            ORDER BY min_age_months
        ''', (medicine_name, age_months, age_months, weight_kg, weight_kg))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_age_specific_dosing(self, medicine_name: str, age_group: str) -> List[Dict]:
        """Get dosing for specific age group."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM dosage_guidelines 
            WHERE medicine_name = ? AND age_group LIKE ?
            ORDER BY min_age_months
        ''', (medicine_name, f'%{age_group}%'))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pediatric_contraindications(self, medicine_name: str) -> List[Dict]:
        """Get pediatric contraindications for a medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM dosage_guidelines 
            WHERE medicine_name = ? 
            AND (contraindications LIKE '%child%' OR contraindications LIKE '%pediatric%' 
                 OR recommended_dose = 'CONTRAINDICATED')
            ORDER BY min_age_months
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_dosing_for_medicine(self, medicine_name: str) -> List[Dict]:
        """Get all dosing information for a medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM dosage_guidelines 
            WHERE medicine_name = ?
            ORDER BY min_age_months
        ''', (medicine_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def check_age_appropriateness(self, medicine_name: str, age_months: int) -> Dict:
        """Check if medicine is age-appropriate and get recommendations."""
        guidelines = self.get_dosage_for_age_weight(medicine_name, age_months, 50)  # Default weight
        
        if not guidelines:
            # Check if there are any guidelines for this medicine
            all_guidelines = self.get_all_dosing_for_medicine(medicine_name)
            if all_guidelines:
                min_age = min(g['min_age_months'] for g in all_guidelines)
                max_age = max(g['max_age_months'] for g in all_guidelines)
                return {
                    "appropriate": False,
                    "reason": f"Age {age_months} months is outside recommended range ({min_age}-{max_age} months)",
                    "available_ages": [(g['age_group'], g['min_age_months'], g['max_age_months']) for g in all_guidelines]
                }
            else:
                return {
                    "appropriate": False,
                    "reason": "No dosing guidelines available for this medicine",
                    "available_ages": []
                }
        
        # Check for contraindications
        contraindicated = any('CONTRAINDICATED' in g['recommended_dose'] for g in guidelines)
        if contraindicated:
            return {
                "appropriate": False,
                "reason": "Contraindicated for this age group",
                "contraindications": [g['contraindications'] for g in guidelines if 'CONTRAINDICATED' in g['recommended_dose']]
            }
        
        return {
            "appropriate": True,
            "guidelines": guidelines
        }


def create_dosage_database():
    """Create and populate the dosage guidelines database."""
    print("🔄 Creating dosage guidelines database...")
    
    db = DosageGuidelinesManager()
    if db.connect():
        db.create_tables()
        db.populate_dosage_guidelines()
        
        # Test the database
        print("\n📊 Database Statistics:")
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dosage_guidelines")
        total_guidelines = cursor.fetchone()[0]
        print(f"  Total dosage guidelines: {total_guidelines}")
        
        cursor.execute("SELECT medicine_name, COUNT(*) FROM dosage_guidelines GROUP BY medicine_name ORDER BY COUNT(*) DESC")
        medicine_counts = cursor.fetchall()
        print("\n💊 Guidelines by medicine:")
        for medicine, count in medicine_counts:
            print(f"  {medicine}: {count} age groups")
        
        # Test some lookups
        print("\n🧪 Testing lookups:")
        
        # Test age appropriateness
        aspirin_child = db.check_age_appropriateness("Aspirin", 60)  # 5 years old
        print(f"  ✅ Aspirin for 5-year-old: {'Appropriate' if aspirin_child['appropriate'] else 'NOT APPROPRIATE'}")
        if not aspirin_child['appropriate']:
            print(f"      Reason: {aspirin_child['reason']}")
        
        # Test dosing lookup
        amoxicillin_dosing = db.get_dosage_for_age_weight("Amoxicillin", 36, 15)  # 3 years, 15kg
        print(f"  ✅ Amoxicillin for 3-year-old (15kg): {len(amoxicillin_dosing)} guidelines found")
        if amoxicillin_dosing:
            print(f"      Dose: {amoxicillin_dosing[0]['recommended_dose']}")
        
        # Test pediatric contraindications
        contraindications = db.get_pediatric_contraindications("Aspirin")
        print(f"  ✅ Aspirin pediatric contraindications: {len(contraindications)} found")
        
        db.close()
        print("✅ Dosage guidelines database created successfully!")
        return True
    else:
        print("❌ Failed to create dosage guidelines database")
        return False


if __name__ == "__main__":
    create_dosage_database() 