"use client";

interface QuizCardProps {
  index: number;
  question: string;
  options: string[];
  selectedAnswer: number | null;
  onSelect: (index: number) => void;
  disabled: boolean;
  result?: {
    correct_index: number;
    is_correct: boolean;
    explanation: string;
  };
}

export default function QuizCard({
  index,
  question,
  options,
  selectedAnswer,
  onSelect,
  disabled,
  result,
}: QuizCardProps) {
  return (
    <div className="rounded-xl bg-gray-900 border border-gray-800 p-6">
      <p className="font-medium mb-4">
        <span className="text-gray-500 mr-2">{index + 1}.</span>
        {question}
      </p>
      <div className="space-y-2">
        {options.map((option, i) => {
          let borderColor = "border-gray-700";
          let bgColor = "bg-gray-800";

          if (result) {
            if (i === result.correct_index) {
              borderColor = "border-green-500";
              bgColor = "bg-green-900/30";
            } else if (i === selectedAnswer && !result.is_correct) {
              borderColor = "border-red-500";
              bgColor = "bg-red-900/30";
            }
          } else if (i === selectedAnswer) {
            borderColor = "border-blue-500";
            bgColor = "bg-blue-900/30";
          }

          return (
            <button
              key={i}
              onClick={() => !disabled && onSelect(i)}
              disabled={disabled}
              className={`w-full text-left rounded-lg border ${borderColor} ${bgColor} px-4 py-3 text-sm transition hover:border-gray-500 disabled:cursor-default`}
            >
              <span className="text-gray-500 mr-2">
                {String.fromCharCode(65 + i)}.
              </span>
              {option}
            </button>
          );
        })}
      </div>
      {result && (
        <p
          className={`mt-3 text-sm ${
            result.is_correct ? "text-green-400" : "text-red-400"
          }`}
        >
          {result.is_correct ? "✓ Correct" : "✗ Incorrect"} — {result.explanation}
        </p>
      )}
    </div>
  );
}
