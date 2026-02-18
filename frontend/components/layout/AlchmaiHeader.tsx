"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { getCardClass } from "@/lib/alchmai-theme";

export function AlchmaiHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-alchmai-purple/20 bg-alchmai-dark/95 backdrop-blur supports-[backdrop-filter]:bg-alchmai-dark/80">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center">
          <Image
            src="/alchmai-logo.png"
            alt="Alchmai"
            width={140}
            height={40}
            className="h-10 w-auto object-contain"
            priority
          />
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          <Link
            href="/"
            className="text-alchmai-text-secondary hover:text-alchmai-text-primary transition-colors"
          >
            Home
          </Link>
          <Link
            href="#services"
            className="text-alchmai-text-secondary hover:text-alchmai-text-primary transition-colors"
          >
            Services
          </Link>
          <Link
            href="#about"
            className="text-alchmai-text-secondary hover:text-alchmai-text-primary transition-colors"
          >
            About Us
          </Link>
          <Link
            href="#contact"
            className="text-alchmai-text-secondary hover:text-alchmai-text-primary transition-colors"
          >
            Contact Us
          </Link>
        </nav>

        {/* Get Started Button */}
        <div className="flex items-center space-x-4">
          <Button
            asChild
            className="bg-alchmai-purple hover:bg-alchmai-purple/90 text-white glow-purple"
          >
            <a
              href="https://alchmai.com/#product"
              target="_blank"
              rel="noopener noreferrer"
            >
              Get Started
            </a>
          </Button>
        </div>
      </div>
    </header>
  );
}
