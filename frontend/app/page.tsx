import Link from "next/link";

export default function Home() {
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
