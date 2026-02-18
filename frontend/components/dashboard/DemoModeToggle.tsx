"use client";

import { Button } from "@/components/ui/button";

interface DemoModeToggleProps {
  currentDemo: 'signals' | 'volume' | 'risk';
  onDemoChange: (demo: 'signals' | 'volume' | 'risk') => void;
}

export function DemoModeToggle({ currentDemo, onDemoChange }: DemoModeToggleProps) {
  const demos = [
    { id: 'signals' as const, label: 'AI Trade Signals', available: true },
    { id: 'volume' as const, label: 'Volume Spike Detection', available: false },
    { id: 'risk' as const, label: 'Risk Assessment', available: false },
  ];

  return (
    <div className="flex items-center space-x-2 p-1 rounded-lg bg-alchmai-darker/50 border border-alchmai-purple/20">
      {demos.map((demo) => (
        <Button
          key={demo.id}
          variant={currentDemo === demo.id ? 'default' : 'ghost'}
          size="sm"
          onClick={() => demo.available && onDemoChange(demo.id)}
          disabled={!demo.available}
          className={
            currentDemo === demo.id
              ? 'bg-alchmai-purple hover:bg-alchmai-purple/90 text-white'
              : 'text-alchmai-text-secondary hover:text-alchmai-text-primary'
          }
        >
          {demo.label}
          {!demo.available && (
            <span className="ml-2 text-xs opacity-50">(Coming Soon)</span>
          )}
        </Button>
      ))}
    </div>
  );
}
