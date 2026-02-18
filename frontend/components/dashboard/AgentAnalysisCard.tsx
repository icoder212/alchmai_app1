"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AgentAnalysis } from "@/lib/api";
import { getCardClass } from "@/lib/alchmai-theme";
import { BarChart2, Globe, TrendingUp, MessageSquare, type LucideIcon } from "lucide-react";

interface AgentAnalysisCardProps {
  title: string;
  analysis: AgentAnalysis;
}

const AGENT_META: Record<
  string,
  { Icon: LucideIcon; iconColor: string; description: string; weight: string }
> = {
  fundamental: {
    Icon: BarChart2,
    iconColor: "text-alchmai-blue bg-alchmai-blue/10",
    description: "P/E ratio, earnings, revenue growth, debt & margins",
    weight: "20%",
  },
  economic: {
    Icon: Globe,
    iconColor: "text-alchmai-purple bg-alchmai-purple/10",
    description: "GDP, inflation, Fed rate, unemployment & economic calendar",
    weight: "15%",
  },
  technical: {
    Icon: TrendingUp,
    iconColor: "text-alchmai-success bg-alchmai-success/10",
    description: "RSI, MACD, SMA-20, Bollinger Bands on 15-min chart",
    weight: "40%",
  },
  sentiment: {
    Icon: MessageSquare,
    iconColor: "text-yellow-400 bg-yellow-400/10",
    description: "News headlines scored by FinBERT financial AI model",
    weight: "25%",
  },
};

export function AgentAnalysisCard({ title, analysis }: AgentAnalysisCardProps) {
  const isBuy = analysis.recommendation === "BUY";
  const isSell = analysis.recommendation === "SELL";

  const meta = AGENT_META[analysis.agent] ?? {
    Icon: BarChart2,
    iconColor: "text-alchmai-text-secondary bg-alchmai-text-secondary/10",
    description: "",
    weight: "–",
  };

  const { Icon } = meta;

  const recColor = isBuy
    ? "text-alchmai-success"
    : isSell
    ? "text-alchmai-danger"
    : "text-alchmai-text-secondary";

  const recBg = isBuy
    ? "bg-alchmai-success/10 border-alchmai-success/30"
    : isSell
    ? "bg-alchmai-danger/10 border-alchmai-danger/30"
    : "bg-alchmai-text-secondary/10 border-alchmai-text-secondary/20";

  const barColor = isBuy
    ? "bg-alchmai-success"
    : isSell
    ? "bg-alchmai-danger"
    : "bg-alchmai-text-secondary";

  return (
    <Card
      className={getCardClass(
        true,
        "border-alchmai-purple/30 hover:border-alchmai-purple/50 transition-all h-full flex flex-col"
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${meta.iconColor}`}>
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-bold text-alchmai-text-primary leading-tight">
                {title}
              </CardTitle>
              <p className="text-xs text-alchmai-text-secondary mt-0.5">
                {meta.description}
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold text-alchmai-purple bg-alchmai-purple/10 border border-alchmai-purple/30 px-2 py-0.5 rounded-full flex-shrink-0">
            {meta.weight}
          </span>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 flex flex-col flex-1">
        {/* Recommendation badge */}
        <div
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-sm font-bold ${recColor} ${recBg}`}
        >
          {isBuy ? "▲" : isSell ? "▼" : "◼"} {analysis.recommendation}
        </div>

        {/* Score bar — animated fill */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-alchmai-text-secondary">Score</span>
            <span className="text-alchmai-text-primary font-semibold">
              {analysis.score.toFixed(1)} / 100
            </span>
          </div>
          <div className="w-full bg-alchmai-darker rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full animate-score-fill ${barColor}`}
              style={{ width: `${Math.min(analysis.score, 100)}%` }}
            />
          </div>
        </div>

        {/* Confidence — inline progress dot */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-alchmai-text-secondary">Confidence</span>
          <div className="flex items-center gap-2">
            <div className="w-16 bg-alchmai-darker rounded-full h-1 overflow-hidden">
              <div
                className={`h-1 rounded-full animate-score-fill ${barColor} opacity-60`}
                style={{ width: `${Math.min(analysis.confidence, 100)}%` }}
              />
            </div>
            <span className="text-alchmai-text-primary font-semibold">
              {analysis.confidence.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Reasoning */}
        <div className="pt-2 border-t border-alchmai-purple/20 mt-auto">
          <p className="text-xs text-alchmai-text-secondary leading-relaxed">
            {analysis.reasoning}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
