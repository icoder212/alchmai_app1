"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TradingSignal } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getCardClass } from "@/lib/alchmai-theme";
import { TrendingUp, TrendingDown, HelpCircle, Sparkles } from "lucide-react";
import { ExplainDecisionModal } from "./ExplainDecisionModal";

interface SignalCardProps {
  signal: TradingSignal;
}

/** Fallback summary used only when GPT-4o explanation is unavailable */
function buildFallbackSummary(signal: TradingSignal): string {
  const agents = [
    signal.fundamental_analysis,
    signal.economic_analysis,
    signal.technical_analysis,
    signal.sentiment_analysis,
  ];
  const agreeCount = agents.filter(
    (a) => a.recommendation === signal.signal
  ).length;
  const direction = signal.signal === "BUY" ? "bullish" : "bearish";
  const agreeText =
    agreeCount === 4
      ? "All 4 agents agree"
      : agreeCount === 3
      ? "3 of 4 agents agree"
      : agreeCount === 2
      ? "2 of 4 agents agree"
      : "1 of 4 agents agree";

  const techReason = signal.technical_analysis.reasoning
    .split("|")[0]
    ?.trim()
    .toLowerCase();

  return `${agreeText} on a ${direction} outlook. ${
    techReason ? `Technical analysis shows ${techReason}.` : ""
  } Confidence: ${signal.confidence.toFixed(1)}%.`;
}

