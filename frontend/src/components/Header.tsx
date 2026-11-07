import React from 'react';
import { 
  Building2, Users, FileText, Shield, Layers, Video, 
  Globe2, Sparkles 
} from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  portalMode: 'customer' | 'partner';
  setPortalMode: (mode: 'customer' | 'partner') => void;
  language: string;
  setLanguage: (lang: string) => void;
  onOpenModal: (modal: 'architecture' | 'business_case' | 'privacy' | 'script') => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  portalMode,
  setPortalMode,
  language,
  setLanguage,
  onOpenModal
}) => {
  return (
    <header className="sticky top-0 z-50 bg-slate-900 border-b border-slate-800 text-white shadow-lg">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/60 text-xs">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-semibold bg-red-600/20 text-red-400 border border-red-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
            Airtel SYNC 2026
          </span>
          <span className="text-slate-400 hidden sm:inline">|</span>
          <span className="text-slate-300 font-medium">YTL Hackathon Enterprise Track A</span>
          <span className="text-slate-400 hidden md:inline">· Accel Business</span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px]" title="Zero production credentials required for hackathon review. Evaluates RBAC without blocking demo exploration.">
            <Shield className="w-3 h-3 text-amber-400" />
            <span>Simulated Multi-Role Sandbox (No Prod Auth Required)</span>
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Submission Deliverable Links */}
          <button 
            onClick={() => onOpenModal('architecture')}
            className="flex items-center gap-1 text-slate-300 hover:text-white hover:underline transition-colors cursor-pointer"
          >
            <Layers className="w-3.5 h-3.5 text-red-400" />
            <span className="hidden md:inline">Architecture</span>
          </button>
          <button 
            onClick={() => onOpenModal('business_case')}
            className="flex items-center gap-1 text-slate-300 hover:text-white hover:underline transition-colors cursor-pointer"
          >
            <FileText className="w-3.5 h-3.5 text-amber-400" />
            <span>Business Case (10 Slides)</span>
          </button>
          <button 
            onClick={() => onOpenModal('privacy')}
            className="flex items-center gap-1 text-slate-300 hover:text-white hover:underline transition-colors cursor-pointer"
          >
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden md:inline">DPDP Privacy</span>
          </button>
          <button 
            onClick={() => onOpenModal('script')}
            className="flex items-center gap-1 text-slate-300 hover:text-white hover:underline transition-colors cursor-pointer"
          >
            <Video className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">3-Min Pitch</span>
          </button>

          {/* Language Selector */}
          <div className="flex items-center gap-1 bg-slate-800 border border-slate-700 rounded-lg px-2 py-1">
            <Globe2 className="w-3.5 h-3.5 text-slate-400" />
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="en" className="bg-slate-900 text-white">English</option>
              <option value="hi" className="bg-slate-900 text-white">हिंदी (Hindi)</option>
              <option value="ta" className="bg-slate-900 text-white">தமிழ் (Tamil)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center font-black text-xl tracking-tighter text-white shadow-md shadow-red-900/40">
            U1
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight text-white">UdyamOne</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-red-600 text-white">
                Accel Business
              </span>
            </div>
            <p className="text-[11px] text-slate-400">One Conversation. One Smart Bundle. One Connected Business.</p>
          </div>
        </div>

        {/* Portal Switcher & Navigation Tabs */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Mode Switcher */}
          <div className="bg-slate-800 p-1 rounded-xl flex items-center gap-1 border border-slate-700">
            <button
              onClick={() => { setPortalMode('customer'); setActiveTab('advisor'); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                portalMode === 'customer'
                  ? 'bg-red-600 text-white shadow'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>MSME Portal</span>
            </button>
            <button
              onClick={() => { setPortalMode('partner'); setActiveTab('partner'); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                portalMode === 'partner'
                  ? 'bg-red-600 text-white shadow'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Partner Command</span>
            </button>
          </div>

          {/* Portal Tabs */}
          <nav className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-xl border border-slate-700/80">
            {portalMode === 'customer' ? (
              <>
                <button
                  onClick={() => setActiveTab('advisor')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'advisor' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  <span className="flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-red-400" />
                    AI Advisor
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('bundle')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'bundle' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Smart Quote
                </button>
                <button
                  onClick={() => setActiveTab('kyc')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'kyc' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Digital KYC
                </button>
                <button
                  onClick={() => setActiveTab('tracker')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'tracker' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Order Tracker
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setActiveTab('partner')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'partner' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Lead Funnel
                </button>
                <button
                  onClick={() => setActiveTab('intelligence')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'intelligence' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Predictive ML
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'analytics' ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Executive BI
                </button>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

