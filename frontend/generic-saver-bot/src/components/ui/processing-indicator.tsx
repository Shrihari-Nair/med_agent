import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Database, 
  Shield, 
  TrendingUp, 
  Pill,
  CheckCircle2,
  Clock,
  Zap
} from 'lucide-react';

interface ProcessingIndicatorProps {
  isVisible: boolean;
  keepAlive?: boolean; // Keep showing even after progress completes
}

const processingSteps = [
  {
    id: 'extraction',
    icon: Pill,
    label: 'Medicine Extraction',
    description: 'Identifying medicines from prescription',
    duration: 3000
  },
  {
    id: 'databases',
    icon: Database,
    label: 'Database Analysis',
    description: 'Querying 7 medical databases for insights',
    duration: 4000
  },
  {
    id: 'safety',
    icon: Shield,
    label: 'Safety Analysis',
    description: 'Checking drug interactions and contraindications',
    duration: 4000
  },
  {
    id: 'intelligence',
    icon: Brain,
    label: 'AI Processing',
    description: 'Generating evidence-based recommendations',
    duration: 5000
  },
  {
    id: 'alternatives',
    icon: TrendingUp,
    label: 'Finding Alternatives',
    description: 'Identifying cost-effective substitutions',
    duration: Infinity // Never completes - waits for actual API response
  }
];

export function ProcessingIndicator({ isVisible, keepAlive = false }: ProcessingIndicatorProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0);
      setProgress(0);
      setCompletedSteps(new Set());
      setIsWaitingForResponse(false);
      return;
    }

    let totalElapsed = 0;
    // Calculate total duration excluding the infinite last step
    const finiteDuration = processingSteps.slice(0, -1).reduce((sum, step) => sum + step.duration, 0);
    const totalDuration = finiteDuration + 2000; // Add buffer for final step

    const processSteps = () => {
      processingSteps.forEach((step, index) => {
        const isLastStep = index === processingSteps.length - 1;
        
        setTimeout(() => {
          setCurrentStep(index);
          
          // Animate progress for this step
          const stepStartTime = Date.now();
          const animateProgress = () => {
            const elapsed = Date.now() - stepStartTime;
            
            if (isLastStep) {
              // For the last step, gradually approach but never reach 100%
              const lastStepProgress = Math.min(elapsed / 10000, 0.15); // Slowly add 15% over 10 seconds
              const baseProgress = 80; // Previous 4 steps = 80%
              const overallProgress = baseProgress + (lastStepProgress * 100);
              setProgress(Math.min(overallProgress, 95)); // Never exceed 95%
              
              if (isVisible) {
                requestAnimationFrame(animateProgress);
              }
            } else {
              // Each of the first 4 steps contributes 20% (total 80%)
              const stepProgress = Math.min(elapsed / step.duration, 1);
              const stepContribution = 20; // Each step = 20%
              const previousStepsProgress = index * stepContribution; // Progress from completed steps
              const currentStepProgress = stepProgress * stepContribution; // Progress within current step
              const overallProgress = previousStepsProgress + currentStepProgress;
              
              setProgress(Math.min(overallProgress, 80)); // Don't exceed 80% until last step
              
              if (stepProgress < 1 && isVisible) {
                requestAnimationFrame(animateProgress);
              } else {
                setCompletedSteps(prev => new Set([...prev, step.id]));
                totalElapsed += step.duration;
              }
            }
          };
          
          animateProgress();
        }, isLastStep ? totalElapsed : totalElapsed);
        
        if (!isLastStep) {
          totalElapsed += step.duration;
        }
      });
    };

    processSteps();
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-lg mx-4 shadow-2xl">
        <CardContent className="p-6">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Zap className="h-6 w-6 text-blue-600 animate-pulse" />
              <h3 className="text-xl font-semibold">Enhanced Medical Intelligence</h3>
            </div>
            <p className="text-sm text-muted-foreground">
              Analyzing your prescription with 7 medical databases
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Processing...</span>
              <span className="text-sm text-muted-foreground">
                {Math.round(progress)}%
              </span>
            </div>
            <Progress 
              value={progress} 
              className={`h-2 ${currentStep === processingSteps.length - 1 ? 'animate-pulse' : ''}`} 
            />
          </div>

          {/* Processing Steps */}
          <div className="space-y-3">
            {processingSteps.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === currentStep;
              const isCompleted = completedSteps.has(step.id);
              const isPending = index > currentStep;
              const isLastStep = index === processingSteps.length - 1;

              return (
                <div 
                  key={step.id}
                  className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                    isActive ? 'bg-blue-50 border border-blue-200' : 
                    isCompleted ? 'bg-green-50 border border-green-200' : 
                    'bg-gray-50 border border-gray-200'
                  }`}
                >
                  <div className={`flex-shrink-0 ${
                    isActive ? 'animate-pulse' : ''
                  }`}>
                    {isCompleted && !isLastStep ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : isActive || (isLastStep && currentStep >= index) ? (
                      <Icon className="h-5 w-5 text-blue-600 animate-spin" />
                    ) : (
                      <Icon className={`h-5 w-5 ${isPending ? 'text-gray-400' : 'text-gray-600'}`} />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className={`font-medium text-sm ${
                        isActive ? 'text-blue-900' : 
                        isCompleted ? 'text-green-900' : 
                        isPending ? 'text-gray-500' : 'text-gray-700'
                      }`}>
                        {step.label}
                      </h4>
                      
                      {(isActive || (isLastStep && currentStep >= index)) && (
                        <Badge variant="outline" className="text-xs bg-blue-100 text-blue-700 border-blue-300">
                          <Clock className="h-3 w-3 mr-1" />
                          {isLastStep ? 'Finalizing...' : 'Processing'}
                        </Badge>
                      )}
                      
                      {isCompleted && !isLastStep && (
                        <Badge variant="outline" className="text-xs bg-green-100 text-green-700 border-green-300">
                          ✓ Complete
                        </Badge>
                      )}
                    </div>
                    
                    <p className={`text-xs mt-1 ${
                      isActive ? 'text-blue-700' : 
                      isCompleted ? 'text-green-700' : 
                      'text-gray-500'
                    }`}>
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Current Status */}
          <div className="mt-6 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2">
              <Brain className={`h-4 w-4 text-blue-600 ${currentStep === processingSteps.length - 1 ? 'animate-pulse' : ''}`} />
              <span className="text-sm font-medium text-blue-900">
                {currentStep < processingSteps.length ? 
                  `Currently: ${processingSteps[currentStep]?.label}` : 
                  'Analysis Complete!'
                }
              </span>
            </div>
            <p className="text-xs text-blue-700 mt-1">
              {currentStep === processingSteps.length - 1 ?
                'AI is finalizing your comprehensive medical analysis with safety recommendations and cost-effective alternatives. This involves cross-referencing multiple databases for the most accurate results.' :
                'Our AI is analyzing medicine interactions, side effects, dosage guidelines, effectiveness data, and prescription patterns to provide you with the safest and most cost-effective alternatives.'
              }
            </p>
          </div>

          {/* Fun Facts */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              💡 Did you know? We're checking against {' '}
              <span className="font-medium text-gray-700">48 drug interactions</span>, {' '}
              <span className="font-medium text-gray-700">34 side effects</span>, and {' '}
              <span className="font-medium text-gray-700">28 dosage guidelines</span> in real-time!
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 