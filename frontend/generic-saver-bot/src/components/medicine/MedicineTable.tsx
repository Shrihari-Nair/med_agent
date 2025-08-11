import { Check, X, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MedicineAlternative } from "@/types/api";
import { EnhancedMedicineInfo } from "@/types/enhanced-medicine";
import { EnhancedMedicineInfoDisplay } from "./EnhancedMedicineInfo";

export type GenericAlternative = MedicineAlternative & {
  id: string;
  availability: "in-stock" | "low-stock" | "out-of-stock";
};

export type MedicineRow = {
  id: string;
  name: string;
  quantity: string;
  generic: string;
  original_price: number;
  alternatives: GenericAlternative[];
  selectedAlternativeId?: string | null;
  approval: "pending" | "approved" | "declined" | "no-alternatives";
};

export interface MedicineTableProps {
  rows: MedicineRow[];
  onApprove: (id: string) => void;
  onDecline: (id: string) => void;
  onAlternativeSelect: (medicineId: string, alternativeId: string) => void;
  databaseInfo?: Map<string, EnhancedMedicineInfo> | null;
}

const currency = (n: number) => `₹${n.toLocaleString("en-IN")}`;

const pct = (x: number) => `${x.toFixed(0)}%`;

export function MedicineTable({ rows, onApprove, onDecline, onAlternativeSelect, databaseInfo }: MedicineTableProps) {
  return (
    <Table className="bg-card rounded-lg border">
      <TableCaption className="text-xs">Review suggested substitutions and approve for savings.</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Prescribed Medicine</TableHead>
          <TableHead>Generic Alternative</TableHead>
          <TableHead>Estimated Savings</TableHead>
          <TableHead className="text-right">Patient Approval</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r) => {
          const selectedAlternative = r.alternatives.find(a => a.id === r.selectedAlternativeId) || r.alternatives[0];
          const savings = selectedAlternative ? selectedAlternative.savings_amount : 0;
          const savingsPct = selectedAlternative ? selectedAlternative.savings_percent : 0;
          const isFinal = r.approval !== "pending";
          
          return (
            <TableRow key={r.id} data-state={isFinal ? "selected" : undefined}>
              <TableCell>
                <div className="font-medium">{r.name}</div>
                <div className="text-xs text-muted-foreground">
                  Original Price {currency(r.original_price)} • {r.quantity}
                </div>
                <div className="text-xs text-blue-600">
                  Generic: {r.generic}
                </div>
              </TableCell>
              <TableCell>
                <div className="space-y-2">
                  {r.approval === "no-alternatives" ? (
                    <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                      <div className="text-sm text-gray-600 font-medium">No alternatives available</div>
                      <div className="text-xs text-gray-500 mt-1">
                        This medicine will be included as-is in your order
                      </div>
                    </div>
                  ) : (
                    <>
                      <Select
                        value={r.selectedAlternativeId || r.alternatives[0]?.id}
                        onValueChange={(value) => onAlternativeSelect(r.id, value)}
                        disabled={isFinal}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select generic alternative" />
                        </SelectTrigger>
                        <SelectContent>
                          {r.alternatives.map((alternative) => (
                            <SelectItem 
                              key={alternative.id} 
                              value={alternative.id}
                            >
                              <div className="flex items-center justify-between w-full">
                                <div className="flex-1">
                                  <div className="font-medium">{alternative.name}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {alternative.manufacturer} • {currency(alternative.price)} • {alternative.class}
                                  </div>
                                </div>
                                <div className="ml-2">
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    alternative.availability === "in-stock" 
                                      ? "bg-green-100 text-green-700" 
                                      : alternative.availability === "low-stock"
                                      ? "bg-orange-100 text-orange-700"
                                      : "bg-red-100 text-red-700"
                                  }`}>
                                    {alternative.stock_quantity > 50 ? "In Stock" 
                                     : alternative.stock_quantity > 10 ? "Low Stock"
                                     : alternative.stock_quantity > 0 ? "Limited Stock"
                                     : "Out of Stock"}
                                  </span>
                                </div>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {selectedAlternative && (
                        <div className="text-xs text-muted-foreground">
                          Selected: {selectedAlternative.name} • {currency(selectedAlternative.price)} • Stock: {selectedAlternative.stock_quantity}
                        </div>
                      )}
                    </>
                  )}
                  
                  {/* Enhanced Database Information */}
                  {databaseInfo && (
                    <>
                      {/* Original Medicine Database Info */}
                      {databaseInfo.has(r.name) && (
                        <EnhancedMedicineInfoDisplay 
                          medicineInfo={databaseInfo.get(r.name)!}
                          isAlternative={false}
                        />
                      )}
                      
                      {/* Selected Alternative Database Info */}
                      {selectedAlternative && databaseInfo.has(selectedAlternative.name) && (
                        <EnhancedMedicineInfoDisplay 
                          medicineInfo={databaseInfo.get(selectedAlternative.name)!}
                          isAlternative={true}
                        />
                      )}
                    </>
                  )}
                </div>
              </TableCell>
              <TableCell>
                {r.approval === "no-alternatives" ? (
                  <div className="text-gray-500">
                    <div className="text-sm">No savings</div>
                    <div className="text-xs">Original price</div>
                  </div>
                ) : (
                  <>
                    <div className="font-medium text-green-600">{currency(savings)}</div>
                    <div className="text-xs text-muted-foreground">{pct(savingsPct)} saved</div>
                    {selectedAlternative && (
                      <div className="text-xs text-blue-600 mt-1">
                        vs. original ₹{r.original_price.toLocaleString("en-IN")}
                      </div>
                    )}
                  </>
                )}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  {r.approval === "no-alternatives" ? (
                    <div className="text-xs text-gray-500 px-3 py-2">
                      Auto-included
                    </div>
                  ) : (
                    <>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => onApprove(r.id)}
                        disabled={isFinal || !selectedAlternative}
                        aria-label="Approve substitution"
                        className="bg-green-600 hover:bg-green-700 text-white"
                      >
                        <Check className="w-4 h-4" />
                        <span className="hidden md:inline ml-1">Approve</span>
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onDecline(r.id)}
                        disabled={isFinal}
                        aria-label="Decline substitution"
                      >
                        <X className="w-4 h-4" />
                        <span className="hidden md:inline ml-1">Decline</span>
                      </Button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
