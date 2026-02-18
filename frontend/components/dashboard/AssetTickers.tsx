"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { getCardClass } from "@/lib/alchmai-theme";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { api, AssetTicker } from "@/lib/api";
import { Loader2 } from "lucide-react";

interface AssetTickersProps {
  onTickerClick?: (symbol: string) => void;
}

export function AssetTickers({ onTickerClick }: AssetTickersProps) {
  const [tickers, setTickers] = useState<AssetTicker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTickers();
    // Poll every 30 seconds for updates
    const interval = setInterval(fetchTickers, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchTickers = async () => {
    try {
      const data = await api.getMarketTickers();
      setTickers(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch tickers:', error);
      // Fallback to empty array on error
      setTickers([]);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className={getCardClass(true, "border-alchmai-purple/30")}>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-5 h-5 animate-spin text-alchmai-purple" />
            <span className="text-alchmai-text-secondary">Loading market data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardContent className="pt-6">
        <div className="flex space-x-4 overflow-x-auto pb-2 scrollbar-hide">
          {tickers.map((ticker, idx) => (
            <div
              key={idx}
              onClick={() => onTickerClick?.(ticker.symbol)}
              className="flex-shrink-0 p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50 hover:bg-alchmai-darker hover:border-alchmai-purple/40 cursor-pointer transition-all min-w-[140px]"
            >
              <div className="text-sm font-semibold text-alchmai-text-primary mb-1">
                {ticker.symbol}
              </div>
              <div className="text-lg font-bold text-alchmai-text-primary mb-1">
                {formatCurrency(ticker.price)}
              </div>
              <div className={`text-sm font-semibold ${
                ticker.change_type === 'positive' 
                  ? 'text-alchmai-success' 
                  : 'text-alchmai-danger'
              }`}>
                {ticker.change_type === 'positive' ? '+' : ''}{formatPercent(Math.abs(ticker.change))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
