"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCardClass } from "@/lib/alchmai-theme";
import { TrendingUp, TrendingDown } from "lucide-react";

interface PerformanceMetricsProps {
  winRate: number;
  winRateChange: number;
  avgReturn: number;
  avgReturnChange: number;
  tradesPerMonth: number;
  tradesPerMonthChange: number;
  loading?: boolean;
}

export function PerformanceMetrics({
  winRate,
  winRateChange,
  avgReturn,
  avgReturnChange,
  tradesPerMonth,
  tradesPerMonthChange,
  loading = false,
}: PerformanceMetricsProps) {
  const metrics = [
    { label: "Win Rate",       value: `${winRate.toFixed(1)}%`,        change: winRateChange },
    { label: "Avg Return",     value: `${avgReturn.toFixed(1)}%`,       change: avgReturnChange },
    { label: "Trades / Month", value: String(tradesPerMonth),           change: tradesPerMonthChange },
  ];

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30 h-full")}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-bold text-alchmai-text-primary uppercase tracking-wide">
          Performance
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-2">
          {metrics.map((m, i) => {
            const up = m.change >= 0;
            const Icon = up ? TrendingUp : TrendingDown;
            return (
              <div key={i} className="flex items-center justify-between">
                <span className="text-xs text-alchmai-text-secondary">{m.label}</span>
                <div className="flex items-baseline gap-2">
                  <span className={`text-sm font-bold ${loading ? "text-alchmai-text-secondary" : "text-alchmai-text-primary"}`}>
                    {loading ? "—" : m.value}
                  </span>
                  {!loading && (
                    <span className={`flex items-center gap-0.5 text-xs font-semibold ${up ? "text-alchmai-success" : "text-alchmai-danger"}`}>
                      <Icon className="w-3 h-3" />
                      {up ? "+" : ""}{m.change.toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
