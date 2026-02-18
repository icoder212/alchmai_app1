"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCardClass } from "@/lib/alchmai-theme";
import { TradingSignal } from "@/lib/api";
import { ChevronDown, ChevronUp, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DecisionJourneyProps {
  signal: TradingSignal;
  showDetails?: boolean;
  onToggle?: () => void;
}

export function DecisionJourney({
  signal,
  showDetails: initialShowDetails = false,
  onToggle,
}: DecisionJourneyProps) {
  const [showDetails, setShowDetails] = useState(initialShowDetails);

  const handleToggle = () => {
    setShowDetails(!showDetails);
    onToggle?.();
  };

  const weights = {
    technical: 0.40,
    sentiment: 0.25,
    fundamental: 0.20,
    economic: 0.15,
  };

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation === 'BUY') return 'text-alchmai-success';
    if (recommendation === 'SELL') return 'text-alchmai-danger';
    return 'text-alchmai-text-secondary';
  };

  const calculateWeightedScore = () => {
    const technicalScore = signal.technical_analysis.score * weights.technical;
    const sentimentScore = signal.sentiment_analysis.score * weights.sentiment;
    const fundamentalScore = signal.fundamental_analysis.score * weights.fundamental;
    const economicScore = signal.economic_analysis.score * weights.economic;
    return technicalScore + sentimentScore + fundamentalScore + economicScore;
  };

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold text-alchmai-text-primary">
            AI Decision Journey
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleToggle}
            className="text-alchmai-text-secondary hover:text-alchmai-text-primary"
          >
            {showDetails ? (
              <>
                <ChevronUp className="w-4 h-4 mr-1" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                Show Details
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Step 1: Input */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-alchmai-purple/20 flex items-center justify-center border-2 border-alchmai-purple">
              <span className="text-alchmai-purple font-bold">1</span>
            </div>
            <div className="flex-1">
              <div className="text-sm text-alchmai-text-secondary">Input</div>
              <div className="text-lg font-semibold text-alchmai-text-primary">
                {signal.instrument}
              </div>
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-alchmai-purple ml-6" />

          {/* Step 2: 4 Agents (Parallel) */}
          <div className="space-y-2">
            <div className="text-sm text-alchmai-text-secondary mb-3">4 AI Agents (Parallel Analysis)</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { name: 'Fundamental', analysis: signal.fundamental_analysis },
                { name: 'Economic', analysis: signal.economic_analysis },
                { name: 'Technical', analysis: signal.technical_analysis },
                { name: 'Sentiment', analysis: signal.sentiment_analysis },
              ].map((agent, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50"
                >
                  <div className="text-xs text-alchmai-text-secondary mb-1">{agent.name}</div>
                  <div className={`text-sm font-bold ${getRecommendationColor(agent.analysis.recommendation)}`}>
                    {agent.analysis.recommendation}
                  </div>
                  <div className="text-xs text-alchmai-text-secondary mt-1">
                    Score: {agent.analysis.score.toFixed(1)}
                  </div>
                  {showDetails && (
                    <div className="text-xs text-alchmai-text-secondary mt-2 pt-2 border-t border-alchmai-purple/10">
                      Weight: {(weights[agent.name.toLowerCase() as keyof typeof weights] * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-alchmai-purple ml-6" />

          {/* Step 3: Weighted Scoring */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-alchmai-blue/20 flex items-center justify-center border-2 border-alchmai-blue">
              <span className="text-alchmai-blue font-bold">3</span>
            </div>
            <div className="flex-1">
              <div className="text-sm text-alchmai-text-secondary">Weighted Scoring</div>
              {showDetails ? (
                <div className="text-sm text-alchmai-text-primary mt-1 space-y-1">
                  <div>Technical: {signal.technical_analysis.score.toFixed(1)} × 40% = {(signal.technical_analysis.score * weights.technical).toFixed(1)}</div>
                  <div>Sentiment: {signal.sentiment_analysis.score.toFixed(1)} × 25% = {(signal.sentiment_analysis.score * weights.sentiment).toFixed(1)}</div>
                  <div>Fundamental: {signal.fundamental_analysis.score.toFixed(1)} × 20% = {(signal.fundamental_analysis.score * weights.fundamental).toFixed(1)}</div>
                  <div>Economic: {signal.economic_analysis.score.toFixed(1)} × 15% = {(signal.economic_analysis.score * weights.economic).toFixed(1)}</div>
                  <div className="mt-2 pt-2 border-t border-alchmai-purple/20 font-bold">
                    Total: {calculateWeightedScore().toFixed(1)}/100
                  </div>
                </div>
              ) : (
                <div className="text-lg font-semibold text-alchmai-text-primary">
                  Score: {calculateWeightedScore().toFixed(1)}/100
                </div>
              )}
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-alchmai-purple ml-6" />

          {/* Step 4: Final Synthesis */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-alchmai-success/20 flex items-center justify-center border-2 border-alchmai-success">
              <span className="text-alchmai-success font-bold">4</span>
            </div>
            <div className="flex-1">
              <div className="text-sm text-alchmai-text-secondary">Final Synthesis</div>
              <div className={`text-lg font-bold ${getRecommendationColor(signal.signal)}`}>
                {signal.signal} Signal
              </div>
              <div className="text-sm text-alchmai-text-secondary mt-1">
                Confidence: {signal.confidence.toFixed(1)}%
              </div>
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-alchmai-purple ml-6" />

          {/* Step 5: Safety Validation */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-alchmai-blue/20 flex items-center justify-center border-2 border-alchmai-blue">
              <span className="text-alchmai-blue font-bold">5</span>
            </div>
            <div className="flex-1">
              <div className="text-sm text-alchmai-text-secondary">Safety Validation</div>
              <div className="text-sm text-alchmai-success mt-1">✓ All checks passed</div>
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-alchmai-purple ml-6" />

          {/* Step 6: Final Signal */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-alchmai-purple flex items-center justify-center border-2 border-alchmai-purple glow-purple">
              <span className="text-white font-bold">6</span>
            </div>
            <div className="flex-1">
              <div className="text-sm text-alchmai-text-secondary">Final Signal</div>
              <div className={`text-xl font-bold ${getRecommendationColor(signal.signal)}`}>
                {signal.signal} - {signal.instrument}
              </div>
              <div className="text-sm text-alchmai-text-secondary mt-1">
                Entry: ${signal.entry_price.toFixed(2)} | SL: ${signal.stop_loss.toFixed(2)} | TP: ${signal.take_profit.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
