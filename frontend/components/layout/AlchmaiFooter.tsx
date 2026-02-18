"use client";

import Link from "next/link";
import Image from "next/image";

export function AlchmaiFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full border-t border-alchmai-purple/20 bg-alchmai-dark">
      {/* Brand CTA strip */}
      <div className="border-b border-alchmai-purple/10 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-alchmai-text-secondary text-sm mb-2">
            Impressed by what you saw?
          </p>
          <p className="text-alchmai-text-primary font-semibold text-base mb-4">
            Alchmai builds custom AI &amp; intelligent automation solutions for finance.
          </p>
          <a
            href="https://www.alchmai.com/#product"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-alchmai-purple/20 border border-alchmai-purple/40 text-alchmai-purple hover:bg-alchmai-purple/30 hover:border-alchmai-purple/60 transition-all text-sm font-semibold"
          >
            Explore Alchmai Products →
          </a>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-alchmai-text-secondary">
          <div className="flex items-center gap-2">
            <span>Powered by</span>
            <Link
              href="https://alchmai.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center opacity-80 hover:opacity-100 transition-opacity"
            >
              <Image
                src="/alchmai-logo.png"
                alt="Alchmai"
                width={80}
                height={22}
                className="h-5 w-auto object-contain"
              />
            </Link>
            <span>— AI &amp; Intelligent Automation for Finance</span>
          </div>
          <div className="flex items-center gap-4">
            <span>© {currentYear} Alchmai. All rights reserved.</span>
            <span className="text-alchmai-text-secondary/40">|</span>
            <span className="italic text-alchmai-text-secondary/60">
              For informational purposes only. Not financial advice.
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
