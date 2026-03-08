import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "LeanProve AI - AI-Powered Lean 4 Math Proof Assistant",
  description:
    "Semantic search over 200k+ Mathlib theorems, AI proof generation, error diagnosis, and LaTeX-Lean conversion for formal mathematics research.",
  keywords: ["Lean 4", "Mathlib", "formal proof", "theorem prover", "AI", "mathematics"],
  authors: [{ name: "LeanProve AI Team" }],
  openGraph: {
    title: "LeanProve AI",
    description: "AI-Powered Lean 4 Math Proof Assistant",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-bg-dark text-text-primary antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 5000,
            style: {
              background: "#1E293B",
              color: "#F8FAFC",
              border: "1px solid #334155",
              borderRadius: "8px",
              fontFamily: "Inter, sans-serif",
              fontSize: "14px",
            },
          }}
        />
      </body>
    </html>
  );
}
