"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api, TradingSignal } from "@/lib/api";
import { SignalCard } from "@/components/dashboard/SignalCard";
import { AgentAnalysisCard } from "@/components/dashboard/AgentAnalysisCard";
import { SignalHistory } from "@/components/dashboard/SignalHistory";
import { TradingViewChart } from "@/components/dashboard/TradingViewChart";
import { useSignalUpdates } from "@/hooks/useSignalUpdates";
import { AIConfidenceCard } from "@/components/dashboard/AIConfidenceCard";
import { AgentActivityIndicator } from "@/components/dashboard/AgentActivityIndicator";
import { LiveMarketIndicator } from "@/components/dashboard/LiveMarketIndicator";
import { AssetTickers } from "@/components/dashboard/AssetTickers";
import { PortfolioCard } from "@/components/dashboard/PortfolioCard";
import { ActiveSignalsCounter } from "@/components/dashboard/ActiveSignalsCounter";
import { PerformanceMetrics } from "@/components/dashboard/PerformanceMetrics";
import { getCardClass } from "@/lib/alchmai-theme";
import { Sparkles } from "lucide-react";

// Quick-access demo instruments shown as chips
const DEMO_INSTRUMENTS = ["AAPL", "EURUSD", "Gold", "BTC", "MSFT", "GOOGL"];

// Selectable signal timeframes
const TIMEFRAMES = [
  { value: "1m",  label: "1m"  },
  { value: "5m",  label: "5m"  },
  { value: "15m", label: "15m" },
  { value: "30m", label: "30m" },
  { value: "1h",  label: "1h"  },
  { value: "1D",  label: "1D"  },
];

