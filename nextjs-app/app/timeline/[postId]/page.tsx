'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface AgentLog {
  id: number;
  agent: string;
  input: string;
  output: string;
  timestamp: string;
  metadata: any;
}

interface Post {
  id: number;
  prd: string;
  final_post: string;
}

interface TimelineData {
  post: Post;
  logs: AgentLog[];
  groupedLogs: Array<{
    agent: string;
    logs: AgentLog[];
    iteration?: number;
  }>;
  warning?: string;
}

export default function TimelinePage() {
  const params = useParams();
  const postId = params.postId as string;
  const [data, setData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function fetchTimeline() {
      try {
        const response = await fetch(`/api/timeline/${postId}`);
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `Failed to fetch timeline data (${response.status})`);
        }
        const timelineData = await response.json();
        setData(timelineData);
        // Auto-expand all sections initially
        setExpandedSections(new Set(timelineData.logs.map((log: AgentLog) => log.id.toString())));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    if (postId) {
      fetchTimeline();
    }
  }, [postId]);

  const toggleSection = (id: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const truncateText = (text: string, maxLength: number = 500) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const parseResearchOutput = (output: string) => {
    try {
      const parsed = JSON.parse(output);
      return parsed;
    } catch {
      return null;
    }
  };

  const parseFactCheckOutput = (output: string, metadata: any) => {
    const issues = metadata?.issues || [];
    const status = metadata?.status || 'unknown';
    const verificationSummary = metadata?.verification_summary || '';
    return { issues, status, verificationSummary };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading timeline...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400">Error: {error || 'Failed to load timeline'}</p>
        </div>
      </div>
    );
  }

  const { post, logs, warning } = data;

  // Group logs by agent type for better display
  const researcherLogs = logs.filter(log => log.agent === 'researcher');
  const writerLogs = logs.filter(log => log.agent === 'writer');
  const factCheckerLogs = logs.filter(log => log.agent === 'fact_checker');
  const polisherLogs = logs.filter(log => log.agent === 'polisher');

  return (
    <div className="min-h-screen bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="mb-4">
            <Link 
              href="/posts" 
              className="text-blue-400 hover:text-blue-300 transition-colors inline-flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Posts
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Content Generation Timeline
          </h1>
          <p className="text-gray-400">
            Post ID: {postId}
          </p>
        </div>

        {/* PRD Section */}
        <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white flex items-center">
              <span className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                0
              </span>
              Product Requirements Document (PRD)
            </h2>
            <button
              onClick={() => toggleSection('prd')}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              {expandedSections.has('prd') ? 'Collapse' : 'Expand'}
            </button>
          </div>
          {expandedSections.has('prd') && (
            <div className="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm text-gray-200 font-mono">
                {post.prd}
              </pre>
            </div>
          )}
        </div>

        {/* Warning Message */}
        {warning && (
          <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-200">
              Warning: {warning}
            </p>
          </div>
        )}

        {/* Timeline */}
        {logs.length === 0 ? (
          <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-8 text-center">
            <p className="text-gray-400">
              No agent logs found for this post. The logs may not be linked to this post, or the workflow may not have completed.
            </p>
          </div>
        ) : (
        <div className="space-y-6">
          {/* Step 1: Researcher */}
          {researcherLogs.map((log, idx) => {
            const researchData = parseResearchOutput(log.output);
            const isExpanded = expandedSections.has(log.id.toString());
            
            return (
              <div key={log.id} className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                      {idx + 1}
                    </div>
                    <div className="w-0.5 h-full bg-gray-700 mx-auto mt-2" style={{ minHeight: '40px' }}></div>
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        Researcher Output
                      </h3>
                      <span className="text-xs text-gray-400">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                    {researchData ? (
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-medium text-gray-300 mb-2">
                            Findings: {researchData.findings?.length || 0}
                          </p>
                          {isExpanded ? (
                            <div className="space-y-2">
                              {researchData.findings?.slice(0, 10).map((finding: any, i: number) => (
                                <div key={i} className="p-3 bg-gray-800 border border-gray-700 rounded">
                                  <p className="font-medium text-sm text-white">{finding.title}</p>
                                  <p className="text-sm text-gray-400 mt-1">{finding.snippet}</p>
                                  {finding.source && (
                                    <a href={finding.source} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300 mt-1 block">
                                      {finding.source}
                                    </a>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-400">
                              {researchData.key_points?.slice(0, 3).join(' • ') || 'No key points available'}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => toggleSection(log.id.toString())}
                          className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          {isExpanded ? 'Show less' : 'Show all findings'}
                        </button>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-400">{log.output}</p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Step 2: Writer (with iterations) */}
          {writerLogs.map((log, idx) => {
            const iteration = idx + 1;
            const isExpanded = expandedSections.has(log.id.toString());
            const wordCount = log.output.split(/\s+/).length;
            
            return (
              <div key={log.id} className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                      {researcherLogs.length + idx + 1}
                    </div>
                    {idx < writerLogs.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-700 mx-auto mt-2" style={{ minHeight: '40px' }}></div>
                    )}
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        Writer Draft {writerLogs.length > 1 && `(Iteration ${iteration})`}
                      </h3>
                      <span className="text-xs text-gray-400">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mb-3">
                      {wordCount} words
                    </p>
                    <div className="p-4 bg-gray-800 border border-gray-700 rounded-lg">
                      {isExpanded ? (
                        <p className="text-sm text-gray-200 whitespace-pre-wrap">
                          {log.output}
                        </p>
                      ) : (
                        <p className="text-sm text-gray-200">
                          {truncateText(log.output, 300)}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => toggleSection(log.id.toString())}
                      className="mt-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      {isExpanded ? 'Show less' : 'Show full draft'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Step 3: Fact Checker (with iterations) */}
          {factCheckerLogs.map((log, idx) => {
            const iteration = idx + 1;
            const isExpanded = expandedSections.has(log.id.toString());
            const factCheckData = parseFactCheckOutput(log.output, log.metadata);
            const status = factCheckData.status;
            const isPass = status === 'pass';
            
            return (
              <div key={log.id} className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className={`w-10 h-10 ${isPass ? 'bg-green-600' : 'bg-red-600'} rounded-full flex items-center justify-center text-white font-bold`}>
                      {researcherLogs.length + writerLogs.length + idx + 1}
                    </div>
                    {idx < factCheckerLogs.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-700 mx-auto mt-2" style={{ minHeight: '40px' }}></div>
                    )}
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        Fact-Checker Result {factCheckerLogs.length > 1 && `(Iteration ${iteration})`}
                      </h3>
                      <span className="text-xs text-gray-400">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-3 ${
                      isPass 
                        ? 'bg-green-600 text-white' 
                        : 'bg-red-600 text-white'
                    }`}>
                      {isPass ? '✓ Passed' : '✗ Failed'}
                    </div>
                    {factCheckData.issues.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-gray-300 mb-2">
                          Issues Found: {factCheckData.issues.length}
                        </p>
                        {isExpanded && (
                          <div className="space-y-2">
                            {factCheckData.issues.map((issue: any, i: number) => (
                              <div key={i} className="p-3 bg-yellow-900/30 rounded border border-yellow-700">
                                <p className="text-sm text-gray-200">
                                  {typeof issue === 'string' ? issue : issue.description || JSON.stringify(issue)}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                        <button
                          onClick={() => toggleSection(log.id.toString())}
                          className="mt-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          {isExpanded ? 'Hide issues' : 'Show all issues'}
                        </button>
                      </div>
                    )}
                    {factCheckData.verificationSummary && (
                      <div className="mt-3 p-3 bg-gray-800 border border-gray-700 rounded">
                        <p className="text-sm text-gray-200">
                          {factCheckData.verificationSummary}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Step 4: Polisher */}
          {polisherLogs.map((log, idx) => {
            const isExpanded = expandedSections.has(log.id.toString());
            const wordCount = log.output.split(/\s+/).length;
            
            return (
              <div key={log.id} className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                      {researcherLogs.length + writerLogs.length + factCheckerLogs.length + idx + 1}
                    </div>
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        Style-Polisher Output
                      </h3>
                      <span className="text-xs text-gray-400">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mb-3">
                      {wordCount} words
                    </p>
                    <div className="p-4 bg-gray-800 border border-gray-700 rounded-lg">
                      {isExpanded ? (
                        <p className="text-sm text-gray-200 whitespace-pre-wrap">
                          {log.output}
                        </p>
                      ) : (
                        <p className="text-sm text-gray-200">
                          {truncateText(log.output, 300)}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => toggleSection(log.id.toString())}
                      className="mt-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      {isExpanded ? 'Show less' : 'Show full polished post'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Final Post */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-6 mt-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white flex items-center">
                <span className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                  ✓
                </span>
                Final Polished Blog Post
              </h2>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => copyToClipboard(post.final_post)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 text-white text-sm rounded-md transition-colors flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Copied!
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
                <button
                  onClick={() => toggleSection('final')}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  {expandedSections.has('final') ? 'Collapse' : 'Expand'}
                </button>
              </div>
            </div>
            {expandedSections.has('final') && (
              <div className="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
                <p className="text-sm text-gray-200 whitespace-pre-wrap">
                  {post.final_post}
                </p>
              </div>
            )}
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
