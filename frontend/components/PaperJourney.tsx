"use client";

import JargonTooltip from "./JargonTooltip";

interface JourneyData {
  problem: string;
  prior_approaches: string;
  method: string;
  results: string;
  why_it_matters: string;
  jargon: Array<{ term: string; explanation: string }>;
}

interface PaperJourneyProps {
  journey: JourneyData;
}

const SECTIONS = [
  { key: "problem", title: "The Problem", icon: "?" },
  { key: "prior_approaches", title: "Prior Approaches", icon: "←" },
  { key: "method", title: "Method", icon: "⚙" },
  { key: "results", title: "Results", icon: "📊" },
  { key: "why_it_matters", title: "Why It Matters", icon: "💡" },
] as const;

export default function PaperJourney({ journey }: PaperJourneyProps) {
  return (
    <div className="space-y-8">
      {SECTIONS.map(({ key, title, icon }) => (
        <section key={key} className="rounded-xl bg-gray-900 border border-gray-800 p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>{icon}</span> {title}
          </h3>
          <div className="text-gray-300 leading-relaxed whitespace-pre-line">
            {journey[key]}
          </div>
        </section>
      ))}

      {journey.jargon && journey.jargon.length > 0 && (
        <section className="rounded-xl bg-gray-900 border border-gray-800 p-6">
          <h3 className="text-lg font-semibold mb-4">Key Terms</h3>
          <div className="flex flex-wrap gap-3">
            {journey.jargon.map((item) => (
              <JargonTooltip
                key={item.term}
                term={item.term}
                explanation={item.explanation}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
