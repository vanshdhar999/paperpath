"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import SkillTree from "@/components/SkillTree";
import Link from "next/link";

interface TrackData {
  track: { id: string; domain: string; name: string };
  papers: Array<{
    id: string;
    arxiv_id: string;
    title: string;
    authors: string[];
    abstract: string;
    difficulty_tier: string;
    venue: string;
    status: string;
    quiz_score: number | null;
    prerequisite_ids: string[];
    order: number;
  }>;
}

export default function TrackPage() {
  const { id } = useParams();
  const router = useRouter();
  const supabase = createClient();
  const [data, setData] = useState<TrackData | null>(null);
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
        const result = await apiFetch(`/tracks/${id}/papers`, {}, session.access_token);
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
        <p className="text-gray-400">Loading track...</p>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <p className="text-red-400">{error || "Failed to load track"}</p>
      </main>
    );
  }

  const completed = data.papers.filter((p) => p.status === "completed").length;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-400 hover:text-white transition">
            ← Back
          </Link>
          <h1 className="text-xl font-bold">
            {data.track.domain} — {data.track.name}
          </h1>
        </div>
        <span className="text-sm text-gray-400">
          {completed}/{data.papers.length} papers completed
        </span>
      </header>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <SkillTree
          papers={data.papers}
          onPaperClick={(paperId) => router.push(`/paper/${paperId}`)}
        />
      </div>
    </main>
  );
}
