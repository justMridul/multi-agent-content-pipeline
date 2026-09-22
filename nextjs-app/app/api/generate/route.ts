import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prd, topic, target_length, style } = body;

    if (!prd || !topic) {
      return NextResponse.json(
        { error: 'PRD and topic are required' },
        { status: 400 }
      );
    }

    // Ensure FASTAPI_URL doesn't have trailing slash
    const apiUrl = FASTAPI_URL.replace(/\/$/, '');
    const generateUrl = `${apiUrl}/generate`;

    // Call the Python FastAPI server
    const response = await fetch(generateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prd,
        topic,
        target_length,
        style,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('FastAPI error:', {
        url: generateUrl,
        status: response.status,
        error: error
      });
      return NextResponse.json(
        { error: `FastAPI server error: ${error}`, url: generateUrl },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error calling FastAPI server:', error);
    return NextResponse.json(
      { error: 'Failed to connect to FastAPI server' },
      { status: 500 }
    );
  }
}

export async function GET() {
  // Ensure FASTAPI_URL doesn't have trailing slash
  const apiUrl = FASTAPI_URL.replace(/\/$/, '');
  return NextResponse.json({ 
    message: 'Generate endpoint - use POST to generate content',
    fastapi_url: apiUrl,
    env_fastapi_url: process.env.FASTAPI_URL,
    generate_url: `${apiUrl}/generate`
  });
}

