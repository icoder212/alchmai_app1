"use client";

import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, ColorType, LineStyle } from "lightweight-charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getCardClass } from "@/lib/alchmai-theme";
import { Sparkles, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

interface TradingViewChartProps {
  symbol: string;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  signal?: "BUY" | "SELL";
  /** Timeframe the signal was generated on — controls candle interval */
  timeframe?: string;
  /** Asset class — needed for correct yfinance symbol conversion on backend */
  assetClass?: string;
}

// How much history to show based on the selected view window
type ViewWindow = "1D" | "1W" | "1M" | "3M";

export function TradingViewChart({
  symbol,
  entryPrice,
  stopLoss,
  takeProfit,
  signal = "BUY",
  timeframe = "15m",
  assetClass = "stock",
}: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [viewWindow, setViewWindow] = useState<ViewWindow>("1D");
  const [loadingChart, setLoadingChart] = useState(false);
  const [chartError, setChartError] = useState("");

  // Timeframe → human-readable label for the chart header
  const TF_LABEL: Record<string, string> = {
    "1m": "1-Minute", "5m": "5-Minute", "15m": "15-Minute",
    "30m": "30-Minute", "1h": "1-Hour", "1D": "Daily",
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Destroy previous chart instance before creating a new one
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { type: ColorType.Solid, color: "#0F0F23" },
        textColor: "#FFFFFF",
      },
      grid: {
        vertLines: { color: "rgba(147, 51, 234, 0.1)" },
        horzLines: { color: "rgba(147, 51, 234, 0.1)" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: "rgba(147, 51, 234, 0.3)",
      },
      rightPriceScale: {
        borderColor: "rgba(147, 51, 234, 0.3)",
      },
    });

    chartRef.current = chart;

    // Candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#10B981",
      downColor: "#EF4444",
      borderVisible: false,
      wickUpColor: "#10B981",
      wickDownColor: "#EF4444",
    });

    // Invisible line series used only for price level annotations
    const lineSeries = chart.addLineSeries({
      color: "rgba(0,0,0,0)",
      lineWidth: 1,
    });

    // Entry price line
    lineSeries.createPriceLine({
      price: entryPrice,
      color: "#3B82F6",
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: true,
      title: "Entry",
    });

    // Stop loss line
    lineSeries.createPriceLine({
      price: stopLoss,
      color: "#EF4444",
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: true,
      title: "Stop Loss",
    });

    // Take profit line
    lineSeries.createPriceLine({
      price: takeProfit,
      color: "#10B981",
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: true,
      title: "Take Profit",
    });

    // Signal annotation at entry price
    lineSeries.createPriceLine({
      price: entryPrice,
      color: signal === "BUY" ? "#10B981" : "#EF4444",
      lineWidth: 1,
      axisLabelVisible: true,
      title: signal === "BUY" ? "BUY ↑" : "SELL ↓",
    });

    // Fetch real OHLCV data from backend
    setLoadingChart(true);
    setChartError("");

    api.getChartData(symbol, timeframe, viewWindow, assetClass)
      .then((candles) => {
        if (!candles || candles.length === 0) {
          setChartError("No chart data available for this symbol.");
          return;
        }
        // lightweight-charts requires data sorted ascending by time
        const sorted = [...candles].sort((a, b) => a.time - b.time);
        candlestickSeries.setData(sorted as any);
        // Place the invisible line series at the same last timestamp so price lines render
        lineSeries.setData([{ time: sorted[sorted.length - 1].time as any, value: entryPrice }]);
        chart.timeScale().fitContent();
      })
      .catch(() => setChartError("Failed to load chart data."))
      .finally(() => setLoadingChart(false));

    // Responsive resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [symbol, entryPrice, stopLoss, takeProfit, signal, timeframe, viewWindow, assetClass]);

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader>
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <CardTitle className="text-xl font-bold text-alchmai-text-primary">
              {symbol} - Trading Levels
            </CardTitle>
            <Sparkles className="w-5 h-5 text-alchmai-purple" />
            <span className="text-xs text-alchmai-text-secondary">
              {TF_LABEL[timeframe] ?? timeframe} candles · AI Powered
            </span>
          </div>

          {/* View window buttons — control how much history is shown, NOT the candle interval */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-alchmai-text-secondary mr-1">View:</span>
            {(["1D", "1W", "1M", "3M"] as ViewWindow[]).map((w) => (
              <Button
                key={w}
                variant={viewWindow === w ? "default" : "outline"}
                size="sm"
                onClick={() => setViewWindow(w)}
                className={
                  viewWindow === w
                    ? "bg-alchmai-purple hover:bg-alchmai-purple/90 text-white"
                    : "border-alchmai-purple/30 text-alchmai-text-secondary hover:text-alchmai-text-primary"
                }
              >
                {w}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Loading / error state overlay */}
        {loadingChart && (
          <div className="flex items-center justify-center h-12 mb-2 text-alchmai-text-secondary gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-alchmai-purple" />
            <span className="text-sm">Loading {TF_LABEL[timeframe] ?? timeframe} candles…</span>
          </div>
        )}
        {chartError && !loadingChart && (
          <div className="text-sm text-alchmai-danger mb-2 px-1">{chartError}</div>
        )}

        <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />

        {/* Legend */}
        <div className="mt-4 p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50">
          <div className="text-sm font-semibold text-alchmai-text-primary mb-2">Chart Elements</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-alchmai-blue"></div>
              <span className="text-alchmai-text-secondary">Entry Price</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-alchmai-danger"></div>
              <span className="text-alchmai-text-secondary">Stop Loss</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-alchmai-success"></div>
              <span className="text-alchmai-text-secondary">Take Profit</span>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-alchmai-purple" />
              <span className="text-alchmai-text-secondary">AI Signals</span>
            </div>
          </div>
        </div>

        {/* Price summary */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div className="p-3 rounded-lg border border-alchmai-blue/30 bg-alchmai-blue/10">
            <div className="text-xs text-alchmai-text-secondary mb-1">Entry</div>
            <div className="text-lg font-bold text-alchmai-blue">${entryPrice.toFixed(2)}</div>
          </div>
          <div className="p-3 rounded-lg border border-alchmai-danger/30 bg-alchmai-danger/10">
            <div className="text-xs text-alchmai-text-secondary mb-1">Stop Loss</div>
            <div className="text-lg font-bold text-alchmai-danger">${stopLoss.toFixed(2)}</div>
          </div>
          <div className="p-3 rounded-lg border border-alchmai-success/30 bg-alchmai-success/10">
            <div className="text-xs text-alchmai-text-secondary mb-1">Take Profit</div>
            <div className="text-lg font-bold text-alchmai-success">${takeProfit.toFixed(2)}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
