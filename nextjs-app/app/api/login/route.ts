import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const { password } = body as { password?: string };

    const demoPassword = process.env.DEMO_PASSWORD;

    // If no DEMO_PASSWORD is set, treat demo auth as disabled (allow access)
    if (!demoPassword) {
      const res = NextResponse.json({ ok: true, demoPasswordConfigured: false });
      res.cookies.set('demo_auth', '1', {
        httpOnly: true,
        secure: true,
        sameSite: 'lax',
        path: '/',
        maxAge: 60 * 60 * 12, // 12 hours
      });
      return res;
    }

    if (!password || password !== demoPassword) {
      return NextResponse.json(
        { error: 'Invalid password' },
        { status: 401 }
      );
    }

    const res = NextResponse.json({ ok: true, demoPasswordConfigured: true });
    res.cookies.set('demo_auth', '1', {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 12, // 12 hours
    });
    return res;
  } catch (error) {
    console.error('Error in /api/login:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}