import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// For API routes (server-side), prefer SUPABASE_KEY (secret key) over NEXT_PUBLIC_* (anon key)
// This ensures we have full access to read posts and logs
const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_KEY;

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;
    
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      console.error('Supabase credentials missing:', {
        hasUrl: !!SUPABASE_URL,
        hasKey: !!SUPABASE_KEY,
        envPublicUrl: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
        envUrl: !!process.env.SUPABASE_URL,
        envPublicKey: !!process.env.NEXT_PUBLIC_SUPABASE_KEY,
        envKey: !!process.env.SUPABASE_KEY
      });
      return NextResponse.json(
        { error: 'Supabase credentials not configured', debug: {
          hasUrl: !!SUPABASE_URL,
          hasKey: !!SUPABASE_KEY
        }},
        { status: 500 }
      );
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

    // Convert postId to number for proper comparison
    const postIdNum = parseInt(postId, 10);
    if (isNaN(postIdNum)) {
      return NextResponse.json(
        { error: 'Invalid post ID format', received: postId },
        { status: 400 }
      );
    }

    console.log('Fetching post:', { postId, postIdNum, supabaseUrl: SUPABASE_URL?.substring(0, 30) });

    // First, let's check if ANY posts exist
    const { data: allPosts, error: allPostsError } = await supabase
      .from('posts')
      .select('id')
      .limit(5);
    
    console.log('All posts check:', { 
      count: allPosts?.length, 
      ids: allPosts?.map(p => p.id),
      error: allPostsError?.message 
    });

    // Fetch the post
    const { data: post, error: postError } = await supabase
      .from('posts')
      .select('*')
      .eq('id', postIdNum)
      .single();

    console.log('Post fetch result:', { 
      found: !!post, 
      postId: post?.id,
      error: postError?.message,
      errorCode: postError?.code,
      errorDetails: postError
    });

    if (postError || !post) {
      return NextResponse.json(
        { 
          error: 'Post not found', 
          details: postError?.message,
          code: postError?.code,
          requestedId: postIdNum,
          availableIds: allPosts?.map(p => p.id),
          debug: {
            hasUrl: !!SUPABASE_URL,
            hasKey: !!SUPABASE_KEY,
            keyType: SUPABASE_KEY?.substring(0, 10) // Show first 10 chars to identify key type
          }
        },
        { status: 404 }
      );
    }

    // Fetch agent_logs for this specific post using post_id
    // postIdNum already defined above
    const { data: relatedLogs, error: logsError } = await supabase
      .from('agent_logs')
      .select('*')
      .eq('post_id', postIdNum)
      .order('timestamp', { ascending: true });

    if (logsError) {
      console.error('Agent logs fetch error:', logsError);
      return NextResponse.json(
        { error: 'Failed to fetch agent logs', details: logsError?.message },
        { status: 500 }
      );
    }

    // If no logs found, return empty array (might be an old post before post_id was added)
    if (!relatedLogs || relatedLogs.length === 0) {
      return NextResponse.json({
        post,
        logs: [],
        groupedLogs: [],
        warning: 'No agent logs found for this post. This may be an older post created before post_id linking was implemented.'
      });
    }

    // Sort by timestamp and group by agent type
    const sortedLogs = relatedLogs.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // Group consecutive logs by the same agent (for iterations)
    const groupedLogs: Array<{
      agent: string;
      logs: typeof sortedLogs;
      iteration?: number;
    }> = [];
    
    let currentGroup: typeof sortedLogs = [];
    let currentAgent = '';
    
    sortedLogs.forEach((log, index) => {
      if (log.agent !== currentAgent && currentGroup.length > 0) {
        groupedLogs.push({
          agent: currentAgent,
          logs: [...currentGroup],
          iteration: currentAgent === 'fact_checker' || currentAgent === 'writer' ? groupedLogs.filter(g => g.agent === currentAgent).length + 1 : undefined
        });
        currentGroup = [];
      }
      currentAgent = log.agent;
      currentGroup.push(log);
    });
    
    if (currentGroup.length > 0) {
      groupedLogs.push({
        agent: currentAgent,
        logs: [...currentGroup],
        iteration: currentAgent === 'fact_checker' || currentAgent === 'writer' ? groupedLogs.filter(g => g.agent === currentAgent).length + 1 : undefined
      });
    }

    return NextResponse.json({
      post,
      logs: sortedLogs,
      groupedLogs
    });
  } catch (error) {
    console.error('Error fetching timeline:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

