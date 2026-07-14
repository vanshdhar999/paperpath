"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import { useRouter } from "next/navigation";
import type { User } from "@supabase/supabase-js";
import Link from "next/link";

interface TrackInfo {
  id: string;
  domain: string;
  name: string;
  paper_count: number;
}

interface Suggestion {
  id: string;
  arxiv_id: string;
  title: string;
  authors: string[];
  abstract: string;
  difficulty_tier: string;
  venue: string;
  similarity: number;
  reason: string;
}

const TRACK_META: Record<string, { desc: string; color: string }> = {
  beginner: {
    desc: "Foundational papers: Word2Vec, ResNet, Transformers, GANs",
    color: "border-green-500",
  },
  intermediate: {
    desc: "Core ML/AI: BERT, GPT-3, CLIP, LoRA, Diffusion Models",
    color: "border-yellow-500",
  },
  pro: {
    desc: "Advanced: RLHF, DPO, Flash Attention, Mamba, LLaMA",
    color: "border-red-500",
  },
};

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tracks, setTracks] = useState<TrackInfo[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();
  const router = useRouter();

  useEffect(() => {
    async function load() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }
      setUser(user);
      try {
        const data = await apiFetch("/tracks");
        setTracks(data);
      } catch {
        // Tracks endpoint doesn't require auth
      }
      try {
        const sug = await apiFetch("/suggestions");
        setSuggestions(sug);
      } catch {
        // Suggestions may fail if no auth
      }
      setLoading(false);
    }
    load();
  }, []);

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <p className="text-gray-400">Loading...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Paperpath</h1>
        <div className="flex items-center gap-4">
          <Link
            href={`/profile/${user?.email?.split("@")[0] || ""}`}
            className="text-sm text-gray-400 hover:text-white transition"
          >
            Profile
          </Link>
          <span className="text-sm text-gray-400">{user?.email}</span>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-white transition"
          >
            Sign out
          </button>
        </div>
      </header>
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h2 className="text-2xl font-bold mb-2">Choose your track</h2>
        <p className="text-gray-400 mb-8">
          Pick a difficulty level and start working through ML/AI research
          papers.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tracks.map((track) => {
            const meta = TRACK_META[track.name.toLowerCase()] || {
              desc: "",
              color: "border-gray-500",
            };
            return (
              <Link
                key={track.id}
                href={`/track/${track.id}`}
                className={`rounded-xl border-2 ${meta.color} bg-gray-900 p-6 hover:bg-gray-800 transition`}
              >
                <h3 className="text-lg font-semibold mb-2">{track.name}</h3>
                <p className="text-sm text-gray-400 mb-4">{meta.desc}</p>
                <p className="text-sm text-gray-500">
                  {track.paper_count} papers
                </p>
              </Link>
            );
          })}
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-2">Suggested for you</h2>
            <p className="text-gray-400 mb-6">
              Papers similar to ones you&apos;ve completed.
            </p>
            <div className="space-y-3">
              {suggestions.map((s) => (
                <Link
                  key={s.id}
                  href={`/paper/${s.id}`}
                  className="block rounded-lg bg-gray-900 border border-gray-800 px-5 py-4 hover:bg-gray-800 transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="font-medium">{s.title}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {s.authors?.slice(0, 3).join(", ")}
                        {s.authors?.length > 3 && " et al."}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">{s.abstract}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <span
                        className={`text-xs font-medium ${
                          s.difficulty_tier === "beginner"
                            ? "text-green-400"
                            : s.difficulty_tier === "intermediate"
                            ? "text-yellow-400"
                            : "text-red-400"
                        }`}
                      >
                        {s.difficulty_tier}
                      </span>
                      {s.similarity > 0 && (
                        <p className="text-xs text-gray-600 mt-1">
                          {Math.round(s.similarity * 100)}% match
                        </p>
                      )}
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 mt-2">{s.reason}</p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
