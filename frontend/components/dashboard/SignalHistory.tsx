"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TradingSignal, api } from "@/lib/api";
import { formatDate, formatCurrency } from "@/lib/utils";
import { getCardClass } from "@/lib/alchmai-theme";

interface SignalHistoryProps {
  onSelectSignal: (signal: TradingSignal) => void;
}

export function SignalHistory({ onSelectSignal }: SignalHistoryProps) {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    const result = await api.getSignalHistory(20);
    if (result.success) {
      setSignals(result.signals);
    }
    setLoading(false);
  };

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-bold text-alchmai-text-primary uppercase tracking-wide">
          Recent Signals
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse flex justify-between p-3 rounded-lg bg-alchmai-darker/50">
                <div className="space-y-1.5">
                  <div className="h-3 w-12 bg-alchmai-darker rounded" />
                  <div className="h-2 w-24 bg-alchmai-darker rounded" />
                </div>
                <div className="space-y-1.5 items-end flex flex-col">
                  <div className="h-3 w-8 bg-alchmai-darker rounded" />
                  <div className="h-2 w-14 bg-alchmai-darker rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : signals.length === 0 ? (
          <p className="text-sm text-alchmai-text-secondary">No signals generated yet</p>
        ) : (
          <div className="space-y-2">
            {signals.map((sig, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 border border-alchmai-purple/20 rounded-lg cursor-pointer hover:bg-alchmai-darker hover:border-alchmai-purple/40 transition-all"
                onClick={() => onSelectSignal(sig)}
              >
                <div>
                  <div className="font-semibold text-sm text-alchmai-text-primary">{sig.instrument}</div>
                  <div className="text-xs text-alchmai-text-secondary mt-0.5">
                    {formatDate(sig.timestamp)}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-bold ${sig.signal === 'BUY' ? 'text-alchmai-success' : 'text-alchmai-danger'}`}>
                    {sig.signal}
                  </div>
                  <div className="text-xs text-alchmai-text-secondary mt-0.5">{formatCurrency(sig.entry_price)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
