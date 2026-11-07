import React, { useState, useEffect } from 'react';
import { 
  Users, Search, Filter, Phone, UserCheck, AlertTriangle, 
  ExternalLink, CheckCircle2, Clock, Sparkles, TrendingUp, ShieldCheck,
  Building2, MapPin, IndianRupee, ArrowRight, CheckCircle, XCircle, Info
} from 'lucide-react';
import type { LeadItem } from '../types';
import { fetchPartnerLeads, logPartnerAction } from '../services/api';

const FUNNEL_STAGES = [
  'Lead',
  'Contacted',
  'Needs assessed',
  'Quote accepted',
  'KYC complete',
  'Activated'
];

export const PartnerTab: React.FC = () => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [selectedLead, setSelectedLead] = useState<LeadItem | null>(null);
  const [actionMessage, setActionMessage] = useState('');

  const loadLeads = async () => {
    setLoading(true);
    try {
      const data = await fetchPartnerLeads({
        segment: segmentFilter || undefined,
        stage: stageFilter || undefined,
        priority: priorityFilter || undefined
      });
      setLeads(data);
      if (data.length > 0 && !selectedLead) {
        setSelectedLead(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, [segmentFilter, stageFilter, priorityFilter]);

  const handleAction = async (actionType: string) => {
    if (!selectedLead) return;
    try {
      const res = await logPartnerAction(selectedLead.lead_id, actionType, 'Field Specialist Rajesh Verma');
      setActionMessage(res.message);
      setTimeout(() => setActionMessage(''), 4000);
    } catch (e) {
      console.error(e);
    }
  };

  const filteredLeads = leads.filter((l) => 
    l.business_name.toLowerCase().includes(search.toLowerCase()) ||
    l.lead_id.toLowerCase().includes(search.toLowerCase()) ||
    l.city.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6">
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 mb-2">
            <Users className="w-3.5 h-3.5 text-red-600" />
            <span>Module 5 · Partner & Sales Operations Command Centre</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Intelligent Field Intervention & Abandonment Recovery
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Empowers local sales partners and field executives with machine-learning prioritized leads, root-cause drop diagnoses, and instant quote recovery.
          </p>
        </div>

        {/* Live Partner Badge */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 bg-slate-900 text-white px-3.5 py-2 rounded-xl text-xs font-semibold border border-slate-800 shadow">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Role: Accel Partner Unit (DEL-01)</span>
          </div>
          <span className="text-[10px] text-amber-300 font-normal border-t sm:border-t-0 sm:border-l border-slate-700 sm:pl-2 pt-1 sm:pt-0">
            Simulated Partner IAM Session · Zero Prod Credentials Required
          </span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-400 uppercase">Total Queue Leads</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{leads.length}</p>
          <span className="text-[10px] text-slate-500">Live operational slice</span>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-400 uppercase">High Priority Propensity</span>
          <p className="text-2xl font-black text-emerald-600 mt-1">
            {leads.filter((l) => l.lead_priority === 'HIGH').length}
          </p>
          <span className="text-[10px] text-emerald-600 font-semibold">Immediate intervention fit</span>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-400 uppercase">Abandoned Quotes</span>
          <p className="text-2xl font-black text-amber-600 mt-1">
            {leads.filter((l) => l.drop_reason && l.drop_reason.includes('Quote')).length}
          </p>
          <span className="text-[10px] text-amber-600">Recovery opportunity</span>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-400 uppercase">Estimated Pipeline MRC</span>
          <p className="text-2xl font-black text-red-600 mt-1">
            ₹{leads.reduce((acc, l) => acc + (l.monthly_telecom_spend_inr || 1500), 0).toLocaleString()}
          </p>
          <span className="text-[10px] text-slate-500">Monthly recurring opportunity</span>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm mb-6 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Business Name, Lead ID, or City..."
            className="w-full px-2 py-1.5 focus:outline-none text-xs"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={segmentFilter}
            onChange={(e) => setSegmentFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none bg-white"
          >
            <option value="">All Segments</option>
            <option value="micro">Micro Retail</option>
            <option value="prof">Professional Offices</option>
            <option value="multi">Multi-site Retail</option>
            <option value="mfg">Small Manufacturing</option>
          </select>

          <select
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none bg-white"
          >
            <option value="">All Stages</option>
            <option value="Lead">Lead</option>
            <option value="Contacted">Contacted</option>
            <option value="Needs assessed">Needs Assessed</option>
            <option value="Quote accepted">Quote Accepted</option>
            <option value="KYC complete">KYC Complete</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none bg-white"
          >
            <option value="">All Priorities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>
        </div>
      </div>

      {/* Priority Classification Legend */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 mb-6 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div className="flex items-start gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mt-1 flex-shrink-0"></span>
          <div>
            <span className="font-bold text-slate-800">HIGH PRIORITY (Score ≥ 55%)</span>
            <p className="text-[10px] text-slate-500">High conversion propensity; immediate automated quote recovery or priority callback.</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 mt-1 flex-shrink-0"></span>
          <div>
            <span className="font-bold text-slate-800">MEDIUM PRIORITY (Score 35–54%)</span>
            <p className="text-[10px] text-slate-500">Assisted conversion; requires tariff walkthrough, add-on customization, or site survey.</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-400 mt-1 flex-shrink-0"></span>
          <div>
            <span className="font-bold text-slate-800">LOW PRIORITY (Score &lt; 35%)</span>
            <p className="text-[10px] text-slate-500">Micro unregistered lead; guide through Udyam registration or digital self-service flow.</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Leads Table + Detail Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leads Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto max-h-[520px]">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold sticky top-0">
                <tr>
                  <th className="p-3">Lead ID & Business</th>
                  <th className="p-3">Segment</th>
                  <th className="p-3">Stage & Drop Reason</th>
                  <th className="p-3">ML Score</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredLeads.map((lead) => {
                  const isSelected = selectedLead?.lead_id === lead.lead_id;
                  return (
                    <tr
                      key={lead.lead_id}
                      onClick={() => setSelectedLead(lead)}
                      className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                        isSelected ? 'bg-red-50/60 font-semibold' : ''
                      }`}
                    >
                      <td className="p-3">
                        <span className="font-mono text-[10px] text-slate-400 block">{lead.lead_id}</span>
                        <span className="font-bold text-slate-900 block">{lead.business_name}</span>
                        <span className="text-[10px] text-slate-500">{lead.city} (Tier {lead.city_tier})</span>
                      </td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-100 text-slate-700">
                          {lead.segment}
                        </span>
                      </td>
                      <td className="p-3 max-w-[180px]">
                        <span className="block font-medium text-slate-800">{lead.stage_reached}</span>
                        {lead.drop_reason && (
                          <span className="text-[10px] text-amber-700 block truncate" title={lead.drop_reason}>
                            ⚠ {lead.drop_reason}
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black ${
                          lead.lead_priority === 'HIGH'
                            ? 'bg-emerald-100 text-emerald-800'
                            : lead.lead_priority === 'MEDIUM'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-slate-100 text-slate-600'
                        }`}>
                          {lead.lead_score}% · {lead.lead_priority}
                        </span>
                      </td>
                      <td className="p-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedLead(lead);
                          }}
                          className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-white text-[10px] font-semibold cursor-pointer"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Lead Detail & Recovery Drawer */}
        <div className="space-y-4">
          {selectedLead ? (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-md p-6 space-y-4 text-xs">
              {/* Header */}
              <div className="flex items-start justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="font-mono text-[10px] text-slate-400">{selectedLead.lead_id}</span>
                  <h3 className="font-bold text-base text-slate-900">{selectedLead.business_name}</h3>
                  <p className="text-slate-500">{selectedLead.business_type} · {selectedLead.city} (Tier {selectedLead.city_tier})</p>
                </div>
                <div className="text-right">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-black inline-block ${
                    selectedLead.lead_priority === 'HIGH'
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      : selectedLead.lead_priority === 'MEDIUM'
                      ? 'bg-amber-100 text-amber-800 border border-amber-300'
                      : 'bg-slate-100 text-slate-700'
                  }`}>
                    {selectedLead.lead_score}% · {selectedLead.lead_priority}
                  </span>
                  <span className="text-[9px] text-slate-400 block mt-0.5">Scikit-learn Model</span>
                </div>
              </div>

              {/* Customer Profile Grid */}
              <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[9px] uppercase font-bold">Segment</span>
                  <span className="font-semibold text-slate-800 uppercase">{selectedLead.segment}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px] uppercase font-bold">GSTIN Status</span>
                  <span className={`font-semibold ${selectedLead.has_gstin ? 'text-emerald-700' : 'text-amber-700'}`}>
                    {selectedLead.has_gstin ? (selectedLead.gstin || 'Registered (4.8x Lift)') : 'Unregistered (Micro)'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px] uppercase font-bold">Current Telecom Spend</span>
                  <span className="font-semibold text-slate-800">₹{(selectedLead.monthly_telecom_spend_inr || 1500).toLocaleString()} / mo</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px] uppercase font-bold">Acquisition Source</span>
                  <span className="font-semibold text-slate-800">{selectedLead.lead_source || 'Inbound Web'}</span>
                </div>
              </div>

              {/* Visual Customer Funnel Journey */}
              <div className="pt-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                  Customer Funnel Journey & Drop Stage
                </span>
                <div className="flex items-center justify-between relative bg-slate-50/70 p-2.5 rounded-xl border border-slate-100">
                  {FUNNEL_STAGES.map((stg, sIdx) => {
                    const currentIdx = FUNNEL_STAGES.findIndex(s => s.toLowerCase() === selectedLead.stage_reached.toLowerCase());
                    const isReached = sIdx <= currentIdx;
                    const isDrop = Boolean(selectedLead.drop_reason && sIdx === currentIdx);
                    
                    return (
                      <div key={stg} className="flex flex-col items-center flex-1 text-center relative z-10">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold ${
                          isDrop 
                            ? 'bg-amber-500 text-white shadow-sm ring-2 ring-amber-200' 
                            : isReached 
                            ? 'bg-emerald-600 text-white' 
                            : 'bg-slate-200 text-slate-500'
                        }`}>
                          {isDrop ? '!' : isReached ? '✓' : sIdx + 1}
                        </div>
                        <span className={`text-[8px] mt-1 line-clamp-1 max-w-[48px] ${
                          isDrop ? 'text-amber-800 font-bold' : isReached ? 'text-slate-700 font-semibold' : 'text-slate-400'
                        }`}>
                          {stg}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Drop-off Details */}
              {selectedLead.drop_reason && (
                <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900">
                  <span className="font-bold block text-[11px] mb-0.5 flex items-center gap-1 text-amber-950">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    Drop-off Bottleneck at {selectedLead.stage_reached}:
                  </span>
                  <p className="text-[11px] text-amber-800">{selectedLead.drop_reason}</p>
                </div>
              )}

              {/* Key Risk & Propensity Drivers */}
              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400 block mb-1.5">
                  Contributing Scoring Drivers (Pre-Conversion Features)
                </span>
                <ul className="space-y-1 text-slate-600">
                  {selectedLead.key_factors.map((f, i) => (
                    <li key={i} className="flex items-start gap-1.5 text-[11px]">
                      <span className="text-red-500 font-bold">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Prescriptive Recommended Next Action */}
              <div className="bg-gradient-to-br from-red-50 to-slate-50 rounded-xl p-3.5 border border-red-200/80">
                <span className="text-[10px] font-bold uppercase tracking-wider text-red-700 flex items-center gap-1 mb-1">
                  <Sparkles className="w-3 h-3 text-red-600" />
                  Prescriptive Next Best Action
                </span>
                <p className="text-slate-800 font-semibold text-xs leading-relaxed">
                  {selectedLead.recommended_action}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <button
                  onClick={() => handleAction('RECOVERY_LINK')}
                  className="w-full py-2.5 px-3 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 cursor-pointer shadow-sm transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Send 1-Click WhatsApp Recovery Quote Link</span>
                </button>

                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleAction('CALL')}
                    className="py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs flex items-center justify-center gap-1 cursor-pointer transition-colors"
                  >
                    <Phone className="w-3.5 h-3.5" />
                    <span>Log Call</span>
                  </button>
                  <button
                    onClick={() => handleAction('ASSIGN_FIELD')}
                    className="py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs flex items-center justify-center gap-1 cursor-pointer transition-colors"
                  >
                    <UserCheck className="w-3.5 h-3.5" />
                    <span>Assign Field Rep</span>
                  </button>
                </div>
              </div>

              {actionMessage && (
                <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-center text-xs font-semibold animate-fade-in">
                  ✓ {actionMessage}
                </div>
              )}
            </div>
          ) : (
            <div className="p-6 bg-slate-50 rounded-2xl text-center text-xs text-slate-400">
              Select a lead from the table to view AI predictive guidance.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
