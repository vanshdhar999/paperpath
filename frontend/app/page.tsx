"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import Link from "next/link";

export default function Home() {
  const router = useRouter();
  const supabase = createClient();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === "SIGNED_IN" && session) {
        // Sync user to backend
        try {
          const apiUrl =
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
          await fetch(`${apiUrl}/auth/sync-user`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${session.access_token}`,
            },
          });
        } catch {
          // Non-blocking
        }
        router.push("/dashboard");
      }
    });

    // Also check if already signed in
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        router.push("/dashboard");
      } else {
        setChecking(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <p className="text-gray-400">Loading...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-950 text-white">
      <h1 className="text-5xl font-bold">Paperpath</h1>
      <p className="mt-4 text-lg text-gray-400 max-w-md text-center">
        Duolingo for research papers. Read ML/AI papers through structured
        journeys, prove understanding via quizzes, and build your public
        research profile.
      </p>
      <div className="mt-8 flex gap-4">
        <Link
          href="/signup"
          className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700 transition"
        >
          Get started
        </Link>
        <Link
          href="/login"
          className="rounded-lg border border-gray-700 px-6 py-3 font-medium text-white hover:bg-gray-800 transition"
        >
          Sign in
        </Link>
      </div>
    </main>
  );
}
