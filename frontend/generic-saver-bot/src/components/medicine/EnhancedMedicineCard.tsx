import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { RecommendationBadge, WarningBadge } from '@/components/ui/safety-badge';
import { MedicineAlternativeAnalysis, EnhancedAlternative } from '@/types/api';
import { 
  ChevronDown, 
  ChevronUp, 
  Pill, 
  AlertTriangle, 
  TrendingUp, 
  Shield, 
  Clock,
  Star,
  Activity,
  Eye,
  DollarSign
} from 'lucide-react';

export interface EnhancedMedicineCardProps {
  analysis: MedicineAlternativeAnalysis;
  onAlternativeSelect?: (alternativeName: string) => void;
  selectedAlternative?: string;
}

export function EnhancedMedicineCard({ 
  analysis, 
  onAlternativeSelect, 
  selectedAlternative 
}: EnhancedMedicineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAlternativeDetails, setShowAlternativeDetails] = useState<string | null>(null);
  
  const { original_medicine, recommended_alternatives, clinical_notes, safety_considerations } = analysis;

  const getEffectivenessColor = (rating?: number): string => {
    if (!rating) return 'text-gray-500';
    if (rating >= 85) return 'text-green-600';
    if (rating >= 70) return 'text-blue-600';
    if (rating >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatEffectiveness = (effectiveness: string): { rating: number | null, text: string } => {
    const match = effectiveness.match(/(\d+)%/);
    const rating = match ? parseInt(match[1]) : null;
    return { rating, text: effectiveness };
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <CardTitle className="flex items-center gap-2">
              <Pill className="h-5 w-5" />
              {original_medicine.name}
              {!original_medicine.age_appropriate && (
                <WarningBadge severity="severe" className="ml-2">
                  Age Restriction
                </WarningBadge>
              )}
            </CardTitle>
            <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
              <span>{original_medicine.current_quantity}</span>
              {original_medicine.basic_info && (
                <>
                  <span>•</span>
                  <span>{original_medicine.basic_info.class}</span>
                  <span>•</span>
                  <span>{original_medicine.basic_info.generic_name}</span>
                </>
              )}
            </div>
          </div>
          
          <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm">
                {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </CollapsibleTrigger>
          </Collapsible>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Safety Concerns */}
        {original_medicine.safety_concerns && original_medicine.safety_concerns.length > 0 && (
          <Alert className="border-yellow-200 bg-yellow-50">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              <strong>Safety Concerns:</strong> {original_medicine.safety_concerns.join(', ')}
            </AlertDescription>
          </Alert>
        )}

        {/* Safety Statistics */}
        {safety_considerations && (
          <div className="grid grid-cols-3 gap-4 p-3 bg-gray-50 rounded-md">
            <div className="text-center">
              <div className="font-semibold text-lg">{safety_considerations.drug_interactions}</div>
              <div className="text-xs text-muted-foreground">Drug Interactions</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-lg">{safety_considerations.severe_side_effects}</div>
              <div className="text-xs text-muted-foreground">Severe Side Effects</div>
            </div>
            <div className="text-center">
              <div className={`font-semibold text-lg ${safety_considerations.age_restrictions ? 'text-red-600' : 'text-green-600'}`}>
                {safety_considerations.age_restrictions ? 'Yes' : 'No'}
              </div>
              <div className="text-xs text-muted-foreground">Age Restrictions</div>
            </div>
          </div>
        )}

        {/* Alternatives */}
        <div className="space-y-3">
          <h4 className="font-medium flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Recommended Alternatives ({recommended_alternatives.length})
          </h4>
          
          {recommended_alternatives.map((alternative, index) => (
            <AlternativeOption
              key={index}
              alternative={alternative}
              isSelected={selectedAlternative === alternative.name}
              onSelect={() => onAlternativeSelect?.(alternative.name)}
              showDetails={showAlternativeDetails === alternative.name}
              onToggleDetails={() => 
                setShowAlternativeDetails(
                  showAlternativeDetails === alternative.name ? null : alternative.name
                )
              }
            />
          ))}
        </div>

        {/* Clinical Notes */}
        {clinical_notes && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <h5 className="font-medium text-blue-900 mb-1 flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Clinical Notes
            </h5>
            <p className="text-sm text-blue-800">{clinical_notes}</p>
          </div>
        )}

        {/* Expanded Details */}
        <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
          <CollapsibleContent className="space-y-3">
            {/* Common Side Effects */}
            {original_medicine.common_side_effects && original_medicine.common_side_effects.length > 0 && (
              <div className="space-y-2">
                <h5 className="font-medium text-sm">Common Side Effects</h5>
                <div className="grid grid-cols-1 gap-2">
                  {original_medicine.common_side_effects.map((effect, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
                      <span>{effect.effect}</span>
                      <Badge variant="outline" className="text-xs">
                        {effect.frequency}% • {effect.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>
  );
}

interface AlternativeOptionProps {
  alternative: EnhancedAlternative;
  isSelected: boolean;
  onSelect: () => void;
  showDetails: boolean;
  onToggleDetails: () => void;
}

function AlternativeOption({ 
  alternative, 
  isSelected, 
  onSelect, 
  showDetails, 
  onToggleDetails 
}: AlternativeOptionProps) {
  const formatEffectiveness = (effectiveness: string): { rating: number | null, text: string } => {
    const match = effectiveness.match(/(\d+)%/);
    const rating = match ? parseInt(match[1]) : null;
    return { rating, text: effectiveness };
  };
  
  const effectiveness = formatEffectiveness(alternative.effectiveness);

  return (
    <div className={`border rounded-lg p-3 transition-colors ${
      isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2 flex-wrap">
            <h5 className="font-medium">{alternative.name}</h5>
            <RecommendationBadge strength={alternative.recommendation_strength} />
            {!alternative.age_appropriate && (
              <WarningBadge severity="moderate">Age Restriction</WarningBadge>
            )}
          </div>
          
          <p className="text-sm text-muted-foreground">{alternative.rationale}</p>
          
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-1">
              <Activity className="h-3 w-3" />
              <span className={getEffectivenessColor(effectiveness.rating)}>
                {alternative.effectiveness}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <DollarSign className="h-3 w-3" />
              <span>{alternative.cost_comparison}</span>
            </div>
            {alternative.evidence_level && (
              <Badge variant="outline" className="text-xs">
                {alternative.evidence_level} evidence
              </Badge>
            )}
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onToggleDetails}
          >
            {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
          <Button 
            variant={isSelected ? "default" : "outline"} 
            size="sm" 
            onClick={onSelect}
          >
            {isSelected ? 'Selected' : 'Select'}
          </Button>
        </div>
      </div>

      {/* Alternative Details */}
      <Collapsible open={showDetails}>
        <CollapsibleContent className="mt-3 pt-3 border-t space-y-3">
          {alternative.dosing_recommendation && (
            <div>
              <h6 className="font-medium text-sm flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Dosing
              </h6>
              <p className="text-sm text-muted-foreground pl-4">{alternative.dosing_recommendation}</p>
            </div>
          )}
          
          <div>
            <h6 className="font-medium text-sm flex items-center gap-1">
              <Shield className="h-3 w-3" />
              Safety Profile
            </h6>
            <p className="text-sm text-muted-foreground pl-4">{alternative.safety_profile}</p>
          </div>
          
          {alternative.monitoring_required && (
            <div>
              <h6 className="font-medium text-sm flex items-center gap-1">
                <Eye className="h-3 w-3" />
                Monitoring Required
              </h6>
              <p className="text-sm text-muted-foreground pl-4">{alternative.monitoring_required}</p>
            </div>
          )}

          {alternative.common_side_effects && alternative.common_side_effects.length > 0 && (
            <div>
              <h6 className="font-medium text-sm">Common Side Effects</h6>
              <div className="flex flex-wrap gap-1 pl-4">
                {alternative.common_side_effects.map((effect, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {effect}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CollapsibleContent>
      </Collapsible>
    </div>
  );

  function getEffectivenessColor(rating?: number): string {
    if (!rating) return 'text-gray-500';
    if (rating >= 85) return 'text-green-600';
    if (rating >= 70) return 'text-blue-600';
    if (rating >= 50) return 'text-yellow-600';
    return 'text-red-600';
  }
} 