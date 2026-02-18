import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  const pillars = [
    {
      icon: "📊",
      name: "Fundamental Analysis",
      weight: "20%",
      description:
        "Analyses company financials, P/E ratios, earnings surprises, revenue growth, and balance sheet strength to judge intrinsic value.",
      color: "border-alchmai-purple/40 bg-alchmai-purple/5",
      accent: "text-alchmai-purple",
    },
    {
      icon: "🌐",
      name: "Economic Analysis",
      weight: "15%",
      description:
        "Monitors GDP, inflation, unemployment, Federal Reserve decisions, and upcoming economic calendar events that move markets.",
      color: "border-alchmai-blue/40 bg-alchmai-blue/5",
      accent: "text-alchmai-blue",
    },
    {
      icon: "📈",
      name: "Technical Analysis",
      weight: "40%",
      description:
        "Reads 15-minute charts using RSI, MACD, Moving Averages, and Bollinger Bands to identify precise entry and exit price levels.",
      color: "border-alchmai-success/40 bg-alchmai-success/5",
      accent: "text-alchmai-success",
    },
    {
      icon: "🧠",
      name: "Social Sentiment",
      weight: "25%",
      description:
        "Processes thousands of news headlines using FinBERT — a financial-grade AI — to measure real-time market mood and breaking news impact.",
      color: "border-yellow-500/40 bg-yellow-500/5",
      accent: "text-yellow-400",
    },
  ];

  const steps = [
    {
      step: "01",
      title: "You Name the Instrument",
      body: 'Type any asset — a stock like "Apple", a forex pair like "EURUSD", a commodity like "Gold". The system normalises and identifies it instantly.',
    },
    {
      step: "02",
      title: "4 AI Agents Analyse in Parallel",
      body: "Four specialised agents fire simultaneously — each an expert in its own domain. No waiting, no guessing. Pure parallel intelligence.",
    },
    {
      step: "03",
      title: "A Decision is Synthesised",
      body: "A fifth orchestrator agent weighs every recommendation, resolves conflicts, calculates confidence, and generates a validated signal with exact price levels.",
    },
  ];

  return (
    <div className="min-h-screen bg-alchmai-dark text-alchmai-text-primary">

      {/* ── HERO ── */}
      <section className="relative overflow-hidden">
        {/* subtle radial glow behind the headline */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 80% 50% at 50% 0%, rgba(147,51,234,0.18) 0%, transparent 70%)",
          }}
        />

        <div className="container mx-auto max-w-5xl px-6 pt-24 pb-20 text-center relative z-10">
          {/* eyebrow */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-alchmai-purple/40 bg-alchmai-purple/10 text-alchmai-purple text-sm font-medium mb-8">
            <span className="w-2 h-2 rounded-full bg-alchmai-purple animate-pulse" />
            Powered by Alchmai — AI &amp; Intelligent Automation for Finance
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-6">
            4 AI Minds.{" "}
            <span className="bg-gradient-to-r from-alchmai-purple to-alchmai-blue bg-clip-text text-transparent">
              One Decision.
            </span>
            <br />
            Zero Hesitation.
          </h1>

          <p className="text-xl text-alchmai-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed">
            This is how AI is transforming trading. Four specialised agents —
            Fundamental, Economic, Technical, and Sentiment — analyse any
            financial instrument simultaneously and converge on a single,
            validated trading signal in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              asChild
              size="lg"
              className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white glow-purple text-base px-8 py-6"
            >
              <Link href="/dashboard">See It Live →</Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="border-alchmai-purple/40 text-alchmai-text-secondary hover:text-alchmai-text-primary hover:border-alchmai-purple text-base px-8 py-6"
            >
              <a
                href="https://www.alchmai.com/#product"
                target="_blank"
                rel="noopener noreferrer"
              >
                Explore Alchmai Products
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/* ── THE PROBLEM ── */}
      <section className="border-y border-alchmai-purple/10 bg-alchmai-darker/60 py-14">
        <div className="container mx-auto max-w-4xl px-6 text-center">
          <p className="text-2xl font-semibold text-alchmai-text-secondary leading-relaxed">
            Traditional traders spend{" "}
            <span className="text-alchmai-text-primary">
              30–60 minutes per trade
            </span>{" "}
            checking charts, reading news, and guessing macro conditions —
            separately, sequentially, and imperfectly.
            <br />
            <span className="text-alchmai-purple font-bold">
              Alchmai AI does all four in under 30 seconds.
            </span>
          </p>
        </div>
      </section>

      {/* ── 4 PILLARS ── */}
      <section className="py-20">
        <div className="container mx-auto max-w-6xl px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              The{" "}
              <span className="bg-gradient-to-r from-alchmai-purple to-alchmai-blue bg-clip-text text-transparent">
                4-Pillar Framework
              </span>
            </h2>
            <p className="text-alchmai-text-secondary text-lg max-w-xl mx-auto">
              Every signal is the consensus of four independent expert agents.
              One alone is not enough — all four together are.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {pillars.map((p) => (
              <div
                key={p.name}
                className={`rounded-xl border p-6 ${p.color} transition-all hover:scale-105`}
              >
                <div className="text-3xl mb-3">{p.icon}</div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-alchmai-text-primary text-sm">
                    {p.name}
                  </h3>
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-full border ${p.color} ${p.accent}`}
                  >
                    {p.weight}
                  </span>
                </div>
                <p className="text-alchmai-text-secondary text-xs leading-relaxed">
                  {p.description}
                </p>
              </div>
            ))}
          </div>

          <p className="text-center text-xs text-alchmai-text-secondary mt-6">
            Weights reflect the relative importance for 15-minute intraday
            signals. Technical (40%) dominates short-term; Economic (15%) sets
            the macro backdrop.
          </p>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="py-20 border-t border-alchmai-purple/10">
        <div className="container mx-auto max-w-4xl px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-alchmai-text-secondary text-lg">
              From instrument name to validated trading signal — in three steps.
            </p>
          </div>

          <div className="space-y-8">
            {steps.map((s, i) => (
              <div key={s.step} className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-alchmai-purple/20 border border-alchmai-purple/40 flex items-center justify-center">
                  <span className="text-alchmai-purple font-extrabold text-lg">
                    {s.step}
                  </span>
                </div>
                <div className="flex-1 pt-1">
                  <h3 className="text-lg font-bold text-alchmai-text-primary mb-1">
                    {s.title}
                  </h3>
                  <p className="text-alchmai-text-secondary leading-relaxed">
                    {s.body}
                  </p>
                </div>
                {i < steps.length - 1 && (
                  <div className="hidden" /> /* spacing handled by space-y */
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── LIVE DEMO CTA ── */}
      <section className="py-20 border-t border-alchmai-purple/10">
        <div
          className="container mx-auto max-w-3xl px-6 text-center rounded-2xl py-16"
          style={{
            background:
              "radial-gradient(ellipse 100% 100% at 50% 0%, rgba(147,51,234,0.15) 0%, transparent 70%)",
          }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-alchmai-success/40 bg-alchmai-success/10 text-alchmai-success text-sm font-medium mb-6">
            <span className="w-2 h-2 rounded-full bg-alchmai-success animate-pulse" />
            Live System — Real Market Data
          </div>

          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to see AI trading intelligence in action?
          </h2>
          <p className="text-alchmai-text-secondary text-lg mb-8">
            Enter any stock, forex pair, or commodity. Watch four agents
            deliberate in real time and produce a signal with entry, stop-loss,
            and take-profit levels.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              asChild
              size="lg"
              className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white glow-purple text-base px-10 py-6"
            >
              <Link href="/dashboard">Try the Live Demo</Link>
            </Button>
            <a
              href="https://www.alchmai.com/#product"
              target="_blank"
              rel="noopener noreferrer"
              className="text-alchmai-text-secondary hover:text-alchmai-purple transition-colors text-sm font-medium"
            >
              Learn about Alchmai products →
            </a>
          </div>
        </div>
      </section>

      {/* ── DISCLAIMER ── */}
      <section className="pb-10">
        <div className="container mx-auto max-w-4xl px-6">
          <p className="text-center text-xs text-alchmai-text-secondary/60">
            For demonstration and informational purposes only. Not financial
            advice. Always conduct your own research before trading.
          </p>
        </div>
      </section>
    </div>
  );
}
