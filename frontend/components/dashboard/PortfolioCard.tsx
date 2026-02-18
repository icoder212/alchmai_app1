"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getCardClass } from "@/lib/alchmai-theme";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { TrendingUp, TrendingDown, Wallet } from "lucide-react";

interface PortfolioCardProps {
  totalValue: number;
  changePercent: number;
  changeType: 'positive' | 'negative';
  hasPortfolio?: boolean; // If false, show "Connect Portfolio" button
  onConnect?: () => void; // Callback for connect button
  loading?: boolean;
}

export function PortfolioCard({
  totalValue,
  changePercent,
  changeType,
  hasPortfolio = true,
  onConnect,
  loading = false,
}: PortfolioCardProps) {
  if (loading) {
    return (
      <Card className={getCardClass(true, "border-alchmai-purple/30 h-full")}>
        <CardContent className="pt-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-alchmai-darker rounded"></div>
            <div className="h-4 bg-alchmai-darker rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!hasPortfolio) {
    return (
      <Card className={getCardClass(true, "border-alchmai-purple/30 h-full")}>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-alchmai-text-primary flex items-center gap-2 uppercase tracking-wide">
            <Wallet className="w-4 h-4" />
            <span>Total Portfolio</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-alchmai-text-secondary">
              Connect your portfolio to track performance
            </p>
            <Button
              onClick={onConnect}
              className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white glow-purple w-full"
            >
              Connect Portfolio
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-bold text-alchmai-text-primary flex items-center gap-2 uppercase tracking-wide">
          <Wallet className="w-4 h-4" />
          <span>Total Portfolio</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-4xl font-bold text-alchmai-text-primary">
            {formatCurrency(totalValue)}
          </div>
          <div className={`flex items-center gap-2 text-sm font-semibold ${
            changeType === 'positive' ? 'text-alchmai-success' : 'text-alchmai-danger'
          }`}>
            {changeType === 'positive' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span>
              {changeType === 'positive' ? '+' : ''}{formatPercent(changePercent)} vs Yesterday
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
