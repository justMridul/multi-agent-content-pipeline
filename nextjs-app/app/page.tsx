import Link from "next/link";
import { 
  Bot, 
  BookOpen, 
  Sparkles, 
  Search, 
  PenTool, 
  CheckCircle2, 
  Wand2, 
  ArrowRight, 
  Terminal 
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      
      {/* Top Header / Brand Bar */}
      <header className="w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between text-xs font-semibold tracking-wider text-slate-400">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Bot className="w-4 h-4" />
            </div>
            <span className="text-slate-100 font-bold text-sm tracking-normal">
              Multi-Agent Content Pipeline
            </span>
          </div>
          <span className="text-slate-400 font-mono text-[10px] bg-slate-800 border border-slate-700/80 px-2 py-0.5 rounded">
            v1.0.0
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-16 flex-1 flex flex-col items-center justify-center text-center">
        
        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs text-slate-300 font-medium mb-6 shadow-sm">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          Autonomous Multi-Agent System
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-white max-w-2xl leading-tight mb-4">
          Multi-Agent Content Pipeline
        </h1>

        {/* Hero Subtitle */}
        <p className="text-base sm:text-lg text-slate-300 max-w-2xl font-normal leading-relaxed mb-3">
          AI-powered content generation using a structured multi-agent workflow with web research, 
          automated drafting, fact-checking, and style polishing.
        </p>

        <p className="text-xs text-slate-400 max-w-lg mb-10">
          🔒 Live demo is password protected. Ask the project owner for credentials to log in.
        </p>

        {/* Action Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl mb-14">
          
          {/* Card 1: View Posts */}
          <Link 
            href="/posts"
            className="group p-6 rounded-xl bg-slate-800/60 border border-slate-700/70 hover:border-blue-500/80 transition-all duration-200 text-left hover:bg-slate-800 flex flex-col justify-between shadow-sm hover:shadow-md"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-slate-700/60 border border-slate-600/60 flex items-center justify-center text-slate-200 mb-5 group-hover:text-blue-400 transition-colors">
                <BookOpen className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-300 transition-colors">
                View Generated Posts
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed mb-6">
                Browse previously generated blog posts and view their live execution timelines.
              </p>
            </div>
            <div className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-400 group-hover:text-blue-300">
              Browse Library <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Card 2: Generate Content */}
          <Link 
            href="/generate"
            className="group p-6 rounded-xl bg-slate-800/60 border border-slate-700/70 hover:border-blue-500/80 transition-all duration-200 text-left hover:bg-slate-800 flex flex-col justify-between shadow-sm hover:shadow-md"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-slate-700/60 border border-slate-600/60 flex items-center justify-center text-slate-200 mb-5 group-hover:text-blue-400 transition-colors">
                <Sparkles className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-300 transition-colors">
                Generate Content
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed mb-6">
                Create a new blog post draft from a Product Requirements Document (PRD).
              </p>
            </div>
            <div className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-400 group-hover:text-blue-300">
              Launch Workflow <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

        </div>

        {/* Pipeline Architecture Row */}
        <div className="w-full max-w-2xl border-t border-slate-800 pt-8">
          <h3 className="text-[11px] uppercase tracking-wider font-semibold text-slate-400 mb-5 text-center">
            Workflow Stages
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left">
            
            <div className="p-3.5 rounded-lg bg-slate-800/40 border border-slate-700/50 flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-slate-300 text-xs font-mono font-semibold">
                <Search className="w-3.5 h-3.5 text-blue-400" />
                <span>01. Research</span>
              </div>
              <div className="text-[11px] text-slate-400">Live web citation gathering</div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-800/40 border border-slate-700/50 flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-slate-300 text-xs font-mono font-semibold">
                <PenTool className="w-3.5 h-3.5 text-blue-400" />
                <span>02. Writer</span>
              </div>
              <div className="text-[11px] text-slate-400">PRD-driven draft generation</div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-800/40 border border-slate-700/50 flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-slate-300 text-xs font-mono font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                <span>03. Fact-Check</span>
              </div>
              <div className="text-[11px] text-slate-400">Source verification check</div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-800/40 border border-slate-700/50 flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-slate-300 text-xs font-mono font-semibold">
                <Wand2 className="w-3.5 h-3.5 text-blue-400" />
                <span>04. Polisher</span>
              </div>
              <div className="text-[11px] text-slate-400">Tone & style refinement</div>
            </div>

          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800 py-5 text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between max-w-5xl mx-auto px-6 gap-3">
        <div>
          Multi-Agent Content Pipeline &copy; {new Date().getFullYear()}
        </div>
        <div className="inline-flex items-center gap-2 font-mono text-xs text-slate-400">
          <Terminal className="w-3.5 h-3.5 text-slate-400" />
          <span>API:</span>
          <code className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200">
            POST /api/generate
          </code>
        </div>
      </footer>

    </div>
  );
}