import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/api/login", "/favicon.ico", "/robots.txt"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // allow static assets & public paths
  if (
    pathname.startsWith("/_next") ||
    PUBLIC_PATHS.includes(pathname)
  ) {
    return NextResponse.next();
  }

  // check auth cookie
  const authed = req.cookies.get("scla_auth")?.value === "1";
  if (authed) {
    return NextResponse.next();
  }

  // redirect to login if not authed
  const url = req.nextUrl.clone();
  url.pathname = "/login";
  return NextResponse.redirect(url);
}

// apply middleware to all routes except assets
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
