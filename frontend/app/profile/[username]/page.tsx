"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import ContributionGrid from "@/components/ContributionGrid";
import Link from "next/link";

interface ProfileData {
  username: string;
  name: string;
  domain_interests: string[];
  created_at: string;
  stats: {
    total_completed: number;
    beginner: number;
    intermediate: number;
    pro: number;
  };
  completed_papers: Array<{
    id: string;
    arxiv_id: string;
    title: string;
    difficulty_tier: string;
    venue: string;
    quiz_score: number;
    completed_at: string;
  }>;
  contributions: Record<string, number>;
}

const TIER_COLORS: Record<string, string> = {
  beginner: "text-green-400",
  intermediate: "text-yellow-400",
  pro: "text-red-400",
};

export default function ProfilePage() {
  const { username } = useParams();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/profile/${username}`);
        setProfile(data);
      } catch (e: any) {
        setError(e.message);
      }
      setLoading(false);
    }
    load();
  }, [username]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <p className="text-gray-400">Loading profile...</p>
      </main>
    );
  }

  if (error || !profile) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <div className="text-center">
          <p className="text-red-400">{error || "Profile not found"}</p>
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
        <Link href="/dashboard" className="text-gray-400 hover:text-white transition">
          ← Dashboard
        </Link>
      </header>
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* User info */}
        <div className="mb-8">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center text-2xl font-bold text-gray-400">
              {(profile.name || profile.username || "?")[0].toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold">
                {profile.name || profile.username}
              </h1>
              <p className="text-gray-400">@{profile.username}</p>
              {profile.domain_interests?.length > 0 && (
                <p className="text-sm text-gray-500 mt-1">
                  Interests: {profile.domain_interests.join(", ")}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="rounded-xl bg-gray-900 border border-gray-800 p-4 text-center">
            <p className="text-2xl font-bold">{profile.stats.total_completed}</p>
            <p className="text-sm text-gray-400">Completed</p>
          </div>
          <div className="rounded-xl bg-gray-900 border border-gray-800 p-4 text-center">
            <p className="text-2xl font-bold text-green-400">{profile.stats.beginner}</p>
            <p className="text-sm text-gray-400">Beginner</p>
          </div>
          <div className="rounded-xl bg-gray-900 border border-gray-800 p-4 text-center">
            <p className="text-2xl font-bold text-yellow-400">{profile.stats.intermediate}</p>
            <p className="text-sm text-gray-400">Intermediate</p>
          </div>
          <div className="rounded-xl bg-gray-900 border border-gray-800 p-4 text-center">
            <p className="text-2xl font-bold text-red-400">{profile.stats.pro}</p>
            <p className="text-sm text-gray-400">Pro</p>
          </div>
        </div>

        {/* Contribution grid */}
        <div className="rounded-xl bg-gray-900 border border-gray-800 p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Reading Activity</h2>
          <ContributionGrid contributions={profile.contributions} />
        </div>

        {/* Completed papers list */}
        {profile.completed_papers.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Completed Papers</h2>
            <div className="space-y-3">
              {profile.completed_papers.map((paper) => (
                <div
                  key={paper.id}
                  className="rounded-lg bg-gray-900 border border-gray-800 px-4 py-3 flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium">{paper.title}</p>
                    <div className="flex gap-3 text-sm text-gray-500 mt-1">
                      <span className={TIER_COLORS[paper.difficulty_tier]}>
                        {paper.difficulty_tier}
                      </span>
                      {paper.venue && <span>{paper.venue}</span>}
                      <span>Score: {paper.quiz_score}/5</span>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500">
                    {paper.completed_at
                      ? new Date(paper.completed_at).toLocaleDateString()
                      : ""}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.completed_papers.length === 0 && (
          <p className="text-center text-gray-500 py-8">
            No papers completed yet. Start a track to begin!
          </p>
        )}
      </div>
    </main>
  );
}
