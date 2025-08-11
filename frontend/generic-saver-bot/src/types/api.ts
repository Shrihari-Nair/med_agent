// TypeScript interfaces for the enhanced backend response with multi-database intelligence

// Original simple interfaces (kept for backward compatibility)
export interface MedicineAlternative {
  name: string;
  price: number;
  stock_quantity: number;
  generic_name: string;
  manufacturer: string;
  class: string;
  savings_amount: number;
  savings_percent: number;
  total_savings: number;
  quantity_needed: string;
}

export interface ProcessedMedicine {
  name: string;
  quantity: string;
  generic: string;
  original_price: number;
  alternatives: MedicineAlternative[];
}

export interface ResponseSummary {
  total_medicines: number;
  medicines_with_alternatives: number;
  total_alternatives_found: number;
}

export interface BackendResponse {
  medicines: ProcessedMedicine[];
  summary: ResponseSummary;
}

// Enhanced interfaces for multi-database intelligence
export interface SafetyConcern {
  type: 'interaction' | 'side_effect' | 'contraindication' | 'age_restriction';
  severity: 'mild' | 'moderate' | 'severe' | 'life_threatening' | 'contraindicated';
  description: string;
  recommendation?: string;
}

export interface SideEffect {
  effect: string;
  frequency: number;
  severity: string;
}

export interface EnhancedAlternative {
  name: string;
  recommendation_strength: 'Highly Recommended' | 'Recommended' | 'Consider' | 'Not Recommended';
  rationale: string;
  dosing_recommendation?: string;
  cost_comparison: string;
  safety_profile: string;
  monitoring_required?: string;
  effectiveness: string;
  effectiveness_rating?: number;
  evidence_level?: 'high' | 'moderate' | 'low' | 'expert_opinion';
  suitability_score?: number;
  age_appropriate?: boolean;
  common_side_effects?: string[];
}

export interface OriginalMedicine {
  name: string;
  current_quantity: string;
  safety_concerns: string[];
  effectiveness_rating?: string;
  age_appropriate?: boolean;
  basic_info?: {
    class: string;
    generic_name: string;
    manufacturer?: string;
    price?: number;
  };
  common_side_effects?: SideEffect[];
}

export interface MedicineAlternativeAnalysis {
  original_medicine: OriginalMedicine;
  recommended_alternatives: EnhancedAlternative[];
  clinical_notes: string;
  safety_considerations?: {
    drug_interactions: number;
    severe_side_effects: number;
    age_restrictions: boolean;
  };
}

export interface PrescriptionAnalysis {
  overall_safety_assessment: string;
  safety_score?: 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK';
  critical_warnings: string[];
  recommendations_summary: string;
}

export interface OverallRecommendations {
  prescription_changes: string;
  follow_up_needed: string;
  pharmacist_consultation: boolean;
  doctor_consultation: boolean;
}

export interface EnhancedBackendResponse {
  prescription_analysis: PrescriptionAnalysis;
  medicine_alternatives: MedicineAlternativeAnalysis[];
  overall_recommendations: OverallRecommendations;
}

// Union type for handling both old and new response formats
export type ApiResponse = BackendResponse | EnhancedBackendResponse;

// Type guards to distinguish between response types
export function isEnhancedResponse(response: any): response is EnhancedBackendResponse {
  return 'prescription_analysis' in response && 'medicine_alternatives' in response;
}

export function isLegacyResponse(response: any): response is BackendResponse {
  return 'medicines' in response && 'summary' in response;
}

// Error response interface
export interface BackendErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: string;
    timestamp: string;
  };
}
