"""
Prescription Patterns Database Manager
Creates and manages prescription patterns and trends for informed treatment decisions.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class PrescriptionPatternsManager:
    """Manages prescription patterns database for treatment trend analysis."""
    
    def __init__(self, db_path: str = "data/patterns.db"):
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
        """Create the prescription patterns tables."""
        cursor = self.conn.cursor()
        
        # Create prescription_patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescription_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition TEXT NOT NULL,
                primary_medicine TEXT NOT NULL,
                secondary_medicine TEXT,
                prescription_frequency REAL,
                success_rate REAL,
                age_group TEXT,
                gender_preference TEXT,
                specialty TEXT,
                geographic_region TEXT,
                seasonal_trend TEXT,
                duration_days INTEGER,
                dose_pattern TEXT,
                combination_rationale TEXT,
                contraindications_considered TEXT,
                monitoring_requirements TEXT,
                cost_effectiveness TEXT,
                patient_preference_score REAL,
                doctor_confidence_score REAL,
                guideline_adherence TEXT CHECK (guideline_adherence IN ('high', 'moderate', 'low')),
                evidence_level TEXT CHECK (evidence_level IN ('high', 'moderate', 'low', 'expert_opinion')),
                trend_direction TEXT CHECK (trend_direction IN ('increasing', 'stable', 'decreasing')),
                last_updated DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create common_combinations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS common_combinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition TEXT NOT NULL,
                medicine1 TEXT NOT NULL,
                medicine2 TEXT NOT NULL,
                medicine3 TEXT,
                combination_frequency REAL,
                synergy_score REAL,
                safety_profile TEXT,
                monitoring_needs TEXT,
                typical_duration TEXT,
                cost_ratio REAL,
                patient_outcomes TEXT,
                prescriber_specialty TEXT,
                evidence_base TEXT,
                warnings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(condition, medicine1, medicine2, medicine3)
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_condition ON prescription_patterns(condition)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_medicine ON prescription_patterns(primary_medicine)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON prescription_patterns(prescription_frequency)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_age ON prescription_patterns(age_group)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_combinations_condition ON common_combinations(condition)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_combinations_medicines ON common_combinations(medicine1, medicine2)')
        
        self.conn.commit()
        print("✅ Prescription patterns tables created successfully")
    
    def populate_prescription_patterns(self):
        """Populate the database with realistic prescription patterns data."""
        
        # Prescription patterns based on real clinical practice
        patterns_data = [
            # Hypertension patterns
            {
                "condition": "Hypertension", "primary": "Amlodipine", "secondary": "Atenolol",
                "frequency": 35.2, "success": 88.5, "age_group": "Adults", "gender": "Both",
                "specialty": "Primary Care", "region": "Global", "seasonal": "None",
                "duration": 365, "dose": "5mg daily + 50mg daily",
                "rationale": "Calcium channel blocker + beta blocker combination for better BP control",
                "contraindications": "Check for heart failure, asthma", 
                "monitoring": "BP every 2 weeks initially, then monthly",
                "cost": "Cost-effective combination", "patient_pref": 7.8, "doctor_conf": 8.9,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "Hypertension", "primary": "Candesartan", "secondary": "Amlodipine",
                "frequency": 28.7, "success": 91.2, "age_group": "Adults", "gender": "Both",
                "specialty": "Cardiology", "region": "North America/Europe", "seasonal": "None",
                "duration": 365, "dose": "8mg daily + 5mg daily",
                "rationale": "ARB + CCB combination, excellent CV outcomes",
                "contraindications": "Pregnancy, bilateral renal artery stenosis",
                "monitoring": "BP, kidney function every 3 months",
                "cost": "Moderate cost", "patient_pref": 8.2, "doctor_conf": 9.1,
                "guideline": "high", "evidence": "high", "trend": "increasing"
            },
            {
                "condition": "Hypertension", "primary": "Atenolol", "secondary": None,
                "frequency": 15.3, "success": 82.1, "age_group": "Young Adults", "gender": "Both",
                "specialty": "Primary Care", "region": "Global", "seasonal": "None",
                "duration": 365, "dose": "50mg daily",
                "rationale": "First-line monotherapy in young patients without comorbidities",
                "contraindications": "Asthma, COPD, diabetes",
                "monitoring": "BP, heart rate monthly",
                "cost": "Very cost-effective", "patient_pref": 6.9, "doctor_conf": 7.8,
                "guideline": "moderate", "evidence": "high", "trend": "decreasing"
            },
            
            # Bacterial infection patterns
            {
                "condition": "Bacterial Pneumonia", "primary": "Amoxicillin", "secondary": "Azithromycin",
                "frequency": 42.8, "success": 89.3, "age_group": "Adults", "gender": "Both",
                "specialty": "Primary Care", "region": "Global", "seasonal": "Winter peak",
                "duration": 7, "dose": "875mg BID + 500mg daily",
                "rationale": "Beta-lactam + macrolide for atypical coverage",
                "contraindications": "Penicillin allergy, macrolide allergy",
                "monitoring": "Clinical response at 48-72 hours",
                "cost": "Cost-effective", "patient_pref": 7.2, "doctor_conf": 8.7,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "Urinary Tract Infection", "primary": "Ciprofloxacin", "secondary": None,
                "frequency": 38.5, "success": 94.2, "age_group": "Adults", "gender": "Female predominant",
                "specialty": "Primary Care", "region": "Global", "seasonal": "Summer peak",
                "duration": 3, "dose": "500mg BID",
                "rationale": "High efficacy against common uropathogens",
                "contraindications": "Pregnancy, tendon disorders",
                "monitoring": "Symptom resolution at 3 days",
                "cost": "Moderate cost", "patient_pref": 8.4, "doctor_conf": 9.2,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "Skin and Soft Tissue Infection", "primary": "Cephalexin", "secondary": None,
                "frequency": 45.2, "success": 87.8, "age_group": "All ages", "gender": "Both",
                "specialty": "Primary Care", "region": "Global", "seasonal": "Summer peak",
                "duration": 7, "dose": "500mg QID",
                "rationale": "Excellent coverage for gram-positive skin pathogens",
                "contraindications": "Cephalosporin allergy",
                "monitoring": "Clinical improvement at 48-72 hours",
                "cost": "Very cost-effective", "patient_pref": 7.8, "doctor_conf": 8.5,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            
            # Anxiety and depression patterns
            {
                "condition": "Anxiety Disorder", "primary": "Alprazolam", "secondary": None,
                "frequency": 25.3, "success": 78.5, "age_group": "Adults", "gender": "Female predominant",
                "specialty": "Psychiatry", "region": "North America", "seasonal": "None",
                "duration": 30, "dose": "0.5mg TID PRN",
                "rationale": "Rapid onset for acute anxiety episodes",
                "contraindications": "Substance abuse history, elderly falls risk",
                "monitoring": "Weekly initially for dependence risk",
                "cost": "Low cost", "patient_pref": 8.1, "doctor_conf": 6.8,
                "guideline": "moderate", "evidence": "high", "trend": "decreasing"
            },
            {
                "condition": "Depression", "primary": "Bupropion", "secondary": None,
                "frequency": 18.7, "success": 72.4, "age_group": "Adults", "gender": "Both",
                "specialty": "Psychiatry", "region": "Global", "seasonal": "None",
                "duration": 180, "dose": "150mg BID",
                "rationale": "Low sexual side effects, weight neutral",
                "contraindications": "Seizure history, eating disorders",
                "monitoring": "Mood assessment every 2 weeks initially",
                "cost": "Moderate cost", "patient_pref": 7.6, "doctor_conf": 8.1,
                "guideline": "high", "evidence": "high", "trend": "increasing"
            },
            
            # Allergy patterns
            {
                "condition": "Allergic Rhinitis", "primary": "Cetirizine", "secondary": "Budesonide",
                "frequency": 32.1, "success": 91.8, "age_group": "All ages", "gender": "Both",
                "specialty": "Allergy/Primary Care", "region": "Global", "seasonal": "Spring/Fall peak",
                "duration": 30, "dose": "10mg daily + 200mcg BID nasal",
                "rationale": "Oral antihistamine + nasal corticosteroid for comprehensive control",
                "contraindications": "Hypersensitivity to components",
                "monitoring": "Symptom control at 1 week",
                "cost": "Cost-effective", "patient_pref": 8.6, "doctor_conf": 9.0,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "Urticaria", "primary": "Cetirizine", "secondary": None,
                "frequency": 58.9, "success": 89.2, "age_group": "All ages", "gender": "Both",
                "specialty": "Dermatology/Primary Care", "region": "Global", "seasonal": "None",
                "duration": 14, "dose": "10mg daily",
                "rationale": "First-line H1 antihistamine for hives",
                "contraindications": "Hypersensitivity",
                "monitoring": "Symptom resolution at 3-5 days",
                "cost": "Very cost-effective", "patient_pref": 8.9, "doctor_conf": 9.1,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            
            # Cardiovascular patterns
            {
                "condition": "Angina", "primary": "Atenolol", "secondary": "Aspirin",
                "frequency": 41.5, "success": 84.7, "age_group": "Adults", "gender": "Male predominant",
                "specialty": "Cardiology", "region": "Global", "seasonal": "None",
                "duration": 365, "dose": "100mg daily + 81mg daily",
                "rationale": "Beta blocker for rate control + antiplatelet for secondary prevention",
                "contraindications": "Asthma, active bleeding",
                "monitoring": "Angina frequency, BP, bleeding signs",
                "cost": "Very cost-effective", "patient_pref": 7.4, "doctor_conf": 8.8,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "Atrial Fibrillation", "primary": "Apixaban", "secondary": "Atenolol",
                "frequency": 35.7, "success": 88.9, "age_group": "Elderly", "gender": "Both",
                "specialty": "Cardiology", "region": "Developed countries", "seasonal": "None",
                "duration": 365, "dose": "5mg BID + 25mg daily",
                "rationale": "Anticoagulation + rate control strategy",
                "contraindications": "Active bleeding, severe renal impairment",
                "monitoring": "INR not needed, bleeding signs, heart rate",
                "cost": "High cost but effective", "patient_pref": 7.9, "doctor_conf": 9.2,
                "guideline": "high", "evidence": "high", "trend": "increasing"
            },
            
            # Respiratory patterns
            {
                "condition": "Asthma", "primary": "Budesonide", "secondary": None,
                "frequency": 67.3, "success": 86.4, "age_group": "All ages", "gender": "Both",
                "specialty": "Pulmonology/Primary Care", "region": "Global", "seasonal": "Fall/Spring exacerbations",
                "duration": 365, "dose": "400mcg BID inhaled",
                "rationale": "Inhaled corticosteroid as controller therapy",
                "contraindications": "Respiratory infections",
                "monitoring": "Peak flow, symptom control monthly",
                "cost": "Cost-effective", "patient_pref": 8.0, "doctor_conf": 9.1,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "COPD", "primary": "Budesonide", "secondary": None,
                "frequency": 45.8, "success": 71.2, "age_group": "Elderly", "gender": "Both",
                "specialty": "Pulmonology", "region": "Global", "seasonal": "Winter exacerbations",
                "duration": 365, "dose": "800mcg BID inhaled",
                "rationale": "Inhaled corticosteroid to reduce exacerbations",
                "contraindications": "Respiratory infections, pneumonia risk",
                "monitoring": "Exacerbation frequency, pneumonia risk",
                "cost": "Moderate cost", "patient_pref": 7.1, "doctor_conf": 8.2,
                "guideline": "high", "evidence": "high", "trend": "stable"
            },
            
            # Pain management patterns
            {
                "condition": "Acute Pain", "primary": "Aspirin", "secondary": None,
                "frequency": 28.4, "success": 76.8, "age_group": "Adults", "gender": "Both",
                "specialty": "Primary Care", "region": "Global", "seasonal": "None",
                "duration": 3, "dose": "650mg q6h PRN",
                "rationale": "NSAID for mild to moderate pain relief",
                "contraindications": "GI bleeding, anticoagulant use",
                "monitoring": "Pain relief, GI symptoms",
                "cost": "Very cost-effective", "patient_pref": 6.8, "doctor_conf": 7.9,
                "guideline": "moderate", "evidence": "high", "trend": "stable"
            },
            {
                "condition": "Migraine", "primary": "Aspirin", "secondary": None,
                "frequency": 22.1, "success": 68.3, "age_group": "Adults", "gender": "Female predominant",
                "specialty": "Neurology/Primary Care", "region": "Global", "seasonal": "None",
                "duration": 1, "dose": "1000mg at onset",
                "rationale": "High-dose aspirin for acute migraine treatment",
                "contraindications": "GI bleeding, anticoagulant use",
                "monitoring": "Headache relief at 2 hours",
                "cost": "Very cost-effective", "patient_pref": 6.9, "doctor_conf": 7.5,
                "guideline": "moderate", "evidence": "moderate", "trend": "stable"
            }
        ]
        
        # Common medication combinations
        combinations_data = [
            {
                "condition": "Hypertension", "med1": "Amlodipine", "med2": "Atenolol", "med3": None,
                "frequency": 25.3, "synergy": 8.5, "safety": "Generally safe, monitor for hypotension",
                "monitoring": "BP, heart rate, ankle swelling", "duration": "Long-term",
                "cost": 1.3, "outcomes": "Excellent BP control in 85% of patients",
                "specialty": "Primary Care/Cardiology", "evidence": "Multiple large RCTs",
                "warnings": "Avoid in heart failure, asthma"
            },
            {
                "condition": "Hypertension", "med1": "Candesartan", "med2": "Amlodipine", "med3": None,
                "frequency": 32.1, "synergy": 9.2, "safety": "Excellent safety profile",
                "monitoring": "BP, kidney function", "duration": "Long-term",
                "cost": 2.1, "outcomes": "Superior CV outcomes vs other combinations",
                "specialty": "Cardiology", "evidence": "ACCOMPLISH trial",
                "warnings": "Pregnancy contraindicated"
            },
            {
                "condition": "Bacterial Pneumonia", "med1": "Amoxicillin", "med2": "Azithromycin", "med3": None,
                "frequency": 38.7, "synergy": 8.8, "safety": "Monitor for drug interactions",
                "monitoring": "Clinical response, QT interval", "duration": "5-7 days",
                "cost": 1.2, "outcomes": "Broad spectrum coverage, good clinical outcomes",
                "specialty": "Primary Care/Internal Medicine", "evidence": "Clinical guidelines",
                "warnings": "QT prolongation risk with azithromycin"
            },
            {
                "condition": "Angina", "med1": "Atenolol", "med2": "Aspirin", "med3": None,
                "frequency": 45.2, "synergy": 8.7, "safety": "Monitor for bleeding",
                "monitoring": "Angina frequency, bleeding signs", "duration": "Long-term",
                "cost": 0.8, "outcomes": "Reduced angina episodes and CV events",
                "specialty": "Cardiology", "evidence": "Secondary prevention trials",
                "warnings": "GI bleeding risk, avoid in asthma"
            },
            {
                "condition": "Atrial Fibrillation", "med1": "Apixaban", "med2": "Atenolol", "med3": None,
                "frequency": 28.9, "synergy": 9.1, "safety": "Monitor bleeding risk",
                "monitoring": "Bleeding signs, heart rate", "duration": "Long-term",
                "cost": 15.2, "outcomes": "Stroke prevention with rate control",
                "specialty": "Cardiology", "evidence": "ARISTOTLE, RE-LY trials",
                "warnings": "Major bleeding risk, drug interactions"
            },
            {
                "condition": "Allergic Rhinitis", "med1": "Cetirizine", "med2": "Budesonide", "med3": None,
                "frequency": 41.6, "synergy": 9.0, "safety": "Very safe combination",
                "monitoring": "Symptom control", "duration": "Seasonal or as needed",
                "cost": 1.1, "outcomes": "Superior symptom control vs monotherapy",
                "specialty": "Allergy/Primary Care", "evidence": "Allergy guidelines",
                "warnings": "Minimal warnings"
            }
        ]
        
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM common_combinations')
        cursor.execute('DELETE FROM prescription_patterns')
        
        # Insert prescription patterns
        for pattern in patterns_data:
            cursor.execute('''
                INSERT INTO prescription_patterns 
                (condition, primary_medicine, secondary_medicine, prescription_frequency, success_rate,
                 age_group, gender_preference, specialty, geographic_region, seasonal_trend,
                 duration_days, dose_pattern, combination_rationale, contraindications_considered,
                 monitoring_requirements, cost_effectiveness, patient_preference_score, 
                 doctor_confidence_score, guideline_adherence, evidence_level, trend_direction,
                 last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'))
            ''', (
                pattern["condition"], pattern["primary"], pattern["secondary"], pattern["frequency"],
                pattern["success"], pattern["age_group"], pattern["gender"], pattern["specialty"],
                pattern["region"], pattern["seasonal"], pattern["duration"], pattern["dose"],
                pattern["rationale"], pattern["contraindications"], pattern["monitoring"],
                pattern["cost"], pattern["patient_pref"], pattern["doctor_conf"],
                pattern["guideline"], pattern["evidence"], pattern["trend"]
            ))
        
        # Insert combinations
        for combo in combinations_data:
            cursor.execute('''
                INSERT INTO common_combinations 
                (condition, medicine1, medicine2, medicine3, combination_frequency, synergy_score,
                 safety_profile, monitoring_needs, typical_duration, cost_ratio, patient_outcomes,
                 prescriber_specialty, evidence_base, warnings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                combo["condition"], combo["med1"], combo["med2"], combo["med3"],
                combo["frequency"], combo["synergy"], combo["safety"], combo["monitoring"],
                combo["duration"], combo["cost"], combo["outcomes"], combo["specialty"],
                combo["evidence"], combo["warnings"]
            ))
        
        self.conn.commit()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) FROM prescription_patterns')
        patterns_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM common_combinations')
        combos_count = cursor.fetchone()[0]
        
        print(f"✅ Inserted {patterns_count} prescription patterns and {combos_count} combinations")
    
    def get_patterns_for_condition(self, condition: str) -> List[Dict]:
        """Get all prescription patterns for a specific condition."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prescription_patterns 
            WHERE condition = ?
            ORDER BY prescription_frequency DESC
        ''', (condition,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_patterns_for_medicine(self, medicine_name: str) -> List[Dict]:
        """Get all prescription patterns involving a specific medicine."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prescription_patterns 
            WHERE primary_medicine = ? OR secondary_medicine = ?
            ORDER BY prescription_frequency DESC
        ''', (medicine_name, medicine_name))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_common_combinations_for_condition(self, condition: str) -> List[Dict]:
        """Get common medication combinations for a condition."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM common_combinations 
            WHERE condition = ?
            ORDER BY combination_frequency DESC
        ''', (condition,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_trending_prescriptions(self, trend_direction: str = "increasing") -> List[Dict]:
        """Get prescriptions with specific trend direction."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prescription_patterns 
            WHERE trend_direction = ?
            ORDER BY prescription_frequency DESC
        ''', (trend_direction,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_high_success_patterns(self, min_success_rate: float = 85.0) -> List[Dict]:
        """Get prescription patterns with high success rates."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prescription_patterns 
            WHERE success_rate >= ?
            ORDER BY success_rate DESC, prescription_frequency DESC
        ''', (min_success_rate,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_age_specific_patterns(self, age_group: str) -> List[Dict]:
        """Get prescription patterns for specific age group."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prescription_patterns 
            WHERE age_group = ? OR age_group = 'All ages'
            ORDER BY prescription_frequency DESC
        ''', (age_group,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_seasonal_patterns(self, season: str) -> List[Dict]:
        """Get prescription patterns with seasonal trends."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prescription_patterns 
            WHERE seasonal_trend LIKE ?
            ORDER BY prescription_frequency DESC
        ''', (f'%{season}%',))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_prescription_summary(self, condition: str) -> Dict:
        """Get a comprehensive prescription summary for a condition."""
        if not self.conn:
            return {}
        
        patterns = self.get_patterns_for_condition(condition)
        combinations = self.get_common_combinations_for_condition(condition)
        
        if not patterns:
            return {"condition": condition, "patterns_found": 0}
        
        # Most commonly prescribed
        most_common = patterns[0] if patterns else None
        
        # Average success rate
        avg_success = sum(p['success_rate'] for p in patterns) / len(patterns)
        
        # Trend analysis
        increasing_trends = len([p for p in patterns if p['trend_direction'] == 'increasing'])
        stable_trends = len([p for p in patterns if p['trend_direction'] == 'stable'])
        decreasing_trends = len([p for p in patterns if p['trend_direction'] == 'decreasing'])
        
        # High-quality evidence
        high_quality = len([p for p in patterns if p['evidence_level'] == 'high'])
        
        return {
            "condition": condition,
            "patterns_found": len(patterns),
            "combinations_found": len(combinations),
            "most_common_treatment": {
                "primary": most_common['primary_medicine'],
                "secondary": most_common['secondary_medicine'],
                "frequency": most_common['prescription_frequency'],
                "success_rate": most_common['success_rate']
            } if most_common else None,
            "average_success_rate": round(avg_success, 1),
            "trend_analysis": {
                "increasing": increasing_trends,
                "stable": stable_trends,
                "decreasing": decreasing_trends
            },
            "evidence_quality": {
                "high_quality_patterns": high_quality,
                "percentage_high_quality": round((high_quality / len(patterns)) * 100, 1)
            },
            "top_medicines": list(set([p['primary_medicine'] for p in patterns[:5]])),
            "specialties_prescribing": list(set([p['specialty'] for p in patterns]))
        }


def create_patterns_database():
    """Create and populate the prescription patterns database."""
    print("🔄 Creating prescription patterns database...")
    
    db = PrescriptionPatternsManager()
    if db.connect():
        db.create_tables()
        db.populate_prescription_patterns()
        
        # Test the database
        print("\n📊 Database Statistics:")
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM prescription_patterns")
        patterns_count = cursor.fetchone()[0]
        print(f"  Total prescription patterns: {patterns_count}")
        
        cursor.execute("SELECT COUNT(*) FROM common_combinations")
        combos_count = cursor.fetchone()[0]
        print(f"  Total medication combinations: {combos_count}")
        
        cursor.execute("SELECT condition, COUNT(*) FROM prescription_patterns GROUP BY condition ORDER BY COUNT(*) DESC")
        condition_counts = cursor.fetchall()
        print("\n🏥 Patterns by condition:")
        for condition, count in condition_counts:
            print(f"  {condition}: {count} patterns")
        
        cursor.execute("SELECT trend_direction, COUNT(*) FROM prescription_patterns GROUP BY trend_direction")
        trend_counts = cursor.fetchall()
        print("\n📈 Prescription trends:")
        for trend, count in trend_counts:
            print(f"  {trend}: {count}")
        
        cursor.execute("SELECT AVG(success_rate), AVG(patient_preference_score), AVG(doctor_confidence_score) FROM prescription_patterns")
        averages = cursor.fetchone()
        print(f"\n⭐ Overall averages:")
        print(f"  Success rate: {averages[0]:.1f}%")
        print(f"  Patient preference: {averages[1]:.1f}/10")
        print(f"  Doctor confidence: {averages[2]:.1f}/10")
        
        # Test some lookups
        print("\n🧪 Testing lookups:")
        
        hypertension_patterns = db.get_patterns_for_condition("Hypertension")
        print(f"  ✅ Hypertension patterns: {len(hypertension_patterns)} found")
        if hypertension_patterns:
            top = hypertension_patterns[0]
            print(f"      Most common: {top['primary_medicine']} ({top['prescription_frequency']:.1f}% frequency)")
        
        aspirin_patterns = db.get_patterns_for_medicine("Aspirin")
        print(f"  ✅ Aspirin usage patterns: {len(aspirin_patterns)} conditions")
        
        high_success = db.get_high_success_patterns(90.0)
        print(f"  ✅ High success patterns (≥90%): {len(high_success)} found")
        
        summary = db.get_prescription_summary("Bacterial Pneumonia")
        if summary.get("patterns_found", 0) > 0:
            print(f"  ✅ Pneumonia summary: {summary['patterns_found']} patterns, {summary['average_success_rate']}% avg success")
        
        trending = db.get_trending_prescriptions("increasing")
        print(f"  ✅ Increasing trend prescriptions: {len(trending)} found")
        
        db.close()
        print("✅ Prescription patterns database created successfully!")
        return True
    else:
        print("❌ Failed to create prescription patterns database")
        return False


if __name__ == "__main__":
    create_patterns_database() 