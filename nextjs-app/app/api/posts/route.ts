import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// For API routes (server-side), prefer SUPABASE_KEY (secret key) over NEXT_PUBLIC_* (anon key)
// This ensures we have full access to read posts and logs
const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_KEY;

export async function GET(request: NextRequest) {
  try {
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      return NextResponse.json(
        { error: 'Supabase credentials not configured' },
        { status: 500 }
      );
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

    console.log('Fetching posts:', { 
      supabaseUrl: SUPABASE_URL?.substring(0, 40),
      hasKey: !!SUPABASE_KEY,
      keyType: SUPABASE_KEY?.substring(0, 15)
    });

    // Fetch all posts
    const { data: posts, error } = await supabase
      .from('posts')
      .select('id, prd, final_post')
      .order('id', { ascending: false })
      .limit(100);

    console.log('Posts fetch result:', {
      count: posts?.length,
      error: error?.message,
      errorCode: error?.code,
      errorDetails: error
    });

    if (error) {
      console.error('Posts fetch error:', error);
      return NextResponse.json(
        { 
          error: 'Failed to fetch posts', 
          details: error.message,
          code: error.code,
          debug: {
            supabaseUrl: SUPABASE_URL?.substring(0, 40),
            hasKey: !!SUPABASE_KEY
          }
        },
        { status: 500 }
      );
    }

    // Return posts with truncated previews
    const postsWithPreview = posts?.map(post => ({
      id: post.id,
      prd_preview: post.prd.substring(0, 200) + (post.prd.length > 200 ? '...' : ''),
      final_post_preview: post.final_post.substring(0, 200) + (post.final_post.length > 200 ? '...' : ''),
      prd_length: post.prd.length,
      final_post_length: post.final_post.length
    })) || [];

    return NextResponse.json({ posts: postsWithPreview });
  } catch (error) {
    console.error('Error fetching posts:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

