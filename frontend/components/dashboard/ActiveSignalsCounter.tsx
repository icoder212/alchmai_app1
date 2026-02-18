"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCardClass } from "@/lib/alchmai-theme";

interface ActiveSignalsCounterProps {
  total: number;
  buy: number;
  hold: number;
  sell: number;
  loading?: boolean;
}

export function ActiveSignalsCounter({
  total,
  buy,
  hold,
  sell,
  loading = false,
}: ActiveSignalsCounterProps) {
  if (loading) {
    return (
      <Card className={getCardClass(true, "border-alchmai-purple/30 h-full")}>
        <CardContent className="pt-6">
          <div className="animate-pulse space-y-2">
            <div className="h-6 bg-alchmai-darker rounded w-1/2"></div>
            <div className="h-4 bg-alchmai-darker rounded w-3/4"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-bold text-alchmai-text-primary uppercase tracking-wide">
          Active Signals
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="text-4xl font-bold text-alchmai-text-primary">
            {total}
          </div>
          <div className="space-y-1.5 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-alchmai-text-secondary">Buy Signals:</span>
              <span className="font-semibold text-alchmai-success">{buy}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-alchmai-text-secondary">Hold Signals:</span>
              <span className="font-semibold text-yellow-500">{hold}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-alchmai-text-secondary">Sell Signals:</span>
              <span className="font-semibold text-alchmai-danger">{sell}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
