"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TradingSignal, api } from "@/lib/api";
import { formatDate, formatCurrency } from "@/lib/utils";

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
    <Card>
      <CardHeader>
        <CardTitle>Recent Signals</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-muted-foreground">Loading history...</p>
        ) : signals.length === 0 ? (
          <p className="text-muted-foreground">No signals generated yet</p>
        ) : (
          <div className="space-y-2">
            {signals.map((sig, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-accent transition-colors"
                onClick={() => onSelectSignal(sig)}
              >
                <div>
                  <div className="font-semibold">{sig.instrument}</div>
                  <div className="text-sm text-muted-foreground">
                    {formatDate(sig.timestamp)}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-bold ${sig.signal === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                    {sig.signal}
                  </div>
                  <div className="text-sm">{formatCurrency(sig.entry_price)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
