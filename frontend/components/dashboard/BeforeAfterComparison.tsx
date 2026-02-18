"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCardClass } from "@/lib/alchmai-theme";
import { Clock, FileText, TrendingUp, Zap, BarChart3, Target } from "lucide-react";

interface BeforeAfterComparisonProps {
  show?: boolean; // Control visibility, can be in demo mode
}

export function BeforeAfterComparison({ show = true }: BeforeAfterComparisonProps) {
  if (!show) return null;

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-alchmai-text-primary text-center">
          Transform Your Trading with AI
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-2 gap-6">
          {/* BEFORE ALCHMAI */}
          <div className="space-y-4">
            <div className="text-xl font-bold text-alchmai-danger mb-4">BEFORE ALCHMAI</div>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-danger/20 bg-alchmai-darker/30">
                <Clock className="w-5 h-5 text-alchmai-danger mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Research Time</div>
                  <div className="text-sm text-alchmai-text-secondary">4-6 hrs/trade</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-danger/20 bg-alchmai-darker/30">
                <FileText className="w-5 h-5 text-alchmai-danger mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Source</div>
                  <div className="text-sm text-alchmai-text-secondary">Manual Analysis</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-danger/20 bg-alchmai-darker/30">
                <BarChart3 className="w-5 h-5 text-alchmai-danger mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Analysis Type</div>
                  <div className="text-sm text-alchmai-text-secondary">Single-factor analysis</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-danger/20 bg-alchmai-darker/30">
                <Clock className="w-5 h-5 text-alchmai-danger mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Decision Speed</div>
                  <div className="text-sm text-alchmai-text-secondary">Slow decision-making</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-danger/20 bg-alchmai-darker/30">
                <Target className="w-5 h-5 text-alchmai-danger mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Accuracy</div>
                  <div className="text-sm text-alchmai-text-secondary">Lower accuracy</div>
                </div>
              </div>
            </div>
          </div>

          {/* WITH ALCHMAI */}
          <div className="space-y-4">
            <div className="text-xl font-bold text-alchmai-success mb-4">WITH ALCHMAI</div>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-success/20 bg-alchmai-success/10">
                <Zap className="w-5 h-5 text-alchmai-success mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">AI Analysis</div>
                  <div className="text-sm text-alchmai-text-secondary">Instant (20-30 sec)</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-success/20 bg-alchmai-success/10">
                <Zap className="w-5 h-5 text-alchmai-success mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Source</div>
                  <div className="text-sm text-alchmai-text-secondary">Automated 4-Pillar AI</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-success/20 bg-alchmai-success/10">
                <BarChart3 className="w-5 h-5 text-alchmai-success mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Analysis Type</div>
                  <div className="text-sm text-alchmai-text-secondary">Multi-factor comprehensive analysis</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-success/20 bg-alchmai-success/10">
                <Zap className="w-5 h-5 text-alchmai-success mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Decision Speed</div>
                  <div className="text-sm text-alchmai-text-secondary">Fast, accurate decisions</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-alchmai-success/20 bg-alchmai-success/10">
                <Target className="w-5 h-5 text-alchmai-success mt-0.5" />
                <div>
                  <div className="font-semibold text-alchmai-text-primary">Accuracy</div>
                  <div className="text-sm text-alchmai-text-secondary">Higher accuracy</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Improvement Metrics */}
        <div className="mt-8 pt-6 border-t border-alchmai-purple/20">
          <div className="text-center mb-4">
            <div className="text-lg font-bold text-alchmai-text-primary">Performance Improvement</div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50">
              <div className="text-2xl font-bold text-alchmai-success">76.3%</div>
              <div className="text-sm text-alchmai-text-secondary mt-1">Win Rate</div>
              <div className="text-xs text-alchmai-success mt-1">+28%</div>
            </div>
            <div className="text-center p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50">
              <div className="text-2xl font-bold text-alchmai-success">12.4%</div>
              <div className="text-sm text-alchmai-text-secondary mt-1">Avg Return</div>
              <div className="text-xs text-alchmai-success mt-1">+150%</div>
            </div>
            <div className="text-center p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50">
              <div className="text-2xl font-bold text-alchmai-success">127</div>
              <div className="text-sm text-alchmai-text-secondary mt-1">Trades/Month</div>
              <div className="text-xs text-alchmai-success mt-1">+60%</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