export function SignalCard({ signal }: SignalCardProps) {
  const [showExplainModal, setShowExplainModal] = useState(false);

  const isBuy = signal.signal === "BUY";
  const SignalIcon = isBuy ? TrendingUp : TrendingDown;

  // Risk / reward
  const risk = isBuy
    ? signal.entry_price - signal.stop_loss
    : signal.stop_loss - signal.entry_price;
  const reward = isBuy
    ? signal.take_profit - signal.entry_price
    : signal.entry_price - signal.take_profit;
  const rrRatio = risk > 0 ? (reward / risk).toFixed(2) : "—";

  // Agent consensus
  const agents = [
    { label: "F", analysis: signal.fundamental_analysis },
    { label: "E", analysis: signal.economic_analysis },
    { label: "T", analysis: signal.technical_analysis },
    { label: "S", analysis: signal.sentiment_analysis },
  ];
  const agreeCount = agents.filter(
    (a) => a.analysis.recommendation === signal.signal
  ).length;

  const summaryText = signal.ai_explanation || buildFallbackSummary(signal);
  const isAiExplained = !!signal.ai_explanation;

  return (
    <>
      <Card
        className={getCardClass(
          true,
          `border-2 transition-all ${
            isBuy ? "border-alchmai-success/40" : "border-alchmai-danger/40"
          }`
        )}
      >
        {/* ── Header ── */}
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <CardTitle className="text-2xl text-alchmai-text-primary">
                {signal.instrument}
              </CardTitle>
              <CardDescription className="text-alchmai-text-secondary text-xs mt-0.5">
                Generated {formatDate(signal.timestamp)} · {signal.execution_time.toFixed(1)}s · {signal.api_calls_made} API calls
              </CardDescription>
            </div>

            <div className="flex items-center gap-2">
              {/* BUY / SELL badge */}
              <div
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-lg ${
                  isBuy
                    ? "bg-alchmai-success/20 text-alchmai-success border border-alchmai-success/30"
                    : "bg-alchmai-danger/20 text-alchmai-danger border border-alchmai-danger/30"
                }`}
              >
                <SignalIcon className="w-5 h-5" />
                {signal.signal}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowExplainModal(true)}
                className="border-alchmai-purple/30 text-alchmai-text-secondary hover:text-alchmai-text-primary hover:border-alchmai-purple/50"
              >
                <HelpCircle className="w-4 h-4 mr-1.5" />
                How did AI decide?
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          {/* ── AI Explanation / Summary ── */}
          <div className="p-4 rounded-xl bg-alchmai-darker/60 border border-alchmai-purple/20">
            {isAiExplained && (
              <div className="flex items-center gap-1.5 mb-2">
                <Sparkles className="w-3.5 h-3.5 text-alchmai-purple" />
                <span className="text-[10px] font-semibold text-alchmai-purple uppercase tracking-wider">
                  GPT-4o Analysis
                </span>
              </div>
            )}
            <p className={`leading-relaxed ${isAiExplained ? "text-sm text-alchmai-text-primary" : "text-sm text-alchmai-text-secondary"}`}>
              {summaryText}
            </p>
          </div>

          {/* ── Price Points ── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-xs text-alchmai-text-secondary mb-1">Entry Price</div>
              <div className="text-xl font-bold text-alchmai-text-primary">
                {formatCurrency(signal.entry_price)}
              </div>
              {signal.current_price && signal.current_price !== signal.entry_price && (
                <div className="text-xs text-alchmai-text-secondary mt-0.5">
                  Current: {formatCurrency(signal.current_price)}
                </div>
              )}
            </div>
            <div>
              <div className="text-xs text-alchmai-text-secondary mb-1">Stop Loss</div>
              <div className="text-xl font-bold text-alchmai-danger">
                {formatCurrency(signal.stop_loss)}
              </div>
              <div className="text-xs text-alchmai-danger/70 mt-0.5">
                Risk: {formatCurrency(Math.abs(risk))}
              </div>
            </div>
            <div>
              <div className="text-xs text-alchmai-text-secondary mb-1">Take Profit</div>
              <div className="text-xl font-bold text-alchmai-success">
                {formatCurrency(signal.take_profit)}
              </div>
              <div className="text-xs text-alchmai-success/70 mt-0.5">
                Reward: {formatCurrency(Math.abs(reward))}
              </div>
            </div>
            <div>
              <div className="text-xs text-alchmai-text-secondary mb-1">Confidence</div>
              <div className="text-xl font-bold text-alchmai-text-primary">
                {signal.confidence.toFixed(1)}%
              </div>
              <div className="w-full bg-alchmai-darker rounded-full h-1.5 mt-2">
                <div
                  className="bg-alchmai-purple h-1.5 rounded-full transition-all"
                  style={{ width: `${signal.confidence}%` }}
                />
              </div>
            </div>
          </div>

          {/* ── Risk / Reward bar ── */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-alchmai-text-secondary">
                Risk / Reward Ratio
              </span>
              <span className="text-alchmai-text-primary font-semibold">
                1 : {rrRatio}
              </span>
            </div>
            <div className="flex h-2 rounded-full overflow-hidden">
              {risk > 0 && reward > 0 && (
                <>
                  <div
                    className="bg-alchmai-danger/70"
                    style={{
                      width: `${(risk / (risk + reward)) * 100}%`,
                    }}
                  />
                  <div
                    className="bg-alchmai-success/70"
                    style={{
                      width: `${(reward / (risk + reward)) * 100}%`,
                    }}
                  />
                </>
              )}
            </div>
            <div className="flex justify-between text-xs mt-1 text-alchmai-text-secondary/60">
              <span>Risk</span>
              <span>Reward</span>
            </div>
          </div>

          {/* ── Agent Consensus ── */}
          <div className="pt-1">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-alchmai-text-secondary">
                Agent Consensus
              </span>
              <span className="text-xs text-alchmai-text-primary font-semibold">
                {agreeCount} / 4 agree on {signal.signal}
              </span>
            </div>
            <div className="flex gap-2">
              {agents.map((a) => {
                const agrees = a.analysis.recommendation === signal.signal;
                return (
                  <div
                    key={a.label}
                    className={`flex-1 rounded-lg p-2 text-center border text-xs font-bold transition-all ${
                      agrees
                        ? isBuy
                          ? "bg-alchmai-success/15 border-alchmai-success/40 text-alchmai-success"
                          : "bg-alchmai-danger/15 border-alchmai-danger/40 text-alchmai-danger"
                        : "bg-alchmai-darker/50 border-alchmai-text-secondary/20 text-alchmai-text-secondary"
                    }`}
                  >
                    <div className="text-base mb-0.5">{a.label}</div>
                    <div className="text-[10px] font-normal leading-tight">
                      {a.analysis.recommendation}
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-alchmai-text-secondary/60 mt-1.5">
              F = Fundamental · E = Economic · T = Technical · S = Sentiment
            </p>
          </div>
        </CardContent>
      </Card>

      <ExplainDecisionModal
        signal={signal}
        open={showExplainModal}
        onOpenChange={setShowExplainModal}
      />
    </>
  );
}
