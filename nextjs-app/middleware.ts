import { NextRequest, NextResponse } from 'next/server';

// Paths that require demo authentication
const PROTECTED_PATHS = [
  '/generate',
  '/posts',
  '/timeline',
  '/api/generate',
  '/api/posts',
  '/api/timeline',
];

function isProtectedPath(pathname: string) {
  return PROTECTED_PATHS.some(
    (base) => pathname === base || pathname.startsWith(`${base}/`)
  );
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow login page and login API without auth, plus static assets
  if (
    pathname === '/login' ||
    pathname.startsWith('/api/login') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/favicon') ||
    pathname === '/'
  ) {
    return NextResponse.next();
  }

  if (!isProtectedPath(pathname)) {
    return NextResponse.next();
  }

  const authCookie = request.cookies.get('demo_auth');

  if (!authCookie || authCookie.value !== '1') {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.searchParams.set('from', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/generate/:path*',
    '/posts/:path*',
    '/timeline/:path*',
    '/api/generate/:path*',
    '/api/posts/:path*',
    '/api/timeline/:path*',
    '/login',
  ],
};
