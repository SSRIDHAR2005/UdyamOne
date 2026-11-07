import React, { useState, useEffect } from 'react';
import { 
  BarChart3, TrendingUp, AlertTriangle, ArrowDownRight, 
  Users, CheckCircle2, ShieldCheck, PieChart, Layers, Target 
} from 'lucide-react';
import { fetchAnalyticsFunnel } from '../services/api';

export const AnalyticsTab: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyticsFunnel()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading || !data) {
    return (
      <div className="max-w-6xl mx-auto py-16 text-center text-sm text-slate-500">
        Loading Executive Business Intelligence data...
      </div>
    );
  }

  const funnel = data.historical_funnel;
  const steepest = data.steepest_drop;
  const segments = data.segments;
  const gstinAdv = data.gstin_advantage;
  const benchmarks = data.benchmarks;

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 mb-2">
            <BarChart3 className="w-3.5 h-3.5 text-red-600" />
            <span>Module 7 · Executive Business Intelligence & Funnel Analytics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            MSME Acquisition Funnel Diagnosis & Baseline Telemetry
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Grounded directly in the synthetic dataset of 5,000 SMB leads (Apr–Jun 2026). Identifies critical bottlenecks and engineered target ROI.
          </p>
        </div>

        <span className="text-xs font-bold px-3 py-1.5 rounded-xl bg-slate-900 text-white border border-slate-800">
          Historical Baseline (Measured) vs Target Projections (Modeled)
        </span>
      </div>

      {/* Primary Funnel Cards */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h3 className="font-bold text-slate-900 text-base mb-6 flex items-center justify-between">
          <span>Quarterly Acquisition Funnel (5,000 Leads → 368 Activations, 7.36% Net)</span>
          <span className="text-xs font-medium text-slate-500">Source: smb_leads.csv</span>
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold uppercase text-slate-400">1. Leads Generated</span>
            <p className="text-2xl font-black text-slate-900 mt-1">{funnel.total_leads.toLocaleString()}</p>
            <span className="text-[10px] text-slate-500">100% Base</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold uppercase text-slate-400">2. Contacted</span>
            <p className="text-2xl font-black text-slate-800 mt-1">{funnel.contacted.toLocaleString()}</p>
            <span className="text-[10px] text-emerald-600 font-bold">68% of Leads</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold uppercase text-slate-400">3. Needs Assessed</span>
            <p className="text-2xl font-black text-slate-800 mt-1">{funnel.needs_assessed.toLocaleString()}</p>
            <span className="text-[10px] text-emerald-600 font-bold">58% of Contacted</span>
          </div>

          <div className="p-4 rounded-xl bg-red-50 border-2 border-red-500 text-center relative shadow-sm">
            <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-red-600 text-white text-[9px] font-extrabold px-2 py-0.2 rounded-full uppercase">
              Steepest Drop
            </span>
            <span className="text-[10px] font-bold uppercase text-red-700">4. Quote Accepted</span>
            <p className="text-2xl font-black text-red-600 mt-1">{funnel.quote_accepted.toLocaleString()}</p>
            <span className="text-[10px] text-red-700 font-bold">44% of Assessed</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold uppercase text-slate-400">5. KYC Complete</span>
            <p className="text-2xl font-black text-slate-800 mt-1">{funnel.kyc_complete.toLocaleString()}</p>
            <span className="text-[10px] text-emerald-600 font-bold">68% of Quotes</span>
          </div>

          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-center">
            <span className="text-[10px] font-bold uppercase text-emerald-700">6. Activated</span>
            <p className="text-2xl font-black text-emerald-600 mt-1">{funnel.activated.toLocaleString()}</p>
            <span className="text-[10px] text-emerald-700 font-bold">63% of KYC</span>
          </div>
        </div>

        {/* Steepest Drop Diagnosis Callout */}
        <div className="mt-6 p-4 rounded-xl bg-amber-50 border border-amber-200 flex flex-wrap items-center justify-between gap-4 text-xs text-amber-900">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-sm block text-amber-950">
                Core Vulnerability: {steepest.drop_count} Leads Lost Between Needs Assessed & Quote Accepted ({steepest.drop_percentage}% Drop)
              </span>
              <p className="text-amber-800 mt-0.5">
                Root causes in historical data: Quote took 3-5 days to arrive (179 drops), quote was too complex with unfamiliar product codes (206 drops), and price perceived as too high without transparent add-on customization (414 drops).
              </p>
            </div>
          </div>
          <div className="bg-white px-3 py-2 rounded-lg border border-amber-200 font-semibold text-red-600">
            Solved by UdyamOne Instant 3-Min Advisor & Transparent Bundle Configurator
          </div>
        </div>
      </div>

      {/* 2-Column Analytics: Segments + GSTIN Lift */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Segment Breakdown */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-base flex items-center justify-between">
            <span>Customer Segment Distribution</span>
            <span className="text-xs text-slate-400">Target Strategy</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between font-semibold mb-1">
                <span>Micro Retail & Services (Kirana, Salon, Pharmacy)</span>
                <span className="font-bold text-slate-900">55% of Base</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-red-600 h-full rounded-full" style={{ width: '55%' }}></div>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">High volume scale play. Prioritizes affordable broadband + POS/UPI + WhatsApp catalogue.</p>
            </div>

            <div>
              <div className="flex justify-between font-semibold mb-1">
                <span>Professional Offices (Clinics, CA Firms, Coaching)</span>
                <span className="font-bold text-slate-900">25% of Base</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-red-500 h-full rounded-full" style={{ width: '25%' }}></div>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Highest early adoption & margin. Prioritizes cloud email, backup & endpoint security.</p>
            </div>

            <div>
              <div className="flex justify-between font-semibold mb-1">
                <span>Small Multi-Site Businesses (Restaurants, Chains)</span>
                <span className="font-bold text-slate-900">15% of Base</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-slate-700 h-full rounded-full" style={{ width: '15%' }}></div>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Multi-site central billing, failover 4G/5G, and centralized cloud CCTV.</p>
            </div>

            <div>
              <div className="flex justify-between font-semibold mb-1">
                <span>Small Manufacturers (Auto Parts, Textiles)</span>
                <span className="font-bold text-slate-900">5% of Base</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-slate-500 h-full rounded-full" style={{ width: '5%' }}></div>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">High ARPU enterprise accounts requiring dedicated Leased Line & IoT sensor kits.</p>
            </div>
          </div>
        </div>

        {/* GSTIN Conversion Lift */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-base flex items-center justify-between">
            <span>GSTIN Availability Lift Analysis</span>
            <span className="text-xs text-emerald-600 font-bold">4.8× Multiplier</span>
          </h3>

          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
              <span className="text-[11px] text-emerald-800 font-semibold block">With Registered GSTIN</span>
              <p className="text-3xl font-black text-emerald-600 mt-1">{gstinAdv.with_gstin_conversion_pct}%</p>
              <span className="text-[10px] text-emerald-700 font-bold">Lead-to-Activation Rate</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <span className="text-[11px] text-slate-600 font-semibold block">Without GSTIN (Unregistered)</span>
              <p className="text-3xl font-black text-slate-500 mt-1">{gstinAdv.without_gstin_conversion_pct}%</p>
              <span className="text-[10px] text-slate-500">Lead-to-Activation Rate</span>
            </div>
          </div>

          <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200 text-xs text-slate-600 leading-relaxed">
            <strong>Strategic Implication:</strong> Unregistered businesses drop 4.8× more frequently because sales reps traditionally demand tax paperwork upfront. UdyamOne bridges this gap by offering a streamlined Micro onboarding path with Udyam registration support, unlocking the 55% micro retail market.
          </div>
        </div>
      </div>

      {/* Benchmarks Comparison Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 overflow-hidden">
        <h3 className="font-bold text-slate-900 text-base mb-4 flex items-center justify-between">
          <span>Comparative Unit Economics & Proposed Business Impact</span>
          <span className="text-xs font-semibold text-slate-400">Strictly Labelled Baseline vs Projected</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 font-bold text-slate-500">
              <tr>
                <th className="p-3">Core Performance Metric</th>
                <th className="p-3">Historical Baseline (smb_leads.csv)</th>
                <th className="p-3">UdyamOne Target Projection (Modeled at Scale)</th>
                <th className="p-3">Projected Target Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr>
                <td className="p-3 font-semibold text-slate-900">Lead to Activation Cycle Time</td>
                <td className="p-3 text-red-600 font-bold">17.6 Days (Measured Baseline)</td>
                <td className="p-3 text-emerald-600 font-bold">4.5 Days (Engineered Target)</td>
                <td className="p-3 text-emerald-700 font-bold">-74% Faster Cycle Time</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Customer Chasing Calls</td>
                <td className="p-3 text-red-600 font-bold">3.0 Calls per Customer (Measured Baseline)</td>
                <td className="p-3 text-emerald-600 font-bold">0.3 Calls (Target with Proactive App Tracker)</td>
                <td className="p-3 text-emerald-700 font-bold">-90% Support Ticket Reductions</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Blended Customer Acquisition Cost (CAC)</td>
                <td className="p-3 text-red-600 font-bold">₹15,000 per Activated SMB (High-Touch Field Baseline)</td>
                <td className="p-3 text-emerald-600 font-bold">₹4,800 per Activated SMB (Modeled Target at Scale)</td>
                <td className="p-3 text-emerald-700 font-bold">-68% Cost Savings (Self-Serve Funnel)</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Average Revenue Per User (ARPU)</td>
                <td className="p-3 text-slate-700">₹6,900 / month (Measured Baseline)</td>
                <td className="p-3 text-slate-900 font-bold">₹7,200 / month (Targeted Multi-Product Bundle)</td>
                <td className="p-3 text-emerald-700 font-bold">+4.3% Upsell Attachment</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Funnel Conversion Rate</td>
                <td className="p-3 text-red-600 font-bold">7.36% (368 / 5,000 Measured Baseline)</td>
                <td className="p-3 text-emerald-600 font-bold">24.50% (Modeled Target at Commercial Scale)</td>
                <td className="p-3 text-emerald-700 font-bold">+3.3× Overall Funnel Lift</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mt-4 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-[11px] text-slate-500 leading-relaxed">
          <strong>Methodological Transparency & Audit Disclosure:</strong> Historical baseline metrics (17.6 days cycle time, 7.36% conversion, 3.0 follow-up calls) are verified directly against <code className="text-slate-700 bg-slate-200 px-1 py-0.5 rounded">smb_leads.csv</code> (368 activations out of 5,000 synthetic SMB records). UdyamOne values (4.5 days, 24.50% conversion, ₹4,800 CAC) represent <strong>engineered target projections</strong> under full commercial rollout with automated instant quoting, digital KYC, and proactive self-service tracking, rather than empirically achieved operational results in this simulated prototype.
        </div>
      </div>
    </div>
  );
};

