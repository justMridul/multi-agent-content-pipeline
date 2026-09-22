'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface PostPreview {
  id: number;
  prd_preview: string;
  final_post_preview: string;
  prd_length: number;
  final_post_length: number;
}

export default function PostsPage() {
  const [posts, setPosts] = useState<PostPreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPosts() {
      try {
        const response = await fetch('/api/posts');
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        const data = await response.json();
        setPosts(data.posts || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    fetchPosts();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading posts...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link 
            href="/" 
            className="text-blue-400 hover:text-blue-300 mb-4 inline-block transition-colors"
          >
            ← Back to Home
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">
            Generated Posts
          </h1>
          <p className="text-gray-400">
            View timeline for any post to see the complete generation process
          </p>
        </div>

        {posts.length === 0 ? (
          <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-8 text-center">
            <p className="text-gray-400">
              No posts found. Generate some content first!
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((post) => (
              <Link
                key={post.id}
                href={`/timeline/${post.id}`}
                className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6 hover:border-blue-500 transition-colors"
              >
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Post #{post.id}
                  </h3>
                  <div className="flex gap-4 text-sm text-gray-400 mb-4">
                    <span>PRD: {post.prd_length} chars</span>
                    <span>Post: {post.final_post_length} chars</span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs font-medium text-gray-400 uppercase mb-1">
                      PRD Preview
                    </p>
                    <p className="text-sm text-gray-300 line-clamp-3">
                      {post.prd_preview}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-400 uppercase mb-1">
                      Final Post Preview
                    </p>
                    <p className="text-sm text-gray-300 line-clamp-3">
                      {post.final_post_preview}
                    </p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-700">
                  <span className="text-blue-400 text-sm font-medium">
                    View Timeline →
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

