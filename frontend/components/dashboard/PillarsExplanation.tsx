"use client";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Building2, Globe, BarChart3, MessageSquare } from "lucide-react";

interface PillarsExplanationProps {
  showTooltips?: boolean; // Show tooltips on hover
  expanded?: boolean; // Show full explanation
}

const pillarInfo = {
  fundamental: {
    name: "Fundamental Analysis",
    icon: Building2,
    description: "Analyzes company financials, earnings reports, P/E ratios, revenue growth, and balance sheet strength to assess intrinsic value.",
    data: "Financial statements, earnings data, company metrics",
    importance: "Identifies undervalued or overvalued assets based on financial health",
  },
  economic: {
    name: "Economic Analysis",
    icon: Globe,
    description: "Analyzes macroeconomic indicators including GDP, inflation, unemployment, Federal Reserve policies, and global economic trends.",
    data: "GDP, inflation rates, unemployment, interest rates, Fed policies",
    importance: "Understands broader market conditions affecting asset prices",
  },
  technical: {
    name: "Technical Analysis",
    icon: BarChart3,
    description: "Analyzes price patterns, trends, and technical indicators (RSI, MACD, Moving Averages, Bollinger Bands) on 15-minute charts.",
    data: "Price charts, volume, technical indicators",
    importance: "Identifies entry/exit points and trend reversals",
  },
  sentiment: {
    name: "Social Sentiment Analysis",
    icon: MessageSquare,
    description: "Analyzes news headlines, social media sentiment, and market mood using AI-powered FinBERT model to gauge market psychology.",
    data: "News articles, social media, market sentiment scores",
    importance: "Captures market psychology and potential price movements",
  },
};

export function PillarsExplanation({ showTooltips = true, expanded = false }: PillarsExplanationProps) {
  if (expanded) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(pillarInfo).map(([key, pillar]) => {
          const Icon = pillar.icon;
          return (
            <div
              key={key}
              className="p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50"
            >
              <div className="flex items-center space-x-3 mb-2">
                <Icon className="w-6 h-6 text-alchmai-purple" />
                <div className="font-semibold text-alchmai-text-primary">{pillar.name}</div>
              </div>
              <div className="text-sm text-alchmai-text-secondary space-y-2">
                <p>{pillar.description}</p>
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Data Sources:</div>
                  <div>{pillar.data}</div>
                </div>
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Why It Matters:</div>
                  <div>{pillar.importance}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  if (!showTooltips) return null;

  // Check if tooltip component exists
  try {
    return (
      <TooltipProvider>
        <div className="flex items-center space-x-4">
          {Object.entries(pillarInfo).map(([key, pillar]) => {
            const Icon = pillar.icon;
            return (
              <Tooltip key={key}>
                <TooltipTrigger asChild>
                  <div className="flex items-center space-x-2 cursor-help">
                    <Icon className="w-5 h-5 text-alchmai-purple" />
                    <span className="text-sm text-alchmai-text-secondary">{pillar.name}</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs bg-alchmai-darker border-alchmai-purple/30">
                  <div className="space-y-2">
                    <div className="font-semibold text-alchmai-text-primary">{pillar.name}</div>
                    <div className="text-sm text-alchmai-text-secondary">{pillar.description}</div>
                  </div>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    );
  } catch {
    // Tooltip component not available, return simple version
    return (
      <div className="flex items-center space-x-4">
        {Object.entries(pillarInfo).map(([key, pillar]) => {
          const Icon = pillar.icon;
          return (
            <div key={key} className="flex items-center space-x-2">
              <Icon className="w-5 h-5 text-alchmai-purple" />
              <span className="text-sm text-alchmai-text-secondary">{pillar.name}</span>
            </div>
          );
        })}
      </div>
    );
  }
}
