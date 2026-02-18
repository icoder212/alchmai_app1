"use client";

import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, ColorType, LineStyle } from "lightweight-charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getCardClass } from "@/lib/alchmai-theme";
import { TrendingUp, TrendingDown, Sparkles } from "lucide-react";

interface TradingViewChartProps {
  symbol: string;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  signal?: 'BUY' | 'SELL'; // Signal direction for AI annotations
}

type Timeframe = '1D' | '1W' | '1M' | '3M';

export function TradingViewChart({ 
  symbol, 
  entryPrice, 
  stopLoss, 
  takeProfit,
  signal = 'BUY'
}: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [timeframe, setTimeframe] = useState<Timeframe>('1D');

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart with Alchmai dark theme
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { type: ColorType.Solid, color: '#0F0F23' }, // Alchmai dark
        textColor: '#FFFFFF', // White text
      },
      grid: {
        vertLines: { color: 'rgba(147, 51, 234, 0.1)' }, // Purple grid
        horzLines: { color: 'rgba(147, 51, 234, 0.1)' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: 'rgba(147, 51, 234, 0.3)',
      },
      rightPriceScale: {
        borderColor: 'rgba(147, 51, 234, 0.3)',
      },
    });

    chartRef.current = chart;

    // Add candlestick series for better visualization
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10B981', // Green for up candles
      downColor: '#EF4444', // Red for down candles
      borderVisible: false,
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444',
    });

    // Add line series for price levels
    const lineSeries = chart.addLineSeries({
      color: '#9333EA', // Alchmai purple
      lineWidth: 2,
    });
    
    // Add horizontal price lines for trading levels with AI annotations
    const entryLine = lineSeries.createPriceLine({
      price: entryPrice,
      color: '#3B82F6', // Alchmai blue for entry
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: true,
      title: 'Entry',
    });
    
    const stopLossLine = lineSeries.createPriceLine({
      price: stopLoss,
      color: '#EF4444', // Red for stop loss
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: true,
      title: 'Stop Loss',
    });
    
    const takeProfitLine = lineSeries.createPriceLine({
      price: takeProfit,
      color: '#10B981', // Green for take profit
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: true,
      title: 'Take Profit',
    });

    // Add AI annotation: BUY label at entry price
    if (signal === 'BUY') {
      lineSeries.createPriceLine({
        price: entryPrice,
        color: '#10B981',
        lineWidth: 0,
        axisLabelVisible: true,
        title: 'BUY ↑',
      });
    }

    // Calculate resistance level (approximate - can be enhanced)
    const resistanceLevel = Math.max(entryPrice, stopLoss, takeProfit) * 1.02;
    if (resistanceLevel > entryPrice * 1.01) {
      lineSeries.createPriceLine({
        price: resistanceLevel,
        color: '#9333EA',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        axisLabelVisible: true,
        title: 'RESIST',
      });
    }

    // Add sample candlestick data (in production, fetch real data based on timeframe)
    const now = Math.floor(Date.now() / 1000);
    const sampleData = [];
    let basePrice = entryPrice;
    
    // Generate more data points based on timeframe
    const dataPoints = timeframe === '1D' ? 24 : timeframe === '1W' ? 168 : timeframe === '1M' ? 720 : 2160;
    
    for (let i = -dataPoints; i <= 0; i++) {
      const time = now + i * 900; // 15-minute intervals
      const open = basePrice;
      const change = (Math.random() - 0.5) * (basePrice * 0.005);
      const close = basePrice + change;
      const high = Math.max(open, close) + Math.random() * (basePrice * 0.002);
      const low = Math.min(open, close) - Math.random() * (basePrice * 0.002);
      
      sampleData.push({
        time,
        open,
        high,
        low,
        close,
      });
      
      basePrice = close;
    }
    
    candlestickSeries.setData(sampleData);

    // Make chart responsive
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [symbol, entryPrice, stopLoss, takeProfit, signal, timeframe]);

  return (
    <Card className={getCardClass(true, "border-alchmai-purple/30")}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CardTitle className="text-xl font-bold text-alchmai-text-primary">
              {symbol} - Trading Levels
            </CardTitle>
            <Sparkles className="w-5 h-5 text-alchmai-purple" />
            <span className="text-xs text-alchmai-text-secondary">AI Powered</span>
          </div>
          
          {/* Timeframe buttons */}
          <div className="flex items-center space-x-2">
            {(['1D', '1W', '1M', '3M'] as Timeframe[]).map((tf) => (
              <Button
                key={tf}
                variant={timeframe === tf ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeframe(tf)}
                className={
                  timeframe === tf
                    ? 'bg-alchmai-purple hover:bg-alchmai-purple/90 text-white'
                    : 'border-alchmai-purple/30 text-alchmai-text-secondary hover:text-alchmai-text-primary'
                }
              >
                {tf}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
        
        {/* Legend */}
        <div className="mt-4 p-4 rounded-lg border border-alchmai-purple/20 bg-alchmai-darker/50">
          <div className="text-sm font-semibold text-alchmai-text-primary mb-2">Chart Elements</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-alchmai-blue"></div>
              <span className="text-alchmai-text-secondary">Entry Price</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-alchmai-danger"></div>
              <span className="text-alchmai-text-secondary">Stop Loss</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-alchmai-success"></div>
              <span className="text-alchmai-text-secondary">Take Profit</span>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-alchmai-purple" />
              <span className="text-alchmai-text-secondary">AI Signals</span>
            </div>
          </div>
        </div>
        
        {/* Price summary */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div className="p-3 rounded-lg border border-alchmai-blue/30 bg-alchmai-blue/10">
            <div className="text-xs text-alchmai-text-secondary mb-1">Entry</div>
            <div className="text-lg font-bold text-alchmai-blue">${entryPrice.toFixed(2)}</div>
          </div>
          <div className="p-3 rounded-lg border border-alchmai-danger/30 bg-alchmai-danger/10">
            <div className="text-xs text-alchmai-text-secondary mb-1">Stop Loss</div>
            <div className="text-lg font-bold text-alchmai-danger">${stopLoss.toFixed(2)}</div>
          </div>
          <div className="p-3 rounded-lg border border-alchmai-success/30 bg-alchmai-success/10">
            <div className="text-xs text-alchmai-text-secondary mb-1">Take Profit</div>
            <div className="text-lg font-bold text-alchmai-success">${takeProfit.toFixed(2)}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