export default function DashboardPage() {
  const [instrument, setInstrument] = useState("");
  const [timeframe, setTimeframe] = useState("15m");
  const [loading, setLoading] = useState(false);
  const [signal, setSignal] = useState<TradingSignal | null>(null);
  const [error, setError] = useState("");

  const [agentStatus, setAgentStatus] = useState([
    { name: "Fundamental", status: "idle" as const, progress: 0 },
    { name: "Economic",    status: "idle" as const, progress: 0 },
    { name: "Technical",   status: "idle" as const, progress: 0 },
    { name: "Sentiment",   status: "idle" as const, progress: 0 },
  ]);

  const [activeSignals, setActiveSignals] = useState({ total: 0, buy: 0, hold: 0, sell: 0 });
  const [performanceMetrics, setPerformanceMetrics] = useState({
    winRate: 0, winRateChange: 0,
    avgReturn: 0, avgReturnChange: 0,
    tradesPerMonth: 0, tradesPerMonthChange: 0,
  });
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 0, changePercent: 0,
    changeType: "positive" as "positive" | "negative",
    hasPortfolio: false,
  });

  const { latestSignal } = useSignalUpdates();

  useEffect(() => {
    fetchActiveSignals();
    fetchPerformanceMetrics();
    fetchPortfolioData();
  }, []);

  const fetchActiveSignals = async () => {
    try {
      const data = await api.getActiveSignals();
      setActiveSignals({ total: data.total, buy: data.buy, hold: data.hold, sell: data.sell });
    } catch {}
  };

  const fetchPerformanceMetrics = async () => {
    try {
      const data = await api.getPerformanceMetrics();
      setPerformanceMetrics({
        winRate: data.win_rate,
        winRateChange: data.win_rate_change,
        avgReturn: data.avg_return,
        avgReturnChange: data.avg_return_change,
        tradesPerMonth: data.trades_per_month,
        tradesPerMonthChange: data.trades_per_month_change,
      });
    } catch {}
  };

  const fetchPortfolioData = async () => {
    try {
      const data = await api.getPortfolioSummary();
      setPortfolioData({
        totalValue: data.total_value,
        changePercent: data.change_percent,
        changeType: data.change_type,
        hasPortfolio: data.has_portfolio,
      });
    } catch {}
  };

  const runGenerate = async (sym: string) => {
    if (!sym.trim()) return;
    setLoading(true);
    setError("");
    setSignal(null);

    setAgentStatus([
      { name: "Fundamental", status: "analyzing", progress: 0 },
      { name: "Economic",    status: "analyzing", progress: 0 },
      { name: "Technical",   status: "analyzing", progress: 0 },
      { name: "Sentiment",   status: "analyzing", progress: 0 },
    ]);

    // Animate progress bars at different speeds per agent for realism
    const speeds = [18, 14, 22, 16];
    const timers: ReturnType<typeof setInterval>[] = [];
    [0, 1, 2, 3].forEach((idx) => {
      const id = setInterval(() => {
        setAgentStatus((prev) =>
          prev.map((a, i) =>
            i === idx && a.status === "analyzing"
              ? { ...a, progress: Math.min(a.progress + speeds[idx] * Math.random(), 92) }
              : a
          )
        );
      }, 600);
      timers.push(id);
    });

    try {
      const response = await api.generateSignal(sym.trim(), timeframe);
      timers.forEach(clearInterval);

      if (response.success && response.signal) {
        setSignal(response.signal);
        setAgentStatus([
          { name: "Fundamental", status: "complete", progress: 100 },
          { name: "Economic",    status: "complete", progress: 100 },
          { name: "Technical",   status: "complete", progress: 100 },
          { name: "Sentiment",   status: "complete", progress: 100 },
        ]);
        fetchActiveSignals();
      } else {
        setError(response.error || "Failed to generate signal");
        setAgentStatus((prev) =>
          prev.map((a) => ({ ...a, status: "error" as const, progress: 0 }))
        );
      }
    } catch (err: any) {
      timers.forEach(clearInterval);
      setError(err.response?.data?.detail || "Error generating signal");
      setAgentStatus((prev) =>
        prev.map((a) => ({ ...a, status: "error" as const, progress: 0 }))
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSignal = (e: React.FormEvent) => {
    e.preventDefault();
    runGenerate(instrument);
  };

  const handleTickerClick = (sym: string) => setInstrument(sym);

  const handleDemoChip = (sym: string) => {
    setInstrument(sym);
    runGenerate(sym);
  };

  return (
    <div className="min-h-screen bg-alchmai-dark p-4 md:p-6">
      <div className="container mx-auto max-w-7xl">

        {/* ── Page Header ── */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-alchmai-text-primary mb-0.5">
              AI Trading Signal Generator
            </h1>
            <p className="text-alchmai-text-secondary text-sm">
              4 specialised agents · Real market data · Instant validated signals
            </p>
          </div>
          <LiveMarketIndicator />
        </div>

        {/* ── Asset Tickers ── */}
        <div className="mb-4">
          <AssetTickers onTickerClick={handleTickerClick} />
        </div>

        {/* ── Top Metrics Row: 3 stat cards + Performance strip ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          {signal ? (
            <div className="animate-badge-pop h-full">
              <AIConfidenceCard confidence={signal.confidence} />
            </div>
          ) : (
            <Card className={getCardClass(true, "border-alchmai-purple/30 h-full")}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-bold text-alchmai-text-primary">
                  AI Confidence Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-2">
                  <div className="text-3xl font-bold text-alchmai-text-secondary mb-1">--</div>
                  <div className="text-xs text-alchmai-text-secondary">
                    Generate a signal to see score
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          <PortfolioCard
            totalValue={portfolioData.totalValue}
            changePercent={portfolioData.changePercent}
            changeType={portfolioData.changeType}
            hasPortfolio={portfolioData.hasPortfolio}
          />
          <ActiveSignalsCounter
            total={activeSignals.total}
            buy={activeSignals.buy}
            hold={activeSignals.hold}
            sell={activeSignals.sell}
          />
          {/* Performance strip replaces the old "Quick Stats" card */}
          <PerformanceMetrics {...performanceMetrics} />
        </div>

        {/* ── Main Content + Sidebar ── */}
        <div className="grid lg:grid-cols-4 gap-4 items-start">
          <div className="lg:col-span-3 space-y-4">

            {/* WebSocket live-signal notification */}
            {latestSignal && latestSignal.instrument !== signal?.instrument && (
              <Card className={getCardClass(true, "border-alchmai-blue bg-alchmai-blue/10")}>
                <CardContent className="py-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-alchmai-blue text-sm">
                      New signal: <strong>{latestSignal.instrument}</strong> — {latestSignal.signal}
                    </span>
                    <Button
                      size="sm"
                      variant="link"
                      onClick={() => setSignal(latestSignal)}
                      className="text-alchmai-blue p-0"
                    >
                      View
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* ── Signal Generation Form ── */}
            <Card className={getCardClass(true, "border-alchmai-purple/30")} id="signal-form">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-bold text-alchmai-text-primary flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-alchmai-purple" />
                  Generate a Signal
                </CardTitle>
                <CardDescription className="text-alchmai-text-secondary">
                  Enter any stock, forex pair, or commodity — or click a chip below
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleGenerateSignal} className="space-y-3">
                  <div className="flex gap-3">
                    <div className="flex-1">
                      <Label htmlFor="instrument" className="text-alchmai-text-primary text-sm mb-1 block">
                        Instrument
                      </Label>
                      <Input
                        id="instrument"
                        placeholder="AAPL · Apple · EURUSD · Gold · BTC…"
                        value={instrument}
                        onChange={(e) => setInstrument(e.target.value)}
                        disabled={loading}
                        className="bg-alchmai-darker border-alchmai-purple/30 text-alchmai-text-primary placeholder:text-alchmai-text-secondary/40"
                      />
                    </div>
                    <div className="flex items-end">
                      <Button
                        type="submit"
                        disabled={loading || !instrument.trim()}
                        className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white glow-purple"
                      >
                        {loading ? "Analysing…" : "Generate"}
                      </Button>
                    </div>
                  </div>

                  {/* Timeframe selector */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-alchmai-text-secondary font-medium">Timeframe:</span>
                    {TIMEFRAMES.map((tf) => (
                      <button
                        key={tf.value}
                        type="button"
                        onClick={() => setTimeframe(tf.value)}
                        disabled={loading}
                        className={`px-3 py-1 text-xs rounded-full border transition-all disabled:opacity-40 ${
                          timeframe === tf.value
                            ? "bg-alchmai-purple/20 border-alchmai-purple text-alchmai-purple font-semibold"
                            : "border-alchmai-purple/30 text-alchmai-text-secondary hover:text-alchmai-text-primary hover:border-alchmai-purple/60"
                        }`}
                      >
                        {tf.label}
                      </button>
                    ))}
                  </div>

                  {/* Quick demo chips */}
                  <div className="flex flex-wrap gap-2">
                    {DEMO_INSTRUMENTS.map((sym) => (
                      <button
                        key={sym}
                        type="button"
                        onClick={() => handleDemoChip(sym)}
                        disabled={loading}
                        className="px-3 py-1 text-xs rounded-full border border-alchmai-purple/30 text-alchmai-text-secondary hover:text-alchmai-text-primary hover:border-alchmai-purple/60 hover:bg-alchmai-purple/10 transition-all disabled:opacity-40"
                      >
                        {sym}
                      </button>
                    ))}
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* ── Agent Activity ── */}
            {(loading || agentStatus.some((a) => a.status !== "idle")) && (
              <AgentActivityIndicator agents={agentStatus} show />
            )}

            {/* ── Error ── */}
            {error && (
              <Card className={getCardClass(false, "border-alchmai-danger/50")}>
                <CardContent className="py-4">
                  <p className="text-alchmai-danger text-sm">{error}</p>
                </CardContent>
              </Card>
            )}

            {/* ── Signal Result ── */}
            {signal && (
              <div className="space-y-4">
                {/* SignalCard slides in */}
                <div className="animate-fade-slide-up">
                  <SignalCard signal={signal} />
                </div>

                {/* Chart slides in slightly after */}
                <div className="animate-fade-slide-up-1">
                  <TradingViewChart
                    symbol={signal.instrument}
                    entryPrice={signal.entry_price}
                    stopLoss={signal.stop_loss}
                    takeProfit={signal.take_profit}
                    signal={signal.signal as "BUY" | "SELL"}
                    timeframe={signal.timeframe || timeframe}
                    assetClass={signal.asset_class || "stock"}
                  />
                </div>

                {/* Agent cards staggered */}
                <div className="animate-fade-slide-up-2">
                  <h2 className="text-sm font-semibold text-alchmai-text-secondary uppercase tracking-wider mb-3">
                    What each agent found
                  </h2>
                  <div className="grid md:grid-cols-2 gap-3 auto-rows-fr">
                    <div className="animate-fade-slide-up-1 h-full">
                      <AgentAnalysisCard title="Fundamental Analysis" analysis={signal.fundamental_analysis} />
                    </div>
                    <div className="animate-fade-slide-up-2 h-full">
                      <AgentAnalysisCard title="Economic Analysis" analysis={signal.economic_analysis} />
                    </div>
                    <div className="animate-fade-slide-up-3 h-full">
                      <AgentAnalysisCard title="Technical Analysis" analysis={signal.technical_analysis} />
                    </div>
                    <div className="animate-fade-slide-up-4 h-full">
                      <AgentAnalysisCard title="Sentiment Analysis" analysis={signal.sentiment_analysis} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ── Sidebar ── */}
          <div className="lg:col-span-1">
            <div className="sticky top-4">
              <SignalHistory onSelectSignal={setSignal} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
