"use client";

import { useEffect, useRef } from "react";
import { createChart, IChartApi, ColorType } from "lightweight-charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TradingViewChartProps {
  symbol: string;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
}

export function TradingViewChart({ symbol, entryPrice, stopLoss, takeProfit }: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Add line series for price levels
    const lineSeries = chart.addLineSeries({
      color: '#2962FF',
      lineWidth: 2,
    });
    
    // Add horizontal price lines for trading levels
    lineSeries.createPriceLine({
      price: entryPrice,
      color: '#2962FF',
      lineWidth: 2,
      lineStyle: 2, // Dashed
      axisLabelVisible: true,
      title: 'Entry',
    });
    
    lineSeries.createPriceLine({
      price: stopLoss,
      color: '#EF5350',
      lineWidth: 2,
      lineStyle: 2, // Dashed
      axisLabelVisible: true,
      title: 'Stop Loss',
    });
    
    lineSeries.createPriceLine({
      price: takeProfit,
      color: '#26A69A',
      lineWidth: 2,
      lineStyle: 2, // Dashed
      axisLabelVisible: true,
      title: 'Take Profit',
    });

    // Add some sample data to show the chart (in production, fetch real data)
    const now = Math.floor(Date.now() / 1000);
    const sampleData = [];
    for (let i = -20; i <= 0; i++) {
      const time = now + i * 900; // 15-minute intervals
      const price = entryPrice + (Math.random() - 0.5) * (entryPrice * 0.01);
      sampleData.push({ time, value: price });
    }
    lineSeries.setData(sampleData);

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
  }, [symbol, entryPrice, stopLoss, takeProfit]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{symbol} - Trading Levels</CardTitle>
      </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} />
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Entry:</span>
            <span className="ml-2 font-semibold text-blue-600">${entryPrice.toFixed(2)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Stop Loss:</span>
            <span className="ml-2 font-semibold text-red-600">${stopLoss.toFixed(2)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Take Profit:</span>
            <span className="ml-2 font-semibold text-green-600">${takeProfit.toFixed(2)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
