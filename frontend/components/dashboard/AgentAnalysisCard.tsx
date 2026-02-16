"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AgentAnalysis } from "@/lib/api";
import { formatPercent } from "@/lib/utils";

interface AgentAnalysisCardProps {
  title: string;
  analysis: AgentAnalysis;
}

export function AgentAnalysisCard({ title, analysis }: AgentAnalysisCardProps) {
  const isBuy = analysis.recommendation === "BUY";
  const isSell = analysis.recommendation === "SELL";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Recommendation</span>
            <span
              className={`font-semibold ${
                isBuy
                  ? "text-green-600"
                  : isSell
                  ? "text-red-600"
                  : "text-gray-600"
              }`}
            >
              {analysis.recommendation}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Score</span>
            <span className="font-semibold">{analysis.score.toFixed(1)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Confidence</span>
            <span className="font-semibold">{formatPercent(analysis.confidence)}</span>
          </div>
          <div className="pt-2 border-t">
            <div className="text-sm text-muted-foreground mb-1">Reasoning</div>
            <div className="text-sm">{analysis.reasoning}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
