"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import PaperJourney from "@/components/PaperJourney";
import Link from "next/link";

interface PaperData {
  paper: {
    id: string;
    arxiv_id: string;
    title: string;
    authors: string[];
    venue: string;
    pdf_url: string;
  };
  journey: {
    problem: string;
    prior_approaches: string;
    method: string;
    results: string;
    why_it_matters: string;
    jargon: Array<{ term: string; explanation: string }>;
  };
  status: string;
}

export default function PaperPage() {
  const { id } = useParams();
  const router = useRouter();
  const supabase = createClient();
  const [data, setData] = useState<PaperData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
        const result = await apiFetch(
          `/papers/${id}/journey`,
          {},
          session.access_token
        );
        setData(result);
      } catch (e: any) {
        setError(e.message);
      }
      setLoading(false);
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <div className="text-center">
          <p className="text-gray-400">Loading paper journey...</p>
          <p className="text-xs text-gray-600 mt-2">
            First load may take ~30s while the paper is being restructured by AI
          </p>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <div className="text-center">
          <p className="text-red-400">{error || "Failed to load paper"}</p>
          <Link href="/dashboard" className="text-blue-400 hover:underline mt-4 block">
            Back to dashboard
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <button
          onClick={() => router.back()}
          className="text-gray-400 hover:text-white transition"
        >
          ← Back to track
        </button>
      </header>
      <div className="max-w-3xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">{data.paper.title}</h1>
          <p className="text-gray-400 mt-2">
            {data.paper.authors?.join(", ")}
          </p>
          <div className="flex gap-4 mt-3 text-sm text-gray-500">
            {data.paper.venue && <span>{data.paper.venue}</span>}
            <span>arXiv: {data.paper.arxiv_id}</span>
            {data.paper.pdf_url && (
              <a
                href={data.paper.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:underline"
              >
                View PDF
              </a>
            )}
          </div>
        </div>

        <PaperJourney journey={data.journey} />

        <div className="mt-8 text-center">
          {data.status !== "completed" ? (
            <Link
              href={`/paper/${id}/quiz`}
              className="inline-block rounded-lg bg-blue-600 px-8 py-3 font-medium text-white hover:bg-blue-700 transition"
            >
              Take the quiz
            </Link>
          ) : (
            <p className="text-green-400 font-medium">
              ✓ Paper completed
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
