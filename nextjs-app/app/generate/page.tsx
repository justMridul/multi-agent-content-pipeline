'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function GeneratePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    prd: '',
    topic: '',
    target_length: 1000,
    style: 'professional'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [postId, setPostId] = useState<number | null>(null);

  // Preset loader helper
  const handleLoadSample = (sampleTopic: string, samplePrd: string) => {
    setFormData(prev => ({
      ...prev,
      topic: sampleTopic,
      prd: samplePrd
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPostId(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate content');
      }

      // Get post_id from metadata (added by FastAPI backend)
      const postIdFromResponse = data.metadata?.post_id;
      
      if (postIdFromResponse) {
        setPostId(postIdFromResponse);
        // Redirect to timeline after a short delay
        setTimeout(() => {
          router.push(`/timeline/${postIdFromResponse}`);
        }, 2000);
      } else {
        // Fallback: try to get the latest post
        const postsResponse = await fetch('/api/posts');
        const postsData = await postsResponse.json();
        
        if (postsData.posts && postsData.posts.length > 0) {
          const latestPostId = postsData.posts[0].id;
          setPostId(latestPostId);
          setTimeout(() => {
            router.push(`/timeline/${latestPostId}`);
          }, 2000);
        } else {
          throw new Error('Content generated but post ID not found');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'target_length' ? parseInt(value, 10) : value
    }));
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      
      {/* Top Header Bar */}
      <header className="w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link 
            href="/" 
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <span>&larr;</span> Back to Home
          </Link>
          <div className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2.5 py-1 rounded border border-slate-700/60">
            Pipeline OS / Generator
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-3xl mx-auto px-6 py-12 flex-1 w-full">
        
        {/* Title & Description */}
        <div className="mb-8 text-left">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-2">
            Generate Blog Post
          </h1>
          <p className="text-sm sm:text-base text-slate-300">
            Enter a Product Requirements Document (PRD) and topic to generate a polished blog post.
          </p>
        </div>

        {/* Quick Sample Presets */}
        <div className="mb-6 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-medium text-slate-400">Try a sample template:</span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleLoadSample('Star Wars Lore', 'Anakin Skywalker, his tragic downfall to the Dark Side, and eventual redemption.')}
              className="px-2.5 py-1 text-xs rounded bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              Star Wars Lore
            </button>
            <button
              type="button"
              onClick={() => handleLoadSample('AI Agent Workflows', 'An overview of autonomous LangGraph multi-agent pipelines for engineering teams.')}
              className="px-2.5 py-1 text-xs rounded bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              SaaS PRD
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-950/60 border border-red-800/80 rounded-lg p-4 flex items-center justify-between text-left">
            <p className="text-red-300 text-sm">{error}</p>
            <button onClick={() => setError(null)} className="text-xs text-red-400 hover:underline">Dismiss</button>
          </div>
        )}

        {/* Success Banner */}
        {postId && (
          <div className="mb-6 bg-emerald-950/60 border border-emerald-800/80 rounded-lg p-4 text-left">
            <p className="text-emerald-300 text-sm mb-2 font-medium">
              ✅ Content generated successfully! Redirecting to timeline...
            </p>
            <Link 
              href={`/timeline/${postId}`}
              className="text-emerald-400 hover:text-emerald-300 hover:underline text-xs font-semibold transition-colors"
            >
              View Timeline &rarr;
            </Link>
          </div>
        )}

        {/* Main Form */}
        <form onSubmit={handleSubmit} className="bg-slate-800/60 border border-slate-700/70 rounded-xl shadow-sm p-6 sm:p-8 space-y-6">
          
          {/* PRD Textarea */}
          <div className="text-left">
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="prd" className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Product Requirements Document (PRD) <span className="text-blue-400">*</span>
              </label>
              <span className="text-xs font-mono text-slate-400">
                {formData.prd.length} characters
              </span>
            </div>
            <textarea
              id="prd"
              name="prd"
              rows={10}
              required
              value={formData.prd}
              onChange={handleChange}
              placeholder="Enter your Product Requirements Document here. Include details about features, target audience, benefits, etc."
              className="w-full px-4 py-3 border border-slate-700/80 rounded-lg bg-slate-900 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all resize-y"
            />
          </div>

          {/* Topic Input */}
          <div className="text-left">
            <label htmlFor="topic" className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Topic <span className="text-blue-400">*</span>
            </label>
            <input
              type="text"
              id="topic"
              name="topic"
              required
              value={formData.topic}
              onChange={handleChange}
              placeholder="e.g., AI-Powered Content Generation"
              className="w-full px-4 py-3 border border-slate-700/80 rounded-lg bg-slate-900 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
            />
          </div>

          {/* Grid Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
            <div>
              <label htmlFor="target_length" className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                Target Length (words)
              </label>
              <input
                type="number"
                id="target_length"
                name="target_length"
                min="100"
                max="5000"
                step="100"
                value={formData.target_length}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-slate-700/80 rounded-lg bg-slate-900 text-slate-100 text-sm font-mono focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
            </div>

            <div>
              <label htmlFor="style" className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                Writing Style
              </label>
              <select
                id="style"
                name="style"
                value={formData.style}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-slate-700/80 rounded-lg bg-slate-900 text-slate-100 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all cursor-pointer"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="academic">Academic</option>
                <option value="conversational">Conversational</option>
                <option value="technical">Technical</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 pt-2">
            <button
              type="submit"
              disabled={loading || !formData.prd.trim() || !formData.topic.trim()}
              className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold text-sm py-3 px-6 rounded-lg transition-all shadow-md flex items-center justify-center"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </span>
              ) : (
                'Generate Blog Post'
              )}
            </button>
            <Link
              href="/"
              className="px-6 py-3 border border-slate-700/80 text-slate-300 rounded-lg hover:bg-slate-800 text-sm font-medium transition-colors"
            >
              Cancel
            </Link>
          </div>

          {/* Progress Indicator */}
          {loading && (
            <div className="mt-4 p-4 bg-slate-900/80 border border-slate-700/60 rounded-lg text-left">
              <p className="text-sm text-blue-300 mb-1 font-medium flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
                Generating content... This may take a few moments.
              </p>
              <p className="text-xs text-slate-400">
                Pipeline order: Research &rarr; Writer &rarr; Fact-Checker &rarr; Style-Polisher
              </p>
            </div>
          )}

        </form>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800 py-5 text-xs text-slate-400 text-center max-w-4xl mx-auto px-6">
        Multi-Agent Content Pipeline &copy; {new Date().getFullYear()}
      </footer>

    </div>
  );
}