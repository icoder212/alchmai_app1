"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getCardClass } from "@/lib/alchmai-theme";
import { Sparkles } from "lucide-react";

interface AIActionDemoProps {
  demo: 'signals' | 'volume' | 'risk';
  onTryFeature?: () => void;
}

export function AIActionDemo({ demo, onTryFeature }: AIActionDemoProps) {
  if (demo === 'signals') {
    return (
      <Card className={getCardClass(true, "border-alchmai-purple/30")}>
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-alchmai-text-primary flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-alchmai-purple" />
            <span>See AI In Action</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <p className="text-alchmai-text-secondary text-lg">
              Watch how Alchmai transforms trading from chaos to mathematical certainty
            </p>
            <p className="text-alchmai-text-secondary">
              Our AI-powered system analyzes 4 pillars of market data in real-time to generate 
              accurate trading signals in just 20-30 seconds. Experience the power of automated 
              decision-making backed by advanced machine learning.
            </p>
            {onTryFeature && (
              <Button
                onClick={onTryFeature}
                className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white glow-purple text-lg px-8 py-6"
                size="lg"
              >
                Try This Feature Now
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardContent className="pt-6">
        <div className="text-center py-8">
          <p className="text-alchmai-text-secondary">
            {demo === 'volume' 
              ? 'Volume Spike Detection feature coming soon!'
              : 'Risk Assessment feature coming soon!'}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
