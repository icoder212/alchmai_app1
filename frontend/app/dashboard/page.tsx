"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api, TradingSignal } from "@/lib/api";
import { formatCurrency, formatPercent, formatDate } from "@/lib/utils";
import { SignalCard } from "@/components/dashboard/SignalCard";
import { AgentAnalysisCard } from "@/components/dashboard/AgentAnalysisCard";
import { SignalHistory } from "@/components/dashboard/SignalHistory";
import { TradingViewChart } from "@/components/dashboard/TradingViewChart";
import { useSignalUpdates } from "@/hooks/useSignalUpdates";

export default function DashboardPage() {
  const [instrument, setInstrument] = useState("");
  const [loading, setLoading] = useState(false);
  const [signal, setSignal] = useState<TradingSignal | null>(null);
  const [error, setError] = useState("");
  const { latestSignal } = useSignalUpdates();

  const handleGenerateSignal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instrument.trim()) return;

    setLoading(true);
    setError("");
    setSignal(null);

    try {
      const response = await api.generateSignal(instrument.trim());
      if (response.success && response.signal) {
        setSignal(response.signal);
      } else {
        setError(response.error || "Failed to generate signal");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error generating signal");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="container mx-auto max-w-7xl">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Main content - 3 columns */}
          <div className="lg:col-span-3 space-y-6">
            <div>
              <h1 className="text-3xl font-bold">Trading Signal Generator</h1>
              <p className="text-muted-foreground">
                Generate AI-powered trading signals for any instrument
              </p>
            </div>

            {/* Live signal notification */}
            {latestSignal && latestSignal.instrument !== signal?.instrument && (
              <Card className="border-blue-500 bg-blue-50 dark:bg-blue-950">
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-blue-600 dark:text-blue-300">
                      New signal generated: {latestSignal.instrument} - {latestSignal.signal}
                    </span>
                    <Button size="sm" variant="link" onClick={() => setSignal(latestSignal)}>
                      View
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

        <Card>
          <CardHeader>
            <CardTitle>Generate Signal</CardTitle>
            <CardDescription>
              Enter an instrument name or symbol (e.g., AAPL, Apple, EURUSD, Gold)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleGenerateSignal} className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Label htmlFor="instrument">Instrument</Label>
                  <Input
                    id="instrument"
                    placeholder="AAPL, Apple, EURUSD, Gold..."
                    value={instrument}
                    onChange={(e) => setInstrument(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="flex items-end">
                  <Button type="submit" disabled={loading || !instrument.trim()}>
                    {loading ? "Generating..." : "Generate Signal"}
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <div className="text-destructive">{error}</div>
            </CardContent>
          </Card>
        )}

        {signal && (
          <div className="space-y-6">
            <SignalCard signal={signal} />
            
            {/* TradingView Chart */}
            <TradingViewChart
              symbol={signal.instrument}
              entryPrice={signal.entry_price}
              stopLoss={signal.stop_loss}
              takeProfit={signal.take_profit}
            />
            
            <div className="grid md:grid-cols-2 gap-4">
              <AgentAnalysisCard
                title="Fundamental Analysis"
                analysis={signal.fundamental_analysis}
              />
              <AgentAnalysisCard
                title="Economic Analysis"
                analysis={signal.economic_analysis}
              />
              <AgentAnalysisCard
                title="Technical Analysis"
                analysis={signal.technical_analysis}
              />
              <AgentAnalysisCard
                title="Sentiment Analysis"
                analysis={signal.sentiment_analysis}
              />
            </div>
          </div>
        )}
          </div>

          {/* Sidebar - 1 column */}
          <div className="lg:col-span-1">
            <SignalHistory onSelectSignal={setSignal} />
          </div>
        </div>
      </div>
    </div>
  );
}
