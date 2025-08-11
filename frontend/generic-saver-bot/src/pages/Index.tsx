import { useState } from "react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { MedicineTable, MedicineRow } from "@/components/medicine/MedicineTable";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Upload, FileText, DollarSign, CheckCircle2, AlertCircle, Pill, TrendingDown, Shield, Clock } from "lucide-react";
import { 
  BackendResponse, 
  ProcessedMedicine, 
  ApiResponse, 
  EnhancedBackendResponse,
  isEnhancedResponse,
  isLegacyResponse 
} from "@/types/api";
import { SafetyAnalysis } from "@/components/medicine/SafetyAnalysis";
import { EnhancedMedicineCard } from "@/components/medicine/EnhancedMedicineCard";
import { convertEnhancedToLegacyFormat, extractSafetySummary } from "@/utils/responseConverter";
import { EnhancedMedicineInfo } from "@/types/enhanced-medicine";
import { ProcessingIndicator } from "@/components/ui/processing-indicator";

// Helper function to convert backend response to frontend format
const convertBackendToFrontend = (backendData: BackendResponse): MedicineRow[] => {
  return backendData.medicines.map((medicine, index) => ({
    id: `med_${index + 1}`,
    name: medicine.name,
    quantity: medicine.quantity,
    generic: medicine.generic,
    original_price: medicine.original_price,
    alternatives: medicine.alternatives.map((alt, altIndex) => ({
      id: `alt_${index}_${altIndex}`,
      ...alt,
      availability: alt.stock_quantity > 50 ? "in-stock" as const
                  : alt.stock_quantity > 10 ? "low-stock" as const
                  : "out-of-stock" as const
    })),
    selectedAlternativeId: medicine.alternatives.length > 0 ? `alt_${index}_0` : null, // Only set if alternatives exist
    approval: medicine.alternatives.length > 0 ? "pending" as const : "no-alternatives" as const // Special status for no alternatives
  }));
};

const sampleRows: MedicineRow[] = [
  {
    id: "1",
    name: "Paracetamol",
    quantity: "10 tablets",
    generic: "Acetaminophen",
    original_price: 61.57,
    alternatives: [
      {
        id: "1a",
        name: "Paracetamol E",
        price: 13.56,
        stock_quantity: 74,
        generic_name: "Acetaminophen",
        manufacturer: "GSK",
        class: "Pain Relievers",
        savings_amount: 48.01,
        savings_percent: 78.0,
        total_savings: 480.1,
        quantity_needed: "10 tablets",
        availability: "in-stock"
      },
      {
        id: "1b",
        name: "Paracetamol D",
        price: 47.59,
        stock_quantity: 353,
        generic_name: "Acetaminophen",
        manufacturer: "GSK",
        class: "Pain Relievers",
        savings_amount: 13.98,
        savings_percent: 22.7,
        total_savings: 139.8,
        quantity_needed: "10 tablets",
        availability: "in-stock"
      }
    ],
    selectedAlternativeId: "1a",
    approval: "pending",
  },
  {
    id: "2",
    name: "Amoxicillin",
    quantity: "15 capsules",
    generic: "Amoxicillin",
    original_price: 12.46,
    alternatives: [
      {
        id: "2a",
        name: "Amoxicillin C",
        price: 8.61,
        stock_quantity: 164,
        generic_name: "Amoxicillin",
        manufacturer: "Cipla",
        class: "Antibiotics",
        savings_amount: 3.85,
        savings_percent: 30.9,
        total_savings: 57.75,
        quantity_needed: "15 capsules",
        availability: "in-stock"
      }
    ],
    selectedAlternativeId: "2a",
    approval: "pending",
  },
  {
    id: "3",
    name: "Cetirizine",
    quantity: "7 tablets",
    generic: "Cetirizine",
    original_price: 24.2,
    alternatives: [
      {
        id: "3a",
        name: "Cetirizine B",
        price: 19.79,
        stock_quantity: 11,
        generic_name: "Cetirizine",
        manufacturer: "UCB",
        class: "Antihistamines",
        savings_amount: 4.41,
        savings_percent: 18.2,
        total_savings: 30.87,
        quantity_needed: "7 tablets",
        availability: "low-stock"
      },
      {
        id: "3b",
        name: "Cetirizine E",
        price: 20.9,
        stock_quantity: 322,
        generic_name: "Cetirizine",
        manufacturer: "UCB",
        class: "Antihistamines",
        savings_amount: 3.3,
        savings_percent: 13.6,
        total_savings: 23.1,
        quantity_needed: "7 tablets",
        availability: "in-stock"
      }
    ],
    selectedAlternativeId: "3a",
    approval: "pending",
  },
];

