import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AlchmaiHeader } from "@/components/layout/AlchmaiHeader";
import { AlchmaiFooter } from "@/components/layout/AlchmaiFooter";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Alchmai AI - Trading Signal Generator",
  description: "AI-powered trading signals using 4-pillar analysis (Fundamental, Technical, Economic, Social Sentiment)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col bg-alchmai-dark bg-grid-pattern">
          <AlchmaiHeader />
          <main className="flex-1">{children}</main>
          <AlchmaiFooter />
        </div>
      </body>
    </html>
  );
}
