import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Trading Signal Generator
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Multi-agent AI system for generating 15-30 minute trading signals
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-12">
          <Card>
            <CardHeader>
              <CardTitle>4 Analysis Pillars</CardTitle>
              <CardDescription>
                Comprehensive market analysis through multiple lenses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Fundamental Analysis</li>
                <li>• Economic Analysis</li>
                <li>• Technical Analysis (15-min charts)</li>
                <li>• Sentiment Analysis</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Real-time Signals</CardTitle>
              <CardDescription>
                Get instant trading signals with entry, stop-loss, and take-profit
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• BUY/SELL recommendations</li>
                <li>• Confidence scores</li>
                <li>• Price point analysis</li>
                <li>• WebSocket live updates</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <Link href="/login">
            <Button size="lg" className="text-lg px-8">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
