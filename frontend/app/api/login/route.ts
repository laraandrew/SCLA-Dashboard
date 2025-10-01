import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { password } = await req.json();

  if (!process.env.DASH_PASSWORD) {
    return NextResponse.json({ ok: false }, { status: 500 });
  }

  if (password === process.env.DASH_PASSWORD) {
    const res = NextResponse.json({ ok: true });
    res.cookies.set("scla_auth", "1", {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    });
    return res;
  }

  return NextResponse.json({ ok: false }, { status: 401 });
}
