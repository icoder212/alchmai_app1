"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { getCardClass, convertConfidenceTo10Scale, getRatingBadge } from "@/lib/alchmai-theme";
import { formatPercent } from "@/lib/utils";

interface AIConfidenceCardProps {
  confidence: number; // 0-100
  accuracy?: number; // 0-100, optional
  precision?: number; // 0-100, optional
  reliability?: number; // 0-100, optional
}

export function AIConfidenceCard({
  confidence,
  accuracy,
  precision,
  reliability,
}: AIConfidenceCardProps) {
  const score = convertConfidenceTo10Scale(confidence);
  const { rating, colorClass } = getRatingBadge(score);

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30 h-full")}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-alchmai-text-primary uppercase tracking-wide">
            AI Confidence Score
          </h2>
          <div className={`px-2 py-0.5 rounded-full text-xs font-semibold ${colorClass}`}>
            {rating}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Main Score Display */}
          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-bold bg-gradient-to-r from-alchmai-purple to-alchmai-blue bg-clip-text text-transparent">
              {score.toFixed(1)}
            </div>
            <div className="text-lg text-alchmai-text-secondary">/ 10</div>
          </div>

          {/* Breakdown Cards (if provided) */}
          {(accuracy !== undefined || precision !== undefined || reliability !== undefined) && (
            <div className="grid grid-cols-3 gap-2 mt-2">
              {accuracy !== undefined && (
                <div className="bg-alchmai-darker/50 rounded-lg p-2 border border-alchmai-purple/20">
                  <div className="text-xs text-alchmai-text-secondary mb-0.5">Accuracy</div>
                  <div className="text-base font-bold text-alchmai-text-primary">
                    {formatPercent(accuracy)}
                  </div>
                </div>
              )}
              {precision !== undefined && (
                <div className="bg-alchmai-darker/50 rounded-lg p-2 border border-alchmai-purple/20">
                  <div className="text-xs text-alchmai-text-secondary mb-0.5">Precision</div>
                  <div className="text-base font-bold text-alchmai-text-primary">
                    {formatPercent(precision)}
                  </div>
                </div>
              )}
              {reliability !== undefined && (
                <div className="bg-alchmai-darker/50 rounded-lg p-2 border border-alchmai-purple/20">
                  <div className="text-xs text-alchmai-text-secondary mb-0.5">Reliability</div>
                  <div className="text-base font-bold text-alchmai-text-primary">
                    {formatPercent(reliability)}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
