"use client";

export function LiveMarketIndicator() {
  return (
    <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-alchmai-darker/50 border border-alchmai-purple/20">
      <div className="relative">
        <div className="w-2 h-2 bg-alchmai-success rounded-full animate-pulse-slow"></div>
        <div className="absolute inset-0 w-2 h-2 bg-alchmai-success rounded-full animate-ping opacity-75"></div>
      </div>
      <span className="text-xs font-semibold text-alchmai-text-primary">
        LIVE MARKET DATA
      </span>
    </div>
  );
}
