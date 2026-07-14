"use client";

import { useState } from "react";

interface JargonTooltipProps {
  term: string;
  explanation: string;
}

export default function JargonTooltip({ term, explanation }: JargonTooltipProps) {
  const [show, setShow] = useState(false);

  return (
    <span
      className="relative inline-block"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <span className="border-b border-dashed border-blue-400 text-blue-400 cursor-help">
        {term}
      </span>
      {show && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 rounded-lg bg-gray-800 border border-gray-700 p-3 text-sm text-gray-200 shadow-xl z-50">
          <span className="font-semibold text-white">{term}</span>
          <br />
          {explanation}
        </span>
      )}
    </span>
  );
}
