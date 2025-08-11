import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { SafetyBadge } from '@/components/ui/safety-badge';
import { PrescriptionAnalysis, OverallRecommendations } from '@/types/api';
import { AlertTriangle, Shield, User, Stethoscope, Calendar, Info } from 'lucide-react';

export interface SafetyAnalysisProps {
  analysis: PrescriptionAnalysis;
  recommendations: OverallRecommendations;
}

export function SafetyAnalysis({ analysis, recommendations }: SafetyAnalysisProps) {
  const getSafetyLevel = (): 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK' => {
    if (analysis.safety_score) return analysis.safety_score;
    
    // Fallback: determine from assessment text
    const assessment = analysis.overall_safety_assessment.toLowerCase();
    if (assessment.includes('high risk') || assessment.includes('severe')) return 'HIGH_RISK';
    if (assessment.includes('moderate risk') || assessment.includes('moderate')) return 'MODERATE_RISK';
    return 'LOW_RISK';
  };

  const safetyLevel = getSafetyLevel();

  return (
    <div className="space-y-4">
      {/* Overall Safety Assessment */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Shield className="h-5 w-5" />
            Prescription Safety Analysis
            <SafetyBadge level={safetyLevel} />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {analysis.overall_safety_assessment}
          </p>
          
          {analysis.recommendations_summary && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Summary:</strong> {analysis.recommendations_summary}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Critical Warnings */}
      {analysis.critical_warnings && analysis.critical_warnings.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg text-red-700">
              <AlertTriangle className="h-5 w-5" />
              Critical Safety Warnings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {analysis.critical_warnings.map((warning, index) => (
              <Alert key={index} className="border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  {warning}
                </AlertDescription>
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Clinical Recommendations */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Stethoscope className="h-5 w-5" />
            Clinical Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Prescription Changes */}
          {recommendations.prescription_changes && (
            <div className="space-y-2">
              <h4 className="font-medium text-sm flex items-center gap-2">
                <Info className="h-4 w-4" />
                Recommended Changes
              </h4>
              <p className="text-sm text-muted-foreground pl-6">
                {recommendations.prescription_changes}
              </p>
            </div>
          )}

          {/* Follow-up */}
          {recommendations.follow_up_needed && (
            <div className="space-y-2">
              <h4 className="font-medium text-sm flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Follow-up Required
              </h4>
              <p className="text-sm text-muted-foreground pl-6">
                {recommendations.follow_up_needed}
              </p>
            </div>
          )}

          {/* Consultation Requirements */}
          <div className="flex flex-wrap gap-2">
            {recommendations.pharmacist_consultation && (
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                <User className="h-3 w-3 mr-1" />
                Pharmacist Consultation Recommended
              </Badge>
            )}
            {recommendations.doctor_consultation && (
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <Stethoscope className="h-3 w-3 mr-1" />
                Doctor Consultation Required
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 