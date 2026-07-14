"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import type { User } from "@supabase/supabase-js";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();
  const router = useRouter();

  useEffect(() => {
    async function getUser() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }
      setUser(user);
      setLoading(false);
    }
    getUser();
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
          {[
            {
              name: "Beginner",
              desc: "Foundational papers: Word2Vec, ResNet, Transformers, GANs",
              papers: 7,
              color: "border-green-500",
            },
            {
              name: "Intermediate",
              desc: "Core ML/AI: BERT, GPT-3, CLIP, LoRA, Diffusion Models",
              papers: 10,
              color: "border-yellow-500",
            },
            {
              name: "Pro",
              desc: "Advanced: RLHF, DPO, Flash Attention, Mamba, LLaMA",
              papers: 8,
              color: "border-red-500",
            },
          ].map((track) => (
            <div
              key={track.name}
              className={`rounded-xl border-2 ${track.color} bg-gray-900 p-6 hover:bg-gray-800 transition cursor-pointer`}
            >
              <h3 className="text-lg font-semibold mb-2">{track.name}</h3>
              <p className="text-sm text-gray-400 mb-4">{track.desc}</p>
              <p className="text-sm text-gray-500">{track.papers} papers</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
