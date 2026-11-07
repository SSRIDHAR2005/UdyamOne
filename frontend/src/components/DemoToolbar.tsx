import React from 'react';
import { PlayCircle, ShieldAlert, CheckCircle2, RotateCcw, FastForward, Info } from 'lucide-react';

interface DemoToolbarProps {
  onSelectScenario: (scenarioId: string) => void;
  onSelectKycCase: (caseId: string) => void;
  onAdvanceOrderStage: () => void;
  onReset: () => void;
  currentScenario?: string;
  currentKycCase?: string;
}

export const DemoToolbar: React.FC<DemoToolbarProps> = ({
  onSelectScenario,
  onSelectKycCase,
  onAdvanceOrderStage,
  onReset,
  currentScenario,
  currentKycCase
}) => {
  return (
    <div className="bg-gradient-to-r from-red-950 via-slate-900 to-slate-900 border-b border-red-900/50 px-4 py-2 text-white shadow-inner">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: Indicator */}
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
          </span>
          <span className="font-bold uppercase tracking-wider text-red-300 flex items-center gap-1">
            <PlayCircle className="w-3.5 h-3.5 text-red-400" />
            Judge Demo Mode
          </span>
          <span className="text-slate-400 hidden lg:inline">| Select 1-click MSME Persona or KYC Edge Case:</span>
        </div>

        {/* Middle: Scenarios & KYC cases */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Persona selector */}
          <div className="flex items-center gap-1 bg-slate-800/80 p-0.5 rounded-lg border border-slate-700">
            <button
              onClick={() => onSelectScenario('scenario-kirana')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-all ${
                currentScenario === 'scenario-kirana' ? 'bg-red-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
              title="Micro Retail: Low budget, UPI/POS, WhatsApp, No GSTIN"
            >
              Kirana (Micro)
            </button>
            <button
              onClick={() => onSelectScenario('scenario-clinic')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-all ${
                currentScenario === 'scenario-clinic' ? 'bg-red-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
              title="Professional Office: High uptime, Cloud email, Security"
            >
              Clinic (Prof)
            </button>
            <button
              onClick={() => onSelectScenario('scenario-restaurant')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-all ${
                currentScenario === 'scenario-restaurant' ? 'bg-red-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
              title="Multi-site Restaurant: 3 outlets, Failover backup, CCTV"
            >
              3-Site Restaurant
            </button>
            <button
              onClick={() => onSelectScenario('scenario-manufacturer')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-all ${
                currentScenario === 'scenario-manufacturer' ? 'bg-red-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
              title="Manufacturer: Dedicated Leased Line, IoT sensors, Firewall"
            >
              Auto Mfg (Leased Line)
            </button>
          </div>

          {/* KYC Planted Cases */}
          <div className="flex items-center gap-1 bg-slate-800/80 p-0.5 rounded-lg border border-slate-700">
            <span className="text-[10px] text-slate-400 px-1 font-semibold uppercase">KYC Specimen:</span>
            <button
              onClick={() => onSelectKycCase('K02')}
              className={`px-2 py-1 rounded text-[11px] font-semibold flex items-center gap-1 transition-all ${
                currentKycCase === 'K02' ? 'bg-emerald-600 text-white' : 'text-emerald-400 hover:bg-emerald-950/40'
              }`}
              title="K02 Harmony Dental: Clean Valid Case (Active GSTIN, Valid Udyam, Valid Bill)"
            >
              <CheckCircle2 className="w-3 h-3" />
              K02 (Valid)
            </button>
            <button
              onClick={() => onSelectKycCase('K01')}
              className={`px-2 py-1 rounded text-[11px] font-semibold flex items-center gap-1 transition-all ${
                currentKycCase === 'K01' ? 'bg-red-600 text-white' : 'text-red-400 hover:bg-red-950/40'
              }`}
              title="K01 Vindhya Tours: Planted Cancelled GSTIN in Registry"
            >
              <ShieldAlert className="w-3 h-3" />
              K01 (Cancelled GST)
            </button>
            <button
              onClick={() => onSelectKycCase('K07')}
              className={`px-2 py-1 rounded text-[11px] font-semibold flex items-center gap-1 transition-all ${
                currentKycCase === 'K07' ? 'bg-amber-600 text-white' : 'text-amber-400 hover:bg-amber-950/40'
              }`}
              title="K07 Neelgiri Clinic: Planted Name Mismatch (Legal Shri Physio vs Trade Neelgiri Physio)"
            >
              K07 (Name Mismatch)
            </button>
            <button
              onClick={() => onSelectKycCase('K11')}
              className={`px-2 py-1 rounded text-[11px] font-semibold flex items-center gap-1 transition-all ${
                currentKycCase === 'K11' ? 'bg-amber-600 text-white' : 'text-amber-400 hover:bg-amber-950/40'
              }`}
              title="K11 Trinity Bake House: Planted Expired Bill (257 days old > 90d)"
            >
              K11 (Expired Bill)
            </button>
          </div>
        </div>

        {/* Right: Stage Advance & Reset */}
        <div className="flex items-center gap-2">
          <button
            onClick={onAdvanceOrderStage}
            className="flex items-center gap-1 bg-red-600/80 hover:bg-red-600 text-white px-2.5 py-1 rounded-md font-semibold transition-all cursor-pointer shadow-sm"
            title="Fast-forward order activation lifecycle through all 7 stages"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>Advance Order</span>
          </button>
          <button
            onClick={onReset}
            className="flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-2.5 py-1 rounded-md font-medium transition-all cursor-pointer border border-slate-700"
            title="Reset form to defaults"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>
    </div>
  );
};

