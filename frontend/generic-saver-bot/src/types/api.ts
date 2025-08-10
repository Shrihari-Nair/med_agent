// TypeScript interfaces for the simplified backend response

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