const Index = () => {
  const [rows, setRows] = useState<MedicineRow[]>([]);
  const [enhancedResponse, setEnhancedResponse] = useState<EnhancedBackendResponse | null>(null);
  const [safetySummary, setSafetySummary] = useState<{
    riskLevel: 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK';
    criticalWarnings: string[];
    requiresConsultation: boolean;
    summary: string;
  } | null>(null);
  const [databaseInfo, setDatabaseInfo] = useState<Map<string, EnhancedMedicineInfo> | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [showFinalList, setShowFinalList] = useState(false);
  const approved = rows.filter((r) => r.approval === "approved");
  const declined = rows.filter((r) => r.approval === "declined");
  const pending = rows.filter((r) => r.approval === "pending");
  const noAlternatives = rows.filter((r) => r.approval === "no-alternatives");
  
  // Get the final list of all medicines (approved alternatives + original declined ones + no alternatives)
  const getFinalMedicineList = () => {
    const finalList = [];
    
    // Add approved alternatives
    approved.forEach(med => {
      const selectedAlternative = med.alternatives.find(a => a.id === med.selectedAlternativeId) || med.alternatives[0];
      if (selectedAlternative) {
        finalList.push({
          name: selectedAlternative.name,
          original_name: med.name,
          quantity: med.quantity,
          generic: med.generic,
          price: selectedAlternative.price,
          manufacturer: selectedAlternative.manufacturer,
          class: selectedAlternative.class,
          savings_amount: selectedAlternative.savings_amount,
          savings_percent: selectedAlternative.savings_percent,
          total_savings: selectedAlternative.total_savings,
          type: 'alternative' as const
        });
      }
    });
    
    // Add original medicines for declined ones
    declined.forEach(med => {
      finalList.push({
        name: med.name,
        original_name: med.name,
        quantity: med.quantity,
        generic: med.generic,
        price: med.original_price,
        manufacturer: 'Original Prescription',
        class: 'Original',
        savings_amount: 0,
        savings_percent: 0,
        total_savings: 0,
        type: 'original' as const
      });
    });

    // Add medicines with no alternatives (these are automatically included)
    noAlternatives.forEach(med => {
      finalList.push({
        name: med.name,
        original_name: med.name,
        quantity: med.quantity,
        generic: med.generic,
        price: med.original_price,
        manufacturer: 'Original Prescription',
        class: 'Original',
        savings_amount: 0,
        savings_percent: 0,
        total_savings: 0,
        type: 'no-alternatives' as const
      });
    });
    
    return finalList;
  };

  const totalSavings = approved.reduce((sum, row) => {
    const selectedAlternative = row.alternatives.find(a => a.id === row.selectedAlternativeId) || row.alternatives[0];
    return sum + (selectedAlternative ? selectedAlternative.savings_amount : 0);
  }, 0);
  const totalOriginalCost = approved.reduce((sum, row) => sum + row.original_price, 0);
  const savingsPercentage = totalOriginalCost > 0 ? (totalSavings / totalOriginalCost) * 100 : 0;

  const handleConfirmAndContinue = () => {
    setShowFinalList(true);
    const hasApprovedAlternatives = approved.length > 0;
    const hasDeclinedOriginals = declined.length > 0;
    
    if (hasApprovedAlternatives) {
      toast.success("Purchase successful! 🎉", {
        description: "Your medicine order has been confirmed with approved alternatives.",
        duration: 5000
      });
    } else if (hasDeclinedOriginals || noAlternatives.length > 0) {
      toast.success("Order confirmed! 📋", {
        description: "Continuing with original prescription as requested.",
        duration: 5000
      });
    } else {
      toast.success("Purchase successful! 🎉", {
        description: "Your medicine order has been confirmed.",
        duration: 5000
      });
    }
  };

  const handleStartNewPrescription = () => {
    setShowFinalList(false);
    setRows([]);
    setEnhancedResponse(null);
    setSafetySummary(null);
    setDatabaseInfo(null);
    setFileName("");
    // Scroll to top for better UX
    window.scrollTo({ top: 0, behavior: 'smooth' });
    toast.success("Ready for new prescription! 📄", {
      description: "Upload your next prescription to continue saving.",
      duration: 3000
    });
  };

  const handleFile = (file?: File) => {
    if (!file) return;
    setFileName(file.name);
    
    // Add slight delay to prevent flicker for fast responses
    setTimeout(() => setIsProcessing(true), 100);
    
    // Real API call to backend
    console.log('📤 Starting file upload:', file.name, file.type, file.size);
    const formData = new FormData();
    formData.append('prescription', file);
    
    fetch('/api/process-prescription', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      console.log('📥 Received response:', response.status, response.statusText);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data: ApiResponse) => {
      console.log('✅ Processing successful:', data);
      
      if (isEnhancedResponse(data)) {
        // Handle enhanced response with multi-database intelligence
        console.log('🔬 Enhanced response detected with medical intelligence');
        setEnhancedResponse(data);
        
        // Convert enhanced response to legacy format for workflow compatibility
        const { rows: convertedRows, databaseInfo: dbInfo } = convertEnhancedToLegacyFormat(data);
        setRows(convertedRows);
        setDatabaseInfo(dbInfo);
        
        // Extract safety summary
        const safety = extractSafetySummary(data);
        setSafetySummary(safety);
        
        toast.success("🧠 Enhanced Medical Intelligence Complete!", {
          description: `AI analyzed ${data.medicine_alternatives.length} medicine(s) using 7 databases for safety, effectiveness, and cost insights.`,
          duration: 6000
        });
      } else if (isLegacyResponse(data)) {
        // Handle legacy response format
        console.log('📊 Legacy response detected, converting to standard format');
        const transformedRows = convertBackendToFrontend(data);
        setRows(transformedRows);
        setEnhancedResponse(null);
        setSafetySummary(null);
        setDatabaseInfo(null);
        
        toast.success("Prescription processed successfully!", {
          description: `Found ${data.summary.total_medicines} medicines with ${data.summary.total_alternatives_found} alternatives available.`,
          duration: 5000
        });
      } else {
        throw new Error('Unknown response format received from server');
      }
      
      setIsProcessing(false);
    })
    .catch(error => {
      console.error('❌ Processing failed:', error);
      setIsProcessing(false);
      toast.error("Processing failed", {
        description: error.message || "Please try again with a clearer image",
        duration: 4000
      });
    });
    
    /* 
    // Fallback simulation for testing (remove this in production)
    const mockBackendResponse: BackendResponse = {
      medicines: [
        {
          name: "Paracetamol",
          quantity: "10 tablets",
          generic: "Acetaminophen",
          original_price: 61.57,
          alternatives: [
            {
              name: "Paracetamol E",
              price: 13.56,
              stock_quantity: 74,
              generic_name: "Acetaminophen",
              manufacturer: "GSK",
              class: "Pain Relievers",
              savings_amount: 48.01,
              savings_percent: 78.0,
              total_savings: 480.1,
              quantity_needed: "10 tablets"
            },
            {
              name: "Paracetamol D",
              price: 47.59,
              stock_quantity: 353,
              generic_name: "Acetaminophen",
              manufacturer: "GSK", 
              class: "Pain Relievers",
              savings_amount: 13.98,
              savings_percent: 22.7,
              total_savings: 139.8,
              quantity_needed: "10 tablets"
            }
          ]
        },
        {
          name: "Amoxicillin",
          quantity: "15 capsules", 
          generic: "Amoxicillin",
          original_price: 12.46,
          alternatives: [
            {
              name: "Amoxicillin C",
              price: 8.61,
              stock_quantity: 164,
              generic_name: "Amoxicillin",
              manufacturer: "Cipla",
              class: "Antibiotics",
              savings_amount: 3.85,
              savings_percent: 30.9,
              total_savings: 57.75,
              quantity_needed: "15 capsules"
            }
          ]
        },
        {
          name: "Cetirizine",
          quantity: "7 tablets",
          generic: "Cetirizine", 
          original_price: 24.2,
          alternatives: [
            {
              name: "Cetirizine B",
              price: 19.79,
              stock_quantity: 11,
              generic_name: "Cetirizine",
              manufacturer: "UCB",
              class: "Antihistamines",
              savings_amount: 4.41,
              savings_percent: 18.2,
              total_savings: 30.87,
              quantity_needed: "7 tablets"
            },
            {
              name: "Cetirizine E",
              price: 20.9,
              stock_quantity: 322,
              generic_name: "Cetirizine",
              manufacturer: "UCB",
              class: "Antihistamines",
              savings_amount: 3.3,
              savings_percent: 13.6,
              total_savings: 23.1,
              quantity_needed: "7 tablets"
            }
          ]
        }
      ],
      summary: {
        total_medicines: 3,
        medicines_with_alternatives: 3,
        total_alternatives_found: 5
      }
    };
    
    setTimeout(() => {
      const transformedRows = convertBackendToFrontend(mockBackendResponse);
      setRows(transformedRows);
      setIsProcessing(false);
      toast.success("Prescription processed successfully!", { 
        description: `Found ${mockBackendResponse.summary.total_medicines} medicines with ${mockBackendResponse.summary.total_alternatives_found} alternatives available.`,
        duration: 5000
      });
    }, 2500);
    */
  };

  const onApprove = (id: string) => {
    setRows((rws) => rws.map((r) => (r.id === id ? { ...r, approval: "approved" } : r)));
    const med = rows.find((r) => r.id === id);
    if (med) {
      const selectedAlternative = med.alternatives.find(a => a.id === med.selectedAlternativeId) || med.alternatives[0];
      if (selectedAlternative) {
        toast.success("Substitution approved! 🎉", { 
          description: `You'll save ₹${selectedAlternative.savings_amount.toLocaleString("en-IN")} with ${selectedAlternative.name}`,
          duration: 4000
        });
      }
    }
  };

  const onAlternativeSelect = (medicineId: string, alternativeId: string) => {
    setRows((rws) => rws.map((r) => 
      r.id === medicineId ? { ...r, selectedAlternativeId: alternativeId } : r
    ));
    
    const med = rows.find((r) => r.id === medicineId);
    const selectedAlternative = med?.alternatives.find(a => a.id === alternativeId);
    
    if (med && selectedAlternative) {
      toast.success("Alternative updated!", { 
        description: `${selectedAlternative.name} selected • Save ₹${selectedAlternative.savings_amount.toLocaleString("en-IN")} (${selectedAlternative.savings_percent.toFixed(1)}%)`,
        duration: 3000
      });
    }
  };

  const onDecline = (id: string) => {
    setRows((rws) => rws.map((r) => (r.id === id ? { ...r, approval: "declined" } : r)));
    const med = rows.find((r) => r.id === id);
    if (med) toast("Substitution declined", { 
      description: `Keeping original prescription: ${med.name}`,
      duration: 3000
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="container py-10">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Generic Medicine Substitution
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Upload your prescription (image or PDF). We’ll suggest high-quality generic equivalents, show your savings, and let you approve with one tap.
          </p>
        </div>
      </header>

      <main className="container space-y-8 pb-16">
        <section>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Upload prescription</CardTitle>
                  <CardDescription>Supported formats: images and PDF</CardDescription>
                </div>
                {rows.length > 0 && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleStartNewPrescription}
                    className="text-gray-600 hover:text-gray-800"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    New Prescription
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-center">
              <Input
                type="file"
                accept="image/*,application/pdf"
                onChange={(e) => handleFile(e.target.files?.[0])}
                aria-label="Upload prescription file"
              />
              <Button onClick={() => toast("Need help?", { description: "Choose an image or PDF to begin." })} className="sm:w-auto w-full">How it works</Button>
              {fileName && (
                <div className="text-sm text-muted-foreground truncate">Selected: {fileName}</div>
              )}
            </CardContent>
          </Card>
        </section>

        <section aria-labelledby="review-substitutions">
          <h2 id="review-substitutions" className="sr-only">Review substitutions</h2>
          {/* Safety Banner for Enhanced Intelligence */}
          {safetySummary && (
            <div className="mb-6">
              <SafetyAnalysis 
                analysis={enhancedResponse!.prescription_analysis} 
                recommendations={enhancedResponse!.overall_recommendations} 
              />
            </div>
          )}
          
          {rows.length === 0 ? (
            <div className="rounded-lg border p-8 text-center text-muted-foreground">
              Your suggested substitutions will appear here after you upload a prescription.
            </div>
          ) : (
            <>
              <MedicineTable 
                rows={rows} 
                onApprove={onApprove} 
                onDecline={onDecline} 
                onAlternativeSelect={onAlternativeSelect}
                databaseInfo={databaseInfo}
              />
              <div className="mt-6 flex justify-end">
                <Dialog>
                  <DialogTrigger asChild>
                                    <Button size="lg" disabled={rows.length === 0} aria-label="Review medicine list">
                  Review Medicine List {rows.length > 0 ? `(${rows.length})` : ""}
                </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Final Medicine List</DialogTitle>
                      <DialogDescription>Review your complete medicine list before confirming.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      {rows.length === 0 ? (
                        <p className="text-muted-foreground text-sm">No medicines to review.</p>
                      ) : (
                        <div className="space-y-4">
                          {/* Approved Substitutions */}
                          {approved.length > 0 && (
                            <div>
                              <h4 className="font-medium text-green-700 mb-2 flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4" />
                                Approved Substitutions ({approved.length})
                              </h4>
                              <ul className="space-y-3">
                                {approved.map((m) => {
                                  const selectedAlternative = m.alternatives.find(a => a.id === m.selectedAlternativeId) || m.alternatives[0];
                                  return (
                                    <li key={m.id} className="flex items-center justify-between rounded-md border border-green-200 p-3 bg-green-50">
                                      <div>
                                        <div className="font-medium">{m.name}</div>
                                        <div className="text-xs text-muted-foreground">
                                          → {selectedAlternative?.name || 'No alternative selected'}
                                        </div>
                                        {selectedAlternative && (
                                          <div className="text-xs text-blue-600 mt-1">
                                            {selectedAlternative.manufacturer} • ₹{selectedAlternative.price.toLocaleString("en-IN")}
                                          </div>
                                        )}
                                      </div>
                                      <div className="text-right">
                                        <div className="text-sm text-green-700">Save ₹{selectedAlternative?.savings_amount.toLocaleString("en-IN") || '0'}</div>
                                        {selectedAlternative && (
                                          <div className="text-xs text-green-600">
                                            {selectedAlternative.savings_percent.toFixed(1)}% off
                                          </div>
                                        )}
                                      </div>
                                    </li>
                                  );
                                })}
                              </ul>
                            </div>
                          )}

                          {/* Declined Substitutions (Original Medicines) */}
                          {declined.length > 0 && (
                            <div>
                              <h4 className="font-medium text-blue-700 mb-2 flex items-center gap-2">
                                <Pill className="h-4 w-4" />
                                Original Prescriptions ({declined.length})
                              </h4>
                              <ul className="space-y-3">
                                {declined.map((m) => (
                                  <li key={m.id} className="flex items-center justify-between rounded-md border border-blue-200 p-3 bg-blue-50">
                                    <div>
                                      <div className="font-medium">{m.name}</div>
                                      <div className="text-xs text-muted-foreground">
                                        Original prescription
                                      </div>
                                      <div className="text-xs text-blue-600 mt-1">
                                        Generic: {m.generic} • ₹{m.original_price.toLocaleString("en-IN")}
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="text-sm text-blue-700">No change</div>
                                      <div className="text-xs text-blue-600">
                                        Original price
                                      </div>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Pending Decisions */}
                          {pending.length > 0 && (
                            <div>
                              <h4 className="font-medium text-orange-700 mb-2 flex items-center gap-2">
                                <Clock className="h-4 w-4" />
                                Pending Decisions ({pending.length})
                              </h4>
                              <ul className="space-y-3">
                                {pending.map((m) => (
                                  <li key={m.id} className="flex items-center justify-between rounded-md border border-orange-200 p-3 bg-orange-50">
                                    <div>
                                      <div className="font-medium">{m.name}</div>
                                      <div className="text-xs text-muted-foreground">
                                        Please approve or decline
                                      </div>
                                      <div className="text-xs text-orange-600 mt-1">
                                        Generic: {m.generic} • ₹{m.original_price.toLocaleString("en-IN")}
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="text-sm text-orange-700">Decision needed</div>
                                      <div className="text-xs text-orange-600">
                                        Review alternatives
                                      </div>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Medicines with No Alternatives */}
                          {noAlternatives.length > 0 && (
                            <div>
                              <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                                <Shield className="h-4 w-4" />
                                No Alternatives Available ({noAlternatives.length})
                              </h4>
                              <ul className="space-y-3">
                                {noAlternatives.map((m) => (
                                  <li key={m.id} className="flex items-center justify-between rounded-md border border-gray-200 p-3 bg-gray-50">
                                    <div>
                                      <div className="font-medium">{m.name}</div>
                                      <div className="text-xs text-muted-foreground">
                                        Original prescription (no alternatives found)
                                      </div>
                                      <div className="text-xs text-gray-600 mt-1">
                                        Generic: {m.generic} • ₹{m.original_price.toLocaleString("en-IN")}
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="text-sm text-gray-700">Auto-included</div>
                                      <div className="text-xs text-gray-600">
                                        Will be in final order
                                      </div>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Summary */}
                          <div className="p-3 bg-muted/50 rounded-lg">
                            <div className="grid grid-cols-3 gap-4 text-sm">
                              <div>
                                <span className="text-muted-foreground">Total Savings:</span>
                                <div className="font-medium text-green-600">₹{totalSavings.toFixed(2)}</div>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Total Medicines:</span>
                                <div className="font-medium">{rows.length}</div>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Auto-included:</span>
                                <div className="font-medium text-gray-600">{noAlternatives.length}</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    <DialogFooter>
                      <DialogClose asChild>
                        <Button variant="secondary">Close</Button>
                      </DialogClose>
                      {(approved.length > 0 || declined.length > 0 || noAlternatives.length > 0) && (
                        <Button onClick={handleConfirmAndContinue}>
                          {approved.length > 0 ? 'Confirm and continue' : 'Continue with original prescription'}
                        </Button>
                      )}
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </>
          )}
        </section>

        {/* Final Medicine List Dialog */}
        <Dialog open={showFinalList} onOpenChange={setShowFinalList}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                Purchase Successful! 🎉
              </DialogTitle>
              <DialogDescription>
                Here's your final medicine list with all approved substitutions and original prescriptions. 
                You can start a new prescription after reviewing this order.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ₹{totalSavings.toFixed(2)}
                  </div>
                  <div className="text-sm text-muted-foreground">Total Savings</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {getFinalMedicineList().length}
                  </div>
                  <div className="text-sm text-muted-foreground">Total Medicines</div>
                </div>
              </div>

              <div className="space-y-3">
                {getFinalMedicineList().map((medicine, index) => (
                  <div key={index} className={`p-4 rounded-lg border ${
                    medicine.type === 'alternative' ? 'bg-green-50 border-green-200' : 
                    medicine.type === 'no-alternatives' ? 'bg-gray-50 border-gray-200' :
                    'bg-blue-50 border-blue-200'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-lg">{medicine.name}</h4>
                          <Badge variant={
                            medicine.type === 'alternative' ? 'default' : 
                            medicine.type === 'no-alternatives' ? 'secondary' :
                            'secondary'
                          }>
                            {medicine.type === 'alternative' ? 'Alternative' : 
                             medicine.type === 'no-alternatives' ? 'No Alternatives' :
                             'Original'}
                          </Badge>
                        </div>
                        
                        {medicine.type === 'alternative' && medicine.original_name !== medicine.name && (
                          <div className="text-sm text-muted-foreground mb-2">
                            Replaces: <span className="font-medium">{medicine.original_name}</span>
                          </div>
                        )}

                        {medicine.type === 'no-alternatives' && (
                          <div className="text-sm text-muted-foreground mb-2">
                            Original prescription (no alternatives available)
                          </div>
                        )}
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Quantity:</span>
                            <div className="font-medium">{medicine.quantity}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Generic:</span>
                            <div className="font-medium">{medicine.generic}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Price:</span>
                            <div className="font-medium">₹{medicine.price.toFixed(2)}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Manufacturer:</span>
                            <div className="font-medium">{medicine.manufacturer}</div>
                          </div>
                        </div>
                        
                        {medicine.type === 'alternative' && medicine.savings_amount > 0 && (
                          <div className="mt-3 p-2 bg-green-100 rounded text-sm">
                            <span className="font-medium text-green-800">
                              💰 Save ₹{medicine.savings_amount.toFixed(2)} ({medicine.savings_percent.toFixed(1)}%)
                            </span>
                            <div className="text-green-700">
                              Total savings for {medicine.quantity}: ₹{medicine.total_savings.toFixed(2)}
                            </div>
                          </div>
                        )}

                        {medicine.type === 'no-alternatives' && (
                          <div className="mt-3 p-2 bg-gray-100 rounded text-sm">
                            <span className="font-medium text-gray-800">
                              ℹ️ No alternatives available
                            </span>
                            <div className="text-gray-700">
                              This medicine will be included as originally prescribed
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <DialogFooter className="flex gap-2">
              <Button variant="outline" onClick={() => setShowFinalList(false)}>
                Close
              </Button>
              <Button onClick={handleStartNewPrescription} className="bg-blue-600 hover:bg-blue-700">
                <Upload className="w-4 h-4 mr-2" />
                Start New Prescription
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
      
      {/* Processing Indicator */}
      <ProcessingIndicator isVisible={isProcessing} keepAlive={true} />
    </div>
  );
};

export default Index;
