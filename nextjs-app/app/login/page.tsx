'use client';

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

function LoginForm() {
  const searchParams = useSearchParams();
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        setError((data && data.error) || 'Invalid password');
        setLoading(false);
        return;
      }

      // Get the redirect destination from query params, default to /generate
      const redirectTo = searchParams.get('from') || '/generate';
      
      // Use window.location.href for a full page reload to ensure cookie is recognized
      // Small delay to ensure cookie is set
      setTimeout(() => {
        window.location.href = redirectTo;
      }, 100);
    } catch (err) {
      setError('Something went wrong. Please try again.');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Demo password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border border-gray-600 bg-black px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter demo password"
          required
        />
      </div>

      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60 transition-colors"
      >
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <main className="w-full max-w-md rounded-lg bg-gray-900 border border-gray-700 p-8 shadow-lg">
        <h1 className="mb-4 text-2xl font-semibold text-white text-center">
          Demo Login
        </h1>
        <p className="mb-6 text-sm text-gray-400 text-center">
          This hosted demo is password-protected to prevent abuse of API credits.
          <br />
          Ask the project owner for the demo password.
        </p>

        <Suspense fallback={
          <div className="space-y-4">
            <div className="h-10 bg-gray-800 rounded-md animate-pulse"></div>
            <div className="h-10 bg-gray-800 rounded-md animate-pulse"></div>
          </div>
        }>
          <LoginForm />
        </Suspense>
      </main>
    </div>
  );
}