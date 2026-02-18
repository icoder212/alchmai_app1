import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { cn } from "./utils";

/**
 * Get Tailwind classes for purple glow effect
 * @param intensity - 'default' | 'large' for glow intensity
 * @returns Tailwind class string
 */
export function getGlowClass(intensity: 'default' | 'large' = 'default'): string {
  return intensity === 'large' ? 'glow-purple-lg' : 'glow-purple';
}

/**
 * Get Tailwind classes for blue glow effect
 * @param intensity - 'default' | 'large' for glow intensity
 * @returns Tailwind class string
 */
export function getBlueGlowClass(intensity: 'default' | 'large' = 'default'): string {
  return intensity === 'large' ? 'glow-blue-lg' : 'glow-blue';
}

/**
 * Get Tailwind classes for Alchmai-styled card
 * @param withGlow - Whether to add glow effect
 * @param additionalClasses - Additional classes to merge
 * @returns Tailwind class string
 */
export function getCardClass(
  withGlow: boolean = true,
  additionalClasses?: ClassValue
): string {
  const baseClasses = "bg-card border border-alchmai-purple/20 rounded-lg";
  const glowClass = withGlow ? getGlowClass() : "";
  
  return cn(baseClasses, glowClass, additionalClasses);
}

/**
 * Get color class based on theme
 * @param colorType - 'primary' | 'secondary' | 'accent' | 'success' | 'danger'
 * @returns Tailwind class string
 */
export function getColorClass(
  colorType: 'primary' | 'secondary' | 'accent' | 'success' | 'danger'
): string {
  const colorMap = {
    primary: 'text-alchmai-purple',
    secondary: 'text-alchmai-blue',
    accent: 'text-alchmai-purple',
    success: 'text-alchmai-success',
    danger: 'text-alchmai-danger',
  };
  
  return colorMap[colorType];
}

/**
 * Get background color class
 * @param colorType - 'primary' | 'secondary' | 'dark' | 'darker'
 * @returns Tailwind class string
 */
export function getBgColorClass(
  colorType: 'primary' | 'secondary' | 'dark' | 'darker'
): string {
  const colorMap = {
    primary: 'bg-alchmai-purple',
    secondary: 'bg-alchmai-blue',
    dark: 'bg-alchmai-dark',
    darker: 'bg-alchmai-darker',
  };
  
  return colorMap[colorType];
}

/**
 * Enhanced currency formatting with Alchmai styling
 * @param value - Number to format
 * @param currency - Currency code (default: 'USD')
 * @returns Formatted currency string
 */
export function formatCurrency(value: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Enhanced percentage formatting
 * @param value - Number to format (0-100)
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Get rating badge class based on score
 * @param score - Score from 0-10
 * @returns Object with rating text and color class
 */
export function getRatingBadge(score: number): {
  rating: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
  colorClass: string;
} {
  if (score >= 8.5) {
    return { rating: 'EXCELLENT', colorClass: 'bg-alchmai-success text-white' };
  } else if (score >= 7) {
    return { rating: 'GOOD', colorClass: 'bg-alchmai-blue text-white' };
  } else if (score >= 5) {
    return { rating: 'FAIR', colorClass: 'bg-yellow-500 text-white' };
  } else {
    return { rating: 'POOR', colorClass: 'bg-alchmai-danger text-white' };
  }
}

/**
 * Convert confidence from 0-100 scale to 0-10 scale
 * @param confidence - Confidence value 0-100
 * @returns Confidence value 0-10 with 1 decimal place
 */
export function convertConfidenceTo10Scale(confidence: number): number {
  return parseFloat((confidence / 10).toFixed(1));
}
