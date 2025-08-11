// Enhanced medicine information from multi-database system

export interface EnhancedMedicineInfo {
  // Original medicine info
  name: string;
  quantity: string;
  safety_concerns: string[];
  age_appropriate?: boolean;
  
  // Database information to display
  drugInteractions?: {
    total: number;
    severe: number;
    interactions: Array<{
      drug: string;
      severity: string;
      description: string;
    }>;
  };
  
  sideEffects?: Array<{
    effect: string;
    frequency: number;
    severity: string;
  }>;
  
  dosageInfo?: {
    ageGroup: string;
    recommendedDose: string;
    maxDailyDose: string;
    administration: string;
  };
  
  effectiveness?: {
    condition: string;
    rating: number;
    patientSatisfaction: number;
    studyData: string;
  };
  
  conditions?: Array<{
    condition: string;
    effectiveness: string;
  }>;
  
  prescriptionPatterns?: {
    commonlyPrescribed: string[];
    frequencyUsed: string;
    seasonalTrends: string;
  };
}

export interface EnhancedAlternativeInfo {
  name: string;
  recommendation_strength: string;
  rationale: string;
  safety_profile: string;
  effectiveness: string;
  cost_comparison: string;
  dosing_recommendation?: string;
  monitoring_required?: string;
  evidence_level?: string;
  
  // Enhanced database information
  enhancedInfo?: EnhancedMedicineInfo;
} 