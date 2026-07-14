"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import QuizCard from "@/components/QuizCard";
import Link from "next/link";

interface QuizQuestion {
  question: string;
  options: string[];
}

interface QuizResult {
  correct: number;
  total: number;
  passed: boolean;
  score_percent: number;
  unlocked_papers: string[];
  explanations: Array<{
    question: string;
    correct_index: number;
    user_answer: number;
    is_correct: boolean;
    explanation: string;
  }>;
}

export default function QuizPage() {
  const { id } = useParams();
  const router = useRouter();
  const supabase = createClient();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<(number | null)[]>([]);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");

  useEffect(() => {
    async function load() {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) {
        router.push("/login");
        return;
      }
      try {
        const data = await apiFetch(
          `/papers/${id}/quiz`,
          {},
          session.access_token
        );
        setQuestions(data.questions);
        setAnswers(new Array(data.questions.length).fill(null));
        setTitle(data.title);
      } catch (e: any) {
        setError(e.message);
      }
      setLoading(false);
    }
    load();
  }, [id]);

  async function handleSubmit() {
    if (answers.some((a) => a === null)) return;
    setSubmitting(true);
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) return;

    try {
      const data = await apiFetch(
        `/papers/${id}/quiz/submit`,
        {
          method: "POST",
          body: JSON.stringify({ answers }),
        },
        session.access_token
      );
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    }
    setSubmitting(false);
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <div className="text-center">
          <p className="text-gray-400">Loading quiz...</p>
          <p className="text-xs text-gray-600 mt-2">
            First load may take ~20s while questions are generated
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <p className="text-red-400">{error}</p>
      </main>
    );
  }

  const allAnswered = answers.every((a) => a !== null);

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <Link
          href={`/paper/${id}`}
          className="text-gray-400 hover:text-white transition"
        >
          ← Back to paper
        </Link>
      </header>
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-xl font-bold mb-2">Quiz: {title}</h1>
        <p className="text-gray-400 mb-8 text-sm">
          Answer all 5 questions. You need 3/5 correct to pass.
        </p>

        <div className="space-y-6">
          {questions.map((q, i) => (
            <QuizCard
              key={i}
              index={i}
              question={q.question}
              options={q.options}
              selectedAnswer={answers[i]}
              onSelect={(optIndex) => {
                if (result) return;
                const newAnswers = [...answers];
                newAnswers[i] = optIndex;
                setAnswers(newAnswers);
              }}
              disabled={!!result}
              result={result?.explanations[i]}
            />
          ))}
        </div>

        {!result ? (
          <div className="mt-8 text-center">
            <button
              onClick={handleSubmit}
              disabled={!allAnswered || submitting}
              className="rounded-lg bg-blue-600 px-8 py-3 font-medium text-white hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Grading..." : "Submit answers"}
            </button>
          </div>
        ) : (
          <div className="mt-8 rounded-xl bg-gray-900 border border-gray-800 p-6 text-center">
            <p
              className={`text-2xl font-bold ${
                result.passed ? "text-green-400" : "text-red-400"
              }`}
            >
              {result.passed ? "Passed!" : "Not quite"}
            </p>
            <p className="text-gray-400 mt-2">
              {result.correct}/{result.total} correct ({result.score_percent}%)
            </p>
            {result.passed ? (
              <div className="mt-4">
                {result.unlocked_papers.length > 0 && (
                  <p className="text-blue-400 text-sm mb-4">
                    {result.unlocked_papers.length} new paper
                    {result.unlocked_papers.length > 1 ? "s" : ""} unlocked!
                  </p>
                )}
                <Link
                  href="/dashboard"
                  className="inline-block rounded-lg bg-green-600 px-6 py-2 font-medium text-white hover:bg-green-700 transition"
                >
                  Back to dashboard
                </Link>
              </div>
            ) : (
              <div className="mt-4 space-x-4">
                <Link
                  href={`/paper/${id}`}
                  className="inline-block rounded-lg border border-gray-700 px-6 py-2 font-medium text-white hover:bg-gray-800 transition"
                >
                  Review paper
                </Link>
                <button
                  onClick={() => {
                    setResult(null);
                    setAnswers(new Array(questions.length).fill(null));
                  }}
                  className="inline-block rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700 transition"
                >
                  Try again
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
