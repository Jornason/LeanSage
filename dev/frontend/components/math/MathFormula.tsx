"use client";

import { useEffect, useRef, useState } from "react";

interface MathFormulaProps {
  formula: string;
  display?: boolean;
  className?: string;
}

export function MathFormula({ formula, display = false, className = "" }: MathFormulaProps) {
  const containerRef = useRef<HTMLSpanElement | HTMLDivElement>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const render = async () => {
      if (!containerRef.current) return;
      try {
        // Dynamic import of KaTeX to avoid SSR issues
        const katex = (await import("katex")).default;
        katex.render(formula, containerRef.current, {
          displayMode: display,
          throwOnError: false,
          strict: false,
          trust: false,
          output: "htmlAndMathml",
        });
        setError(false);
      } catch (err) {
        // Fallback: show raw formula
        setError(true);
      }
    };

    render();
  }, [formula, display]);

  if (error) {
    return (
      <span
        className={`font-mono text-sm text-text-secondary ${className}`}
        title="KaTeX render failed — showing raw LaTeX"
      >
        {formula}
      </span>
    );
  }

  if (display) {
    return (
      <div
        ref={containerRef as React.RefObject<HTMLDivElement>}
        className={`katex-display text-text-primary ${className}`}
      />
    );
  }

  return (
    <span
      ref={containerRef as React.RefObject<HTMLSpanElement>}
      className={`katex-inline text-text-primary ${className}`}
    />
  );
}

// Utility to render KaTeX in a string containing $...$ or $$...$$
export function MathText({ text, className = "" }: { text: string; className?: string }) {
  const parts = text.split(/(\$\$[\s\S]*?\$\$|\$[^$]*?\$)/g);

  return (
    <span className={className}>
      {parts.map((part, i) => {
        if (part.startsWith("$$") && part.endsWith("$$")) {
          return (
            <MathFormula
              key={i}
              formula={part.slice(2, -2)}
              display={true}
            />
          );
        } else if (part.startsWith("$") && part.endsWith("$")) {
          return (
            <MathFormula
              key={i}
              formula={part.slice(1, -1)}
              display={false}
            />
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}
