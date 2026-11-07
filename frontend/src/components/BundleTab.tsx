import React, { useState } from 'react';
import { 
  Check, Plus, Trash2, Download, ArrowRight, AlertTriangle, 
  FileText, ShieldCheck, Clock, Receipt, HelpCircle, Sparkles 
} from 'lucide-react';
import type { QuoteData, Product } from '../types';

interface BundleTabProps {
  quoteData: QuoteData | null;
  catalogue: Product[];
  onToggleAddon: (product: Product) => void;
  onUpdateQuantity: (productId: string, quantity: number) => void;
  onRemoveItem: (productId: string) => void;
  onProceedToKyc: () => void;
}

export const BundleTab: React.FC<BundleTabProps> = ({
  quoteData,
  catalogue,
  onToggleAddon,
  onUpdateQuantity,
  onRemoveItem,
  onProceedToKyc
}) => {
  const [downloading, setDownloading] = useState(false);

  if (!quoteData) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4 text-center">
        <div className="w-16 h-16 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">No Bundle Configured Yet</h2>
        <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto">
          Please run the AI Advisor in Module 1 or select a demo scenario above to generate an initial catalogue-backed bundle recommendation.
        </p>
      </div>
    );
  }

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      const response = await fetch('/api/v1/quote/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(quoteData)
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${quoteData.quote_id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        window.print();
      }
    } catch {
      window.print();
    } finally {
      setDownloading(false);
    }
  };

  // Find products in catalogue not yet in bundle
  const bundledIds = new Set(quoteData.items.map((i: any) => i.product_id));
  const availableAddons = catalogue.filter((p) => !bundledIds.has(p.product_id));

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6">
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 mb-2">
            <Receipt className="w-3.5 h-3.5 text-red-600" />
            <span>Module 2 · Smart Bundle Configurator & Checkout</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Customize Bundle & Generate Verified Quotation
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time pricing formula: Total Monthly Cost = Σ(Eligible Product Unit Prices × Qty). No hidden fees.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-300 text-slate-700 hover:text-slate-900 hover:border-slate-400 text-xs font-semibold shadow-sm transition-all cursor-pointer"
          >
            <Download className="w-4 h-4 text-slate-500" />
            <span>{downloading ? 'Generating Official PDF...' : 'Download Official Quote (PDF)'}</span>
          </button>

          <button
            onClick={onProceedToKyc}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-md shadow-red-600/30 transition-all cursor-pointer"
          >
            <span>Proceed to Digital KYC</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Validation Warnings */}
      {quoteData.validation_warnings && quoteData.validation_warnings.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Product Eligibility & Dependency Alerts</span>
          </div>
          {quoteData.validation_warnings.map((w, idx) => (
            <p key={idx} className="pl-5">• {w}</p>
          ))}
        </div>
      )}

      {/* 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Bundle Items & Addon Configurator */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Items Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Selected Package Architecture</h3>
                <p className="text-xs text-slate-500">Core bundle services and customized optional add-ons</p>
              </div>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 font-semibold border border-red-200">
                Tier: {quoteData.tier_name || 'Custom'}
              </span>
            </div>

            {/* Core Bundle Items */}
            <div className="mb-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Core Package Products ({quoteData.items.filter((i: any) => !i.is_addon).length} SKUs)
              </span>
              <div className="divide-y divide-slate-100">
                {quoteData.items.filter((i: any) => !i.is_addon).map((item: any) => (
                  <div key={item.product_id} className="py-3 flex flex-wrap items-center justify-between gap-4">
                    <div className="max-w-md">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">{item.product_name}</span>
                        <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{item.description}</p>
                      <div className="flex items-center gap-4 text-[11px] text-slate-500 mt-1">
                        <span>Rate: ₹{item.unit_price_monthly_inr.toLocaleString()} / {item.unit}</span>
                        {item.unit_setup_inr > 0 && <span>Setup: ₹{item.unit_setup_inr.toLocaleString()}</span>}
                        <span>SLA: {item.typical_install_days} days install</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      {/* Quantity controls */}
                      <div className="flex items-center border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
                        <button
                          onClick={() => onUpdateQuantity(item.product_id, Math.max(1, item.quantity - 1))}
                          className="px-2 py-1 text-slate-600 hover:bg-slate-200 text-xs font-bold cursor-pointer"
                        >
                          -
                        </button>
                        <span className="px-3 py-1 text-xs font-semibold text-slate-900 bg-white">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.product_id, item.quantity + 1)}
                          className="px-2 py-1 text-slate-600 hover:bg-slate-200 text-xs font-bold cursor-pointer"
                        >
                          +
                        </button>
                      </div>

                      <div className="text-right min-w-[80px]">
                        <span className="font-black text-slate-900 text-sm">
                          ₹{item.total_monthly_inr.toLocaleString()}
                        </span>
                        <p className="text-[10px] text-slate-400">/ month</p>
                      </div>

                      {quoteData.items.length > 1 && (
                        <button
                          onClick={() => onRemoveItem(item.product_id)}
                          className="p-1 text-slate-400 hover:text-red-600 transition-colors cursor-pointer"
                          title="Remove product"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Configured Optional Add-Ons */}
            {quoteData.items.filter((i: any) => i.is_addon).length > 0 && (
              <div className="pt-3 border-t border-slate-100">
                <span className="text-[10px] font-bold uppercase tracking-wider text-red-600 block mb-2">
                  Configured Optional Add-Ons ({quoteData.items.filter((i: any) => i.is_addon).length} Active)
                </span>
                <div className="divide-y divide-slate-100">
                  {quoteData.items.filter((i: any) => i.is_addon).map((item: any) => (
                    <div key={item.product_id} className="py-2.5 flex flex-wrap items-center justify-between gap-4 bg-red-50/20 p-2.5 rounded-xl border border-red-100/60 mb-1.5">
                      <div className="max-w-md">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900 text-xs">{item.product_name}</span>
                          <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-red-100 text-red-800">
                            Custom Add-On
                          </span>
                        </div>
                        <div className="flex items-center gap-3 text-[10px] text-slate-500 mt-0.5">
                          <span>₹{item.unit_price_monthly_inr.toLocaleString()} / mo</span>
                          {item.unit_setup_inr > 0 && <span>• Setup: ₹{item.unit_setup_inr.toLocaleString()}</span>}
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex items-center border border-slate-200 rounded-lg overflow-hidden bg-white">
                          <button
                            onClick={() => onUpdateQuantity(item.product_id, Math.max(1, item.quantity - 1))}
                            className="px-2 py-0.5 text-slate-600 hover:bg-slate-200 text-xs font-bold cursor-pointer"
                          >
                            -
                          </button>
                          <span className="px-2.5 py-0.5 text-xs font-semibold text-slate-900">
                            {item.quantity}
                          </span>
                          <button
                            onClick={() => onUpdateQuantity(item.product_id, item.quantity + 1)}
                            className="px-2 py-0.5 text-slate-600 hover:bg-slate-200 text-xs font-bold cursor-pointer"
                          >
                            +
                          </button>
                        </div>

                        <div className="text-right min-w-[70px]">
                          <span className="font-black text-slate-900 text-xs">
                            ₹{item.total_monthly_inr.toLocaleString()}
                          </span>
                          <p className="text-[9px] text-slate-400">/ mo</p>
                        </div>

                        <button
                          onClick={() => onRemoveItem(item.product_id)}
                          className="p-1 text-slate-400 hover:text-red-600 transition-colors cursor-pointer"
                          title="Remove addon"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Optional Add-ons Section */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="font-bold text-slate-900 text-base mb-1">Explore Additional Catalogue Add-Ons</h3>
            <p className="text-xs text-slate-500 mb-4">
              Toggle additional enterprise tools with automatic dependency validation and real-time recalculation.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {availableAddons.slice(0, 6).map((addon) => (
                <div
                  key={addon.product_id}
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-red-300 transition-all flex flex-col justify-between bg-slate-50/40"
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-bold text-slate-900 text-xs">{addon.product_name}</span>
                      <span className="text-[11px] font-bold text-red-600">
                        ₹{addon.price_inr_per_month.toLocaleString()}/mo
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 line-clamp-2">{addon.description}</p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400">
                      {addon.one_time_setup_inr > 0 ? `Setup: ₹${addon.one_time_setup_inr}` : 'Zero setup fee'}
                    </span>
                    <button
                      onClick={() => onToggleAddon(addon)}
                      className="flex items-center gap-1 text-[11px] font-bold text-red-600 hover:text-red-700 cursor-pointer"
                    >
                      <Plus className="w-3 h-3" />
                      <span>Add to Bundle</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Quotation Summary Card */}
        <div className="space-y-6">
          <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-xl border border-slate-800">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div>
                <span className="text-[10px] uppercase font-bold text-red-400 tracking-wider">Official Quotation</span>
                <p className="font-mono text-xs font-bold text-white">{quoteData.quote_id}</p>
              </div>
              <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                14 Days Validity
              </span>
            </div>

            {/* Client Info */}
            <div className="text-xs text-slate-300 space-y-1 mb-4 bg-slate-800/40 p-3 rounded-xl border border-slate-800">
              <p><strong>Customer:</strong> {quoteData.business_name}</p>
              <p><strong>Location:</strong> {quoteData.city} (Tier {quoteData.city_tier})</p>
              <p><strong>Contract Term:</strong> {quoteData.contract_months} Months (Guaranteed SLA)</p>
            </div>

            {/* Price Breakdown: Structured Recurring vs One-Time vs Tax */}
            <div className="space-y-3 text-xs border-t border-slate-800 pt-3">
              {/* 1. Monthly Recurring Charges Section */}
              <div className="space-y-1.5 bg-slate-800/30 p-2.5 rounded-lg border border-slate-800/60">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Monthly Ongoing Commitment
                </span>
                <div className="flex justify-between text-slate-300">
                  <span>Monthly Recurring Charges (MRC)</span>
                  <span className="font-semibold text-white">₹{quoteData.monthly_recurring_inr.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-slate-400 text-[11px]">
                  <span>Monthly GST @ 18% (SAC 9984 / 9983)</span>
                  <span>+ ₹{quoteData.applicable_gst_amount_monthly.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-[10px] text-slate-500 italic">
                  <span>Split: 9% CGST + 9% SGST (Intra-state) or 18% IGST</span>
                  <span>Indicative Tax</span>
                </div>
                <div className="pt-1 border-t border-slate-700/60 flex justify-between font-bold text-white">
                  <span>Net Ongoing Monthly Total</span>
                  <span className="text-emerald-400">
                    ₹{(quoteData.monthly_recurring_inr + quoteData.applicable_gst_amount_monthly).toLocaleString()} / mo
                  </span>
                </div>
              </div>

              {/* 2. One-Time Setup Charges Section */}
              <div className="space-y-1.5 bg-slate-800/30 p-2.5 rounded-lg border border-slate-800/60">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  One-Time Deployment / Installation
                </span>
                <div className="flex justify-between text-slate-300">
                  <span>Hardware & Deployment Setup</span>
                  <span className="font-semibold text-white">₹{quoteData.one_time_setup_inr.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-slate-400 text-[11px]">
                  <span>Setup GST @ 18% (Provisioning & Installation)</span>
                  <span>+ ₹{((quoteData.one_time_setup_inr * 18) / 100).toLocaleString()}</span>
                </div>
                <div className="pt-1 border-t border-slate-700/60 flex justify-between font-bold text-white text-[11px]">
                  <span>Net One-Time Setup Total</span>
                  <span>₹{(quoteData.one_time_setup_inr + ((quoteData.one_time_setup_inr * 18) / 100)).toLocaleString()}</span>
                </div>
              </div>

              {/* Savings Callout */}
              {quoteData.calculated_savings_inr > 0 && (
                <div className="flex justify-between text-emerald-400 font-semibold px-1 text-[11px]">
                  <span>Bundle Discount vs Standalone:</span>
                  <span>Save ₹{quoteData.calculated_savings_inr.toLocaleString()} / mo</span>
                </div>
              )}

              {/* Final 1st Month Total */}
              <div className="border-t border-slate-700 pt-3 flex justify-between items-baseline">
                <div>
                  <span className="text-sm font-bold text-white">Total 1st Month Pay</span>
                  <p className="text-[10px] text-slate-400">(MRC + Setup + 18% GST)</p>
                </div>
                <span className="text-2xl font-black text-red-400">
                  ₹{quoteData.total_first_month_inr.toLocaleString()}
                </span>
              </div>
            </div>

            {/* Transparent Tax Disclaimer Callout */}
            <div className="mt-4 p-3 bg-slate-800/80 rounded-xl border border-slate-700/80 text-[10px] text-slate-400 leading-relaxed">
              <strong>Statutory Tax Classification & Assumption Notice:</strong> The 18% GST rate reflects statutory classification for telecommunications connectivity (SAC Heading 9984) and cloud/software services (SAC Heading 9983). Depending on the supplier state and subscriber place of supply, tax is levied either as CGST (9%) + SGST (9%) for intra-state supplies, or IGST (18%) for inter-state supplies. The supplied product catalogue does not include SKU-level HSN codes; physical hardware items (e.g. CCTV cameras, IoT sensors under HSN Chapter 85) are modeled as components of a bundled composite connectivity service, but in final enterprise ERP billing may require distinct HSN goods classification and jurisdictional tax treatment.
            </div>

            {/* CTA */}
            <button
              onClick={onProceedToKyc}
              className="w-full mt-5 py-3 px-4 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-red-600/30 transition-all cursor-pointer"
            >
              <span>Accept Quote & Start Digital KYC</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Terms & Conditions */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 text-xs text-slate-600 space-y-2">
            <span className="font-bold text-slate-900 block text-xs uppercase tracking-wider">
              Terms & Regulatory Assurances
            </span>
            <ul className="space-y-1 text-[11px] list-disc list-inside text-slate-500">
              {quoteData.terms_and_conditions.map((term, i) => (
                <li key={i}>{term}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
