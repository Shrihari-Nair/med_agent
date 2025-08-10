# Backend API Documentation for Generic Medicine Substitution

## Overview
This document describes the expected API endpoint and response format for processing prescription images and returning generic medicine alternatives.

## API Endpoint

### POST `/api/process-prescription`

Processes an uploaded prescription image/PDF and returns generic medicine alternatives.

#### Request Format
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Authentication**: Bearer token (if required)

#### Request Body
```
prescription: File (image or PDF)
patient_id: string (optional)
location: { latitude: number, longitude: number } (optional, for pharmacy proximity)
```

#### Response Format

##### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Prescription processed successfully",
  "data": {
    "prescription_id": "presc_123456789",
    "extracted_text": "Full OCR extracted text from prescription",
    "medicines": [
      {
        "id": "med_001",
        "prescribedName": "Crestor 10mg (Rosuvastatin)",
        "brandedPrice": 850,
        "composition": "Rosuvastatin Calcium 10mg",
        "strength": "10mg",
        "dosageForm": "Tablet",
        "extractedText": "Tab Crestor 10mg",
        "confidence": 0.95,
        "genericAlternatives": [
          {
            "id": "gen_001_a",
            "name": "Rosuvastatin 10mg (Rosuvas)",
            "price": 120,
            "manufacturer": "Sun Pharma",
            "composition": "Rosuvastatin Calcium 10mg",
            "strength": "10mg",
            "dosageForm": "Tablet",
            "availability": "in-stock",
            "stockCount": 150,
            "expiryDate": "2026-12-31",
            "pharmacyInfo": {
              "pharmacyId": "pharm_001",
              "pharmacyName": "MedPlus",
              "distance": "0.5 km"
            }
          }
        ],
        "selectedGenericId": "gen_001_a",
        "approval": "pending"
      }
    ],
    "summary": {
      "totalMedicinesFound": 3,
      "totalBrandedCost": 5670,
      "totalGenericCost": 965,
      "totalPotentialSavings": 4705,
      "savingsPercentage": 83.0,
      "processingTime": "2.3 seconds"
    },
    "metadata": {
      "ocrEngine": "Tesseract 5.2",
      "ocrConfidence": 0.95,
      "imageQuality": "high",
      "processingTimestamp": "2025-08-08T14:30:22Z",
      "apiVersion": "v1.2.3"
    }
  }
}
```

##### Error Response (400/500)
```json
{
  "success": false,
  "error": {
    "code": "PROCESSING_FAILED",
    "message": "Unable to extract medicine names from prescription",
    "details": "Image quality too low for OCR processing",
    "timestamp": "2025-08-08T14:30:22Z"
  }
}
```

## Data Field Descriptions

### Medicine Object
- **id**: Unique identifier for the medicine
- **prescribedName**: Full name as extracted from prescription
- **brandedPrice**: Current market price of the branded medicine
- **composition**: Active pharmaceutical ingredient
- **strength**: Dosage strength (e.g., "10mg", "500mg")
- **dosageForm**: Form of medicine ("Tablet", "Capsule", "Syrup", etc.)
- **extractedText**: Raw text extracted from OCR
- **confidence**: OCR confidence score (0-1)
- **genericAlternatives**: Array of available generic alternatives
- **selectedGenericId**: Default selected generic (usually cheapest)
- **approval**: Patient approval status

### Generic Alternative Object
- **id**: Unique identifier for the generic alternative
- **name**: Commercial name of the generic medicine
- **price**: Current price of the generic alternative
- **manufacturer**: Manufacturing company
- **composition**: Active pharmaceutical ingredient (should match branded)
- **strength**: Dosage strength (should match branded)
- **dosageForm**: Form of medicine (should match branded)
- **availability**: Stock status ("in-stock", "low-stock", "out-of-stock")
- **stockCount**: Number of units available
- **expiryDate**: Expiration date of available stock
- **pharmacyInfo**: Information about the pharmacy

### Pharmacy Info Object
- **pharmacyId**: Unique identifier for the pharmacy
- **pharmacyName**: Display name of the pharmacy
- **distance**: Distance from patient location

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_FILE_FORMAT` | Uploaded file is not a supported image or PDF |
| `FILE_TOO_LARGE` | File size exceeds maximum limit |
| `OCR_FAILED` | OCR processing failed |
| `NO_MEDICINES_FOUND` | No medicine names could be extracted |
| `DATABASE_ERROR` | Error accessing medicine database |
| `PROCESSING_TIMEOUT` | Processing took too long |

## Frontend Integration

### How to Handle the Response

```typescript
// Transform backend response to frontend format
const transformedRows: MedicineRow[] = data.data.medicines.map(medicine => ({
  id: medicine.id,
  prescribedName: medicine.prescribedName,
  brandedPrice: medicine.brandedPrice,
  genericAlternatives: medicine.genericAlternatives.map(alt => ({
    id: alt.id,
    name: alt.name,
    price: alt.price,
    manufacturer: alt.manufacturer,
    availability: alt.availability
  })),
  selectedGenericId: medicine.selectedGenericId || medicine.genericAlternatives[0]?.id,
  approval: "pending"
}));
```

### Example Frontend Implementation

```typescript
const handleFileUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('prescription', file);
  
  try {
    const response = await fetch('/api/process-prescription', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${authToken}` // if auth required
      }
    });
    
    const data: BackendResponse = await response.json();
    
    if (data.success) {
      // Update UI with processed medicines
      setMedicines(transformBackendResponse(data));
      showSuccessMessage(data.data.summary);
    } else {
      showErrorMessage(data.error.message);
    }
  } catch (error) {
    showErrorMessage('Network error occurred');
  }
};
```

## Additional API Endpoints (Optional)

### GET `/api/medicines/search?q={medicine_name}`
Search for medicine alternatives by name

### POST `/api/approve-substitution`
Record patient approval for a substitution

### GET `/api/pharmacies/nearby`
Get nearby pharmacies with stock information

### GET `/api/prescription/{prescription_id}`
Retrieve previously processed prescription
