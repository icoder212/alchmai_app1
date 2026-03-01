"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TradingSignal, api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { getCardClass } from "@/lib/alchmai-theme";
import { TrendingUp, TrendingDown, Clock } from "lucide-react";

interface SignalHistoryProps {
  onSelectSignal: (signal: TradingSignal) => void;
  /** Pass the freshly generated signal here — it appears instantly without a re-fetch */
  latestSignal?: TradingSignal | null;
}

function timeAgo(timestamp: string): string {
  const diff = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function SignalHistory({ onSelectSignal, latestSignal }: SignalHistoryProps) {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [loading, setLoading] = useState(true);

  // Initial fetch on mount
  useEffect(() => {
    api.getSignalHistory(20).then((result) => {
      if (result.success) setSignals(result.signals);
      setLoading(false);
    });
  }, []);

  // Prepend new signal to the list immediately — no re-fetch needed
  useEffect(() => {
    if (!latestSignal) return;
    setSignals((prev) => {
      // Guard against duplicates by timestamp + instrument
      const isDuplicate = prev.some(
        (s) => s.timestamp === latestSignal.timestamp && s.instrument === latestSignal.instrument
      );
      if (isDuplicate) return prev;
      return [latestSignal, ...prev].slice(0, 20);
    });
  }, [latestSignal]);

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader className="pb-2 pt-3 px-4">
        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-alchmai-purple" />
          <CardTitle className="text-xs font-bold text-alchmai-text-primary uppercase tracking-wider">
            Recent Signals
          </CardTitle>
          {signals.length > 0 && (
            <span className="ml-auto text-xs text-alchmai-text-secondary">
              {signals.length} signal{signals.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
      </CardHeader>

      <CardContent className="px-4 pb-3">
        {loading ? (
          /* Loading skeleton — grid */
          <div className="grid gap-3 pb-1 grid-cols-[repeat(auto-fill,minmax(11rem,1fr))]">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="animate-pulse h-[76px] rounded-xl bg-alchmai-darker/60 border border-alchmai-purple/10"
              />
            ))}
          </div>
        ) : signals.length === 0 ? (
          <p className="text-xs text-alchmai-text-secondary py-2">
            No signals yet — generate one below
          </p>
        ) : (
          /* Grid that fills the full width — cards expand to fill, minimum 11rem each */
          <div className="grid gap-3 pb-1 grid-cols-[repeat(auto-fill,minmax(11rem,1fr))]">
            {signals.map((sig, idx) => {
              const isBuy = sig.signal === "BUY";
              const Icon = isBuy ? TrendingUp : TrendingDown;
              return (
                <button
                  key={`${sig.instrument}-${sig.timestamp}-${idx}`}
                  onClick={() => onSelectSignal(sig)}
                  className={`p-3 rounded-xl border text-left transition-all hover:scale-[1.02] active:scale-[0.98] ${
                    isBuy
                      ? "border-alchmai-success/30 bg-alchmai-success/5 hover:border-alchmai-success/50 hover:bg-alchmai-success/10"
                      : "border-alchmai-danger/30 bg-alchmai-danger/5 hover:border-alchmai-danger/50 hover:bg-alchmai-danger/10"
                  }`}
                >
                  {/* Instrument + signal badge */}
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-bold text-alchmai-text-primary truncate max-w-[90px]">
                      {sig.instrument}
                    </span>
                    <span
                      className={`flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full flex-shrink-0 ${
                        isBuy
                          ? "bg-alchmai-success/20 text-alchmai-success"
                          : "bg-alchmai-danger/20 text-alchmai-danger"
                      }`}
                    >
                      <Icon className="w-2.5 h-2.5" />
                      {sig.signal}
                    </span>
                  </div>

                  {/* Entry price */}
                  <div className="text-xs text-alchmai-text-secondary mb-1.5">
                    Entry:{" "}
                    <span className="text-alchmai-text-primary font-semibold">
                      {formatCurrency(sig.entry_price)}
                    </span>
                  </div>

                  {/* Confidence + time ago */}
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-alchmai-purple font-semibold">
                      {sig.confidence.toFixed(1)}% conf
                    </span>
                    <span className="text-[10px] text-alchmai-text-secondary">
                      {timeAgo(sig.timestamp)}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
