"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TradingSignal } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Sparkles, TrendingUp, TrendingDown, Brain, ArrowDown } from "lucide-react";

interface AgentWeights {
  fundamental: number;
  economic: number;
  technical: number;
  sentiment: number;
}

interface ExplainDecisionModalProps {
  signal: TradingSignal;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Agent weights as percentages (0-100) fetched from backend. Falls back to config defaults. */
  agentWeights?: AgentWeights;
  /** Model used to generate the AI explanation */
  model?: string;
}

/** Convert a model ID to a short human-readable label */
function modelLabel(model?: string): string {
  if (!model) return "AI Analysis";
  const map: Record<string, string> = {
    "gpt-4o":           "GPT-4o Analysis",
    "gpt-4o-mini":      "GPT-4o Mini Analysis",
    "gpt-4-turbo":      "GPT-4 Turbo Analysis",
    "gpt-3.5-turbo":    "GPT-3.5 Turbo Analysis",
    "claude-opus-4-6":  "Claude Opus 4.6 Analysis",
    "claude-sonnet-4-6":"Claude Sonnet 4.6 Analysis",
    "claude-haiku-4-5": "Claude Haiku 4.5 Analysis",
  };
  return map[model] ?? `${model} Analysis`;
}

export function ExplainDecisionModal({
  signal,
  open,
  onOpenChange,
  agentWeights,
  model,
}: ExplainDecisionModalProps) {
  // Use live weights from backend (as fractions). Fallback = correct config.py defaults.
  const weights = agentWeights
    ? {
        technical:   agentWeights.technical   / 100,
        sentiment:   agentWeights.sentiment   / 100,
        fundamental: agentWeights.fundamental / 100,
        economic:    agentWeights.economic    / 100,
      }
    : { technical: 0.55, sentiment: 0.25, fundamental: 0.10, economic: 0.10 };

  const agents = [
    {
      name: "Fundamental Analysis",
      analysis: signal.fundamental_analysis,
      description: "Company financials, P/E ratios, revenue growth, earnings & margins.",
      weight: weights.fundamental,
    },
    {
      name: "Economic Analysis",
      analysis: signal.economic_analysis,
      description: "Macroeconomic indicators: GDP, inflation, unemployment, Fed rate.",
      weight: weights.economic,
    },
    {
      name: "Technical Analysis",
      analysis: signal.technical_analysis,
      description: "15-minute chart analysis: RSI, MACD, SMA-20, Bollinger Bands.",
      weight: weights.technical,
    },
    {
      name: "Sentiment Analysis",
      analysis: signal.sentiment_analysis,
      description: "News headlines scored by FinBERT financial AI model.",
      weight: weights.sentiment,
    },
  ];

  const isBuy = signal.signal === "BUY";
  const SignalIcon = isBuy ? TrendingUp : TrendingDown;
  const signalColor = isBuy ? "text-alchmai-success" : "text-alchmai-danger";
  const signalBg = isBuy ? "bg-alchmai-success/10 border-alchmai-success/30" : "bg-alchmai-danger/10 border-alchmai-danger/30";

  const calculateWeightedScore = () => {
    return (
      signal.technical_analysis.score * weights.technical +
      signal.sentiment_analysis.score * weights.sentiment +
      signal.fundamental_analysis.score * weights.fundamental +
      signal.economic_analysis.score * weights.economic
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-alchmai-dark border-alchmai-purple/30">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-alchmai-purple/20 border border-alchmai-purple/40 flex items-center justify-center">
              <Brain className="w-5 h-5 text-alchmai-purple" />
            </div>
            <div>
              <DialogTitle className="text-2xl font-bold text-alchmai-text-primary">
                How Did AI Make This Decision?
              </DialogTitle>
              <DialogDescription className="text-alchmai-text-secondary">
                Full AI reasoning for {signal.instrument} · {signal.signal} signal
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-2">

          {/* ── AI Narrative — the WOW section ── */}
          {signal.ai_explanation && (
            <div className="rounded-xl border border-alchmai-purple/40 bg-alchmai-purple/5 p-5">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-alchmai-purple" />
                <span className="text-xs font-semibold text-alchmai-purple uppercase tracking-wider">
                  {modelLabel(model)}
                </span>
              </div>
              <p className="text-base text-alchmai-text-primary leading-relaxed font-medium">
                {signal.ai_explanation}
              </p>
            </div>
          )}

          {/* ── Signal badge + price points ── */}
          <div className={`rounded-xl border p-4 ${signalBg}`}>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <SignalIcon className={`w-6 h-6 ${signalColor}`} />
                <div>
                  <div className={`text-2xl font-bold ${signalColor}`}>{signal.signal}</div>
                  <div className="text-xs text-alchmai-text-secondary">{signal.instrument} · Confidence {signal.confidence.toFixed(1)}%</div>
                </div>
              </div>
              <div className="flex gap-6 text-sm">
                <div>
                  <div className="text-xs text-alchmai-text-secondary mb-0.5">Entry</div>
                  <div className="font-bold text-alchmai-text-primary">${signal.entry_price.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-xs text-alchmai-text-secondary mb-0.5">Stop Loss</div>
                  <div className="font-bold text-alchmai-danger">${signal.stop_loss.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-xs text-alchmai-text-secondary mb-0.5">Take Profit</div>
                  <div className="font-bold text-alchmai-success">${signal.take_profit.toFixed(2)}</div>
                </div>
              </div>
            </div>
          </div>

          {/* ── What each agent found ── */}
          <div>
            <h3 className="text-sm font-semibold text-alchmai-text-secondary uppercase tracking-wider mb-3">
              What Each Agent Found
            </h3>
            <div className="grid sm:grid-cols-2 gap-3">
              {agents.map((agent, idx) => {
                const rec = agent.analysis.recommendation;
                const recColor =
                  rec === "BUY"
                    ? "text-alchmai-success"
                    : rec === "SELL"
                    ? "text-alchmai-danger"
                    : "text-alchmai-text-secondary";
                const recBg =
                  rec === "BUY"
                    ? "bg-alchmai-success/10 border-alchmai-success/30"
                    : rec === "SELL"
                    ? "bg-alchmai-danger/10 border-alchmai-danger/30"
                    : "bg-alchmai-text-secondary/5 border-alchmai-text-secondary/20";

                return (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-alchmai-purple/20 bg-alchmai-darker/50 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-alchmai-text-primary text-sm">
                        {agent.name}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-alchmai-purple">
                          {(agent.weight * 100).toFixed(0)}% weight
                        </span>
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${recColor} ${recBg}`}>
                          {rec}
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-alchmai-text-secondary">{agent.description}</div>
                    <div className="text-xs text-alchmai-text-secondary leading-relaxed border-t border-alchmai-purple/10 pt-2">
                      {agent.analysis.reasoning}
                    </div>
                    <div className="flex gap-4 text-xs text-alchmai-text-secondary/70">
                      <span>Score: <span className="text-alchmai-text-primary font-semibold">{agent.analysis.score.toFixed(1)}/100</span></span>
                      <span>Confidence: <span className="text-alchmai-text-primary font-semibold">{agent.analysis.confidence.toFixed(1)}%</span></span>
                    </div>
                    {/* mini score bar */}
                    <div className="w-full bg-alchmai-darker rounded-full h-1">
                      <div
                        className={`h-1 rounded-full transition-all ${
                          rec === "BUY" ? "bg-alchmai-success" : rec === "SELL" ? "bg-alchmai-danger" : "bg-alchmai-text-secondary"
                        }`}
                        style={{ width: `${Math.min(agent.analysis.score, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── Weighted Score Breakdown ── */}
          <div>
            <h3 className="text-sm font-semibold text-alchmai-text-secondary uppercase tracking-wider mb-3">
              How the Score Was Calculated
            </h3>
            <div className="rounded-xl border border-alchmai-purple/20 bg-alchmai-darker/50 p-4 space-y-2 text-sm">
              {[
                { label: "Technical Analysis",   score: signal.technical_analysis.score,   weight: weights.technical   },
                { label: "Sentiment Analysis",   score: signal.sentiment_analysis.score,   weight: weights.sentiment   },
                { label: "Fundamental Analysis", score: signal.fundamental_analysis.score, weight: weights.fundamental },
                { label: "Economic Analysis",    score: signal.economic_analysis.score,    weight: weights.economic    },
              ].map((row, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-alchmai-text-secondary">{row.label}</span>
                  <span className="text-alchmai-text-primary font-semibold font-mono">
                    {row.score.toFixed(1)} × {(row.weight * 100).toFixed(0)}% ={" "}
                    <span className="text-alchmai-purple">{(row.score * row.weight).toFixed(1)}</span>
                  </span>
                </div>
              ))}
              {/* Weighted Total row */}
              <div className="mt-3 pt-3 border-t border-alchmai-purple/20 flex justify-between font-bold">
                <span className="text-alchmai-text-primary">Weighted Total</span>
                <span className="text-alchmai-purple text-lg">{calculateWeightedScore().toFixed(1)} / 100</span>
              </div>
              {/* Confidence derivation row — shows the formula that converts weighted
                  score to signal conviction (symmetric around 50).
                  For BUY  (score > 50): confidence = score           → numbers match.
                  For SELL (score < 50): confidence = 100 − score     → symmetric. */}
              <div className="flex items-center justify-between text-xs text-alchmai-text-secondary/80 pt-1.5">
                <span>
                  Signal Conviction = 50 + |{calculateWeightedScore().toFixed(1)} − 50|
                </span>
                <span className={`font-semibold ${isBuy ? "text-alchmai-success" : "text-alchmai-danger"}`}>
                  = {signal.confidence.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* ── Decision Journey (compact vertical flow) ── */}
          <div>
            <h3 className="text-sm font-semibold text-alchmai-text-secondary uppercase tracking-wider mb-3">
              Decision Flow
            </h3>
            <div className="rounded-xl border border-alchmai-purple/20 bg-alchmai-darker/50 p-4">
              <div className="flex flex-col items-start gap-1">
                {(() => {
                  const ws = calculateWeightedScore();
                  const dirLabel = ws > 50 ? "bullish" : ws < 50 ? "bearish" : "neutral";
                  const validationPassed = signal.confidence >= 50;
                  return [
                  { step: "1", label: "Input", value: signal.instrument, color: "border-alchmai-purple text-alchmai-purple bg-alchmai-purple/10" },
                  { step: "2", label: "4 Agents (Parallel)", value: `F:${signal.fundamental_analysis.recommendation} · E:${signal.economic_analysis.recommendation} · T:${signal.technical_analysis.recommendation} · S:${signal.sentiment_analysis.recommendation}`, color: "border-alchmai-blue text-alchmai-blue bg-alchmai-blue/10" },
                  { step: "3", label: "Directional Score (50 = neutral)", value: `${ws.toFixed(1)} / 100 (${dirLabel})`, color: "border-alchmai-purple text-alchmai-purple bg-alchmai-purple/10" },
                  { step: "4", label: "Final Signal", value: `${signal.signal} · ${signal.confidence.toFixed(1)}% conviction`, color: `${signal.signal === "BUY" ? "border-alchmai-success text-alchmai-success bg-alchmai-success/10" : "border-alchmai-danger text-alchmai-danger bg-alchmai-danger/10"}` },
                  { step: "5", label: "Safety Validation", value: validationPassed ? "✓ All checks passed" : `⚠ Confidence ${signal.confidence.toFixed(1)}% (min 50%)`, color: validationPassed ? "border-alchmai-success text-alchmai-success bg-alchmai-success/10" : "border-alchmai-danger text-alchmai-danger bg-alchmai-danger/10" },
                  ];
                })().map((item, i, arr) => (
                  <div key={i} className="w-full">
                    <div className="flex items-center gap-3">
                      <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-xs font-bold flex-shrink-0 ${item.color}`}>
                        {item.step}
                      </div>
                      <div className="flex-1 flex items-center justify-between">
                        <span className="text-xs text-alchmai-text-secondary">{item.label}</span>
                        <span className="text-xs font-semibold text-alchmai-text-primary">{item.value}</span>
                      </div>
                    </div>
                    {i < arr.length - 1 && (
                      <div className="ml-3 w-1 h-3 flex items-center justify-center">
                        <ArrowDown className="w-3 h-3 text-alchmai-purple/40" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        <div className="mt-6 flex justify-end">
          <Button
            onClick={() => onOpenChange(false)}
            className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white"
          >
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
