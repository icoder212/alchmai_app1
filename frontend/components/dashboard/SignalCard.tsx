"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TradingSignal } from "@/lib/api";
import { formatCurrency, formatPercent, formatDate } from "@/lib/utils";
import { TrendingUp, TrendingDown } from "lucide-react";

interface SignalCardProps {
  signal: TradingSignal;
}

export function SignalCard({ signal }: SignalCardProps) {
  const isBuy = signal.signal === "BUY";
  const SignalIcon = isBuy ? TrendingUp : TrendingDown;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl">{signal.instrument}</CardTitle>
            <CardDescription>
              Generated {formatDate(signal.timestamp)}
            </CardDescription>
          </div>
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              isBuy
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
            }`}
          >
            <SignalIcon className="w-5 h-5" />
            <span className="font-bold text-lg">{signal.signal}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <div>
            <div className="text-sm text-muted-foreground">Entry Price</div>
            <div className="text-2xl font-bold">{formatCurrency(signal.entry_price)}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Stop Loss</div>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(signal.stop_loss)}
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Take Profit</div>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(signal.take_profit)}
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Confidence</div>
            <div className="text-2xl font-bold">{formatPercent(signal.confidence)}</div>
            <div className="w-full bg-muted rounded-full h-2 mt-2">
              <div
                className="bg-primary h-2 rounded-full"
                style={{ width: `${signal.confidence}%` }}
              />
            </div>
          </div>
        </div>

        {signal.current_price && (
          <div className="text-sm text-muted-foreground">
            Current Price: {formatCurrency(signal.current_price)}
          </div>
        )}

        <div className="mt-4 text-sm text-muted-foreground">
          Execution Time: {signal.execution_time.toFixed(2)}s | 
          API Calls: {signal.api_calls_made}
        </div>
      </CardContent>
    </Card>
  );
}
