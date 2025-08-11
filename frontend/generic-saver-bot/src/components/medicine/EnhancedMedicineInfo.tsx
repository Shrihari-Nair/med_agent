import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ChevronDown, 
  ChevronUp, 
  AlertTriangle, 
  Activity,
  Clock,
  TrendingUp,
  Users,
  Shield,
  Info
} from 'lucide-react';
import { EnhancedMedicineInfo } from '@/types/enhanced-medicine';

interface EnhancedMedicineInfoProps {
  medicineInfo: EnhancedMedicineInfo;
  isAlternative?: boolean;
}

export function EnhancedMedicineInfoDisplay({ medicineInfo, isAlternative = false }: EnhancedMedicineInfoProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="mt-2 border border-blue-200 rounded-lg bg-blue-50/30 transition-colors">
      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            className="w-full justify-between p-3 h-auto text-left hover:bg-blue-100/80 hover:text-blue-900 transition-colors duration-200"
            size="sm"
          >
            <span className="text-sm font-medium text-blue-700">
              💊 Medicine Info {isAlternative ? '(Alternative)' : '(Original)'}
            </span>
            {isExpanded ? <ChevronUp className="h-4 w-4 text-blue-600" /> : <ChevronDown className="h-4 w-4 text-blue-600" />}
          </Button>
        </CollapsibleTrigger>
        
        <CollapsibleContent className="px-3 pb-3">
          <div className="space-y-3 text-sm">
            
            {/* Drug Interactions */}
            {medicineInfo.drugInteractions && (
              <div className="space-y-2">
                <h5 className="font-medium flex items-center gap-1 text-red-700">
                  <AlertTriangle className="h-3 w-3" />
                  Drug Interactions ({medicineInfo.drugInteractions.total})
                </h5>
                {medicineInfo.drugInteractions.severe > 0 && (
                  <Alert className="border-red-200 bg-red-50 py-2">
                    <AlertDescription className="text-red-800 text-xs">
                      ⚠️ {medicineInfo.drugInteractions.severe} severe interactions detected
                    </AlertDescription>
                  </Alert>
                )}
                <div className="grid gap-1">
                  {medicineInfo.drugInteractions.interactions.slice(0, 3).map((interaction, idx) => (
                    <div key={idx} className="text-xs bg-white p-2 rounded border">
                      <span className="font-medium">{interaction.drug}</span>
                      <Badge variant="outline" className={`ml-2 text-xs ${
                        interaction.severity === 'severe' ? 'border-red-300 text-red-700' :
                        interaction.severity === 'moderate' ? 'border-orange-300 text-orange-700' :
                        'border-blue-300 text-blue-700'
                      }`}>
                        {interaction.severity}
                      </Badge>
                      <p className="text-gray-600 mt-1">{interaction.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Side Effects */}
            {medicineInfo.sideEffects && medicineInfo.sideEffects.length > 0 && (
              <div className="space-y-2">
                <h5 className="font-medium flex items-center gap-1 text-orange-700">
                  <Activity className="h-3 w-3" />
                  Common Side Effects
                </h5>
                <div className="grid grid-cols-1 gap-1">
                  {medicineInfo.sideEffects.slice(0, 4).map((effect, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-white p-2 rounded border text-xs">
                      <span>{effect.effect}</span>
                      <div className="flex gap-2">
                        <Badge variant="outline" className="text-xs">
                          {effect.frequency}%
                        </Badge>
                        <Badge variant="outline" className={`text-xs ${
                          effect.severity === 'severe' ? 'border-red-300 text-red-700' :
                          effect.severity === 'moderate' ? 'border-orange-300 text-orange-700' :
                          'border-green-300 text-green-700'
                        }`}>
                          {effect.severity}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Dosage Information */}
            {medicineInfo.dosageInfo && (
              <div className="space-y-2">
                <h5 className="font-medium flex items-center gap-1 text-blue-700">
                  <Clock className="h-3 w-3" />
                  Dosage Guidelines
                </h5>
                <div className="bg-white p-2 rounded border text-xs space-y-1">
                  <div><span className="font-medium">Age Group:</span> {medicineInfo.dosageInfo.ageGroup}</div>
                  <div><span className="font-medium">Recommended:</span> {medicineInfo.dosageInfo.recommendedDose}</div>
                  <div><span className="font-medium">Max Daily:</span> {medicineInfo.dosageInfo.maxDailyDose}</div>
                  <div><span className="font-medium">Method:</span> {medicineInfo.dosageInfo.administration}</div>
                </div>
              </div>
            )}

            {/* Effectiveness */}
            {medicineInfo.effectiveness && (
              <div className="space-y-2">
                <h5 className="font-medium flex items-center gap-1 text-green-700">
                  <TrendingUp className="h-3 w-3" />
                  Effectiveness Data
                </h5>
                <div className="bg-white p-2 rounded border text-xs space-y-1">
                  <div><span className="font-medium">Condition:</span> {medicineInfo.effectiveness.condition}</div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Rating:</span> 
                    <div className="flex items-center gap-1">
                      <div className="w-12 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${medicineInfo.effectiveness.rating}%` }}
                        ></div>
                      </div>
                      <span>{medicineInfo.effectiveness.rating}%</span>
                    </div>
                  </div>
                  <div><span className="font-medium">Patient Satisfaction:</span> {medicineInfo.effectiveness.patientSatisfaction}%</div>
                  <div><span className="font-medium">Evidence:</span> {medicineInfo.effectiveness.studyData}</div>
                </div>
              </div>
            )}

            {/* Treatable Conditions */}
            {medicineInfo.conditions && medicineInfo.conditions.length > 0 && (
              <div className="space-y-2">
                <h5 className="font-medium flex items-center gap-1 text-purple-700">
                  <Shield className="h-3 w-3" />
                  Treatable Conditions
                </h5>
                <div className="flex flex-wrap gap-1">
                  {medicineInfo.conditions.slice(0, 6).map((condition, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs bg-white">
                      {condition.condition} ({condition.effectiveness})
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Prescription Patterns */}
            {medicineInfo.prescriptionPatterns && (
              <div className="space-y-2">
                <h5 className="font-medium flex items-center gap-1 text-indigo-700">
                  <Users className="h-3 w-3" />
                  Prescription Insights
                </h5>
                <div className="bg-white p-2 rounded border text-xs space-y-1">
                  {medicineInfo.prescriptionPatterns.commonlyPrescribed.length > 0 && (
                    <div>
                      <span className="font-medium">Often prescribed with:</span> 
                      <div className="flex flex-wrap gap-1 mt-1">
                        {medicineInfo.prescriptionPatterns.commonlyPrescribed.slice(0, 3).map((med, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {med}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  <div><span className="font-medium">Usage Frequency:</span> {medicineInfo.prescriptionPatterns.frequencyUsed}</div>
                  {medicineInfo.prescriptionPatterns.seasonalTrends && (
                    <div><span className="font-medium">Trends:</span> {medicineInfo.prescriptionPatterns.seasonalTrends}</div>
                  )}
                </div>
              </div>
            )}
            
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
} 