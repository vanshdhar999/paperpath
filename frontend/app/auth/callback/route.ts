import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const token_hash = searchParams.get("token_hash");
  const type = searchParams.get("type");

  const cookieStore = await cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options);
          });
        },
      },
    }
  );

  let authError = null;

  if (token_hash && type) {
    // Implicit flow — verify the OTP token hash directly
    const { error } = await supabase.auth.verifyOtp({
      token_hash,
      type: type as "magiclink" | "email",
    });
    authError = error;
  } else if (code) {
    // PKCE flow — exchange code for session
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    authError = error;
  } else {
    // No code or token_hash — redirect to login
    return NextResponse.redirect(`${origin}/login`);
  }

  if (!authError) {
    // Sync user to our backend
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (session) {
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
    }
    return NextResponse.redirect(`${origin}/dashboard`);
  }

  console.error("Auth callback error:", authError);
  return NextResponse.redirect(`${origin}/login`);
}
