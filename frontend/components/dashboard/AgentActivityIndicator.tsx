"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCardClass } from "@/lib/alchmai-theme";
import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";

interface AgentStatus {
  name: string;
  status: "idle" | "analyzing" | "complete" | "error";
  progress?: number;
}

interface AgentActivityIndicatorProps {
  agents: AgentStatus[];
  show?: boolean;
}

// Realistic thinking lines per agent — cycles while analyzing
const THINKING_LINES: Record<string, string[]> = {
  Fundamental: [
    "Fetching company financials…",
    "Calculating P/E ratio…",
    "Reviewing earnings surprises…",
    "Analysing revenue growth trend…",
    "Checking debt-to-equity ratio…",
    "Evaluating profit margins…",
    "Scoring fundamental health…",
  ],
  Economic: [
    "Pulling latest GDP data…",
    "Checking CPI inflation figures…",
    "Reading Fed funds rate…",
    "Scanning economic calendar…",
    "Assessing unemployment rate…",
    "Evaluating macro backdrop…",
    "Scoring economic conditions…",
  ],
  Technical: [
    "Loading 15-minute chart data…",
    "Calculating RSI (14-period)…",
    "Computing MACD signal line…",
    "Measuring Bollinger Band width…",
    "Checking price vs SMA-20…",
    "Identifying support & resistance…",
    "Generating entry / SL / TP levels…",
  ],
  Sentiment: [
    "Fetching recent news headlines…",
    "Running FinBERT sentiment model…",
    "Scoring positive vs negative articles…",
    "Weighing breaking news impact…",
    "Aggregating social media signals…",
    "Calculating sentiment polarity…",
    "Finalising sentiment score…",
  ],
};

function AgentCard({ agent }: { agent: AgentStatus }) {
  const [lineIndex, setLineIndex] = useState(0);
  const lines = THINKING_LINES[agent.name] ?? ["Analysing…"];

  useEffect(() => {
    if (agent.status !== "analyzing") return;
    setLineIndex(0);
    const id = setInterval(() => {
      setLineIndex((prev) => (prev + 1) % lines.length);
    }, 900);
    return () => clearInterval(id);
  }, [agent.status, lines.length]);

  const borderColor =
    agent.status === "analyzing"
      ? "border-alchmai-purple"
      : agent.status === "complete"
      ? "border-alchmai-success"
      : agent.status === "error"
      ? "border-alchmai-danger"
      : "border-alchmai-text-secondary/20";

  const bgColor =
    agent.status === "analyzing"
      ? "bg-alchmai-purple/5"
      : agent.status === "complete"
      ? "bg-alchmai-success/5"
      : agent.status === "error"
      ? "bg-alchmai-danger/5"
      : "bg-alchmai-darker/40";

  const icon =
    agent.status === "analyzing" ? (
      <Loader2 className="w-4 h-4 animate-spin text-alchmai-purple" />
    ) : agent.status === "complete" ? (
      <CheckCircle2 className="w-4 h-4 text-alchmai-success" />
    ) : agent.status === "error" ? (
      <XCircle className="w-4 h-4 text-alchmai-danger" />
    ) : (
      <Clock className="w-4 h-4 text-alchmai-text-secondary/50" />
    );

  return (
    <div
      className={`rounded-xl border-2 p-4 transition-all duration-300 ${borderColor} ${bgColor}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-alchmai-text-primary">
          {agent.name}
        </span>
        {icon}
      </div>

      {agent.status !== "idle" && (
        <div className="w-full bg-alchmai-darker rounded-full h-1.5 mb-3">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              agent.status === "complete"
                ? "bg-alchmai-success"
                : agent.status === "error"
                ? "bg-alchmai-danger"
                : "bg-alchmai-purple"
            }`}
            style={{
              width:
                agent.status === "complete" || agent.status === "error"
                  ? "100%"
                  : `${agent.progress ?? 0}%`,
            }}
          />
        </div>
      )}

      <div className="min-h-[1.25rem]">
        {agent.status === "analyzing" && (
          <p className="text-xs text-alchmai-text-secondary truncate">
            {lines[lineIndex]}
          </p>
        )}
        {agent.status === "complete" && (
          <p className="text-xs text-alchmai-success">Analysis complete ✓</p>
        )}
        {agent.status === "error" && (
          <p className="text-xs text-alchmai-danger">Analysis failed</p>
        )}
        {agent.status === "idle" && (
          <p className="text-xs text-alchmai-text-secondary/50">Waiting…</p>
        )}
      </div>
    </div>
  );
}

export function AgentActivityIndicator({
  agents,
  show = true,
}: AgentActivityIndicatorProps) {
  if (!show) return null;

  const analyzing = agents.filter((a) => a.status === "analyzing").length;
  const complete = agents.filter((a) => a.status === "complete").length;

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold text-alchmai-text-primary">
            AI Agents Working
          </CardTitle>
          <span className="text-xs text-alchmai-text-secondary">
            {complete === 4
              ? "All agents complete"
              : `${analyzing} of 4 analysing…`}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {agents.map((agent, i) => (
            <AgentCard key={i} agent={agent} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
