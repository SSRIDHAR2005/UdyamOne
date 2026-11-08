import React, { useEffect, useState } from 'react';
import { 
  CheckCircle2, Clock, AlertCircle, Phone, User, MapPin, 
  Wifi, Calendar, Bell, FastForward, Check, Sparkles 
} from 'lucide-react';
import type { OrderData } from '../types';
import { updateOrderStatus } from '../services/api';

interface TrackerTabProps {
  orderData: OrderData | null;
  onOrderUpdated: (updatedOrder: OrderData) => void;
}

const STAGES = [
  { stage: 'PLACED', title: '1. Order Placed', desc: 'Order registered via digital checkout' },
  { stage: 'KYC_VERIFIED', title: '2. KYC Verified', desc: 'Instant GSTIN & DPDP consent passed' },
  { stage: 'CONFIRMED', title: '3. Order Confirmed', desc: 'Commercial booking & SIM dispatch sign-off' },
  { stage: 'FEASIBILITY_CHECKED', title: '4. Network Feasibility', desc: 'Distribution point & OLT loop assigned' },
  { stage: 'INSTALLATION_SCHEDULED', title: '5. Installation Scheduled', desc: 'Field technician appointment confirmed' },
  { stage: 'INSTALLATION_IN_PROGRESS', title: '6. Installation In Progress', desc: 'CPE deployment & router line testing' },
  { stage: 'ACTIVATED', title: '7. Service Activated', desc: 'Live broadband, SLA monitoring active' }
];

export const TrackerTab: React.FC<TrackerTabProps> = ({
  orderData,
  onOrderUpdated
}) => {
  const [updating, setUpdating] = useState(false);
  const [clockNow, setClockNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => setClockNow(Date.now()), 60_000);
    return () => window.clearInterval(timer);
  }, []);

  if (!orderData) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4 text-center">
        <div className="w-16 h-16 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <Clock className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">No Active Order Selected</h2>
        <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto">
          Please place an order in Module 2/3 or select a preloaded scenario to track activation progress.
        </p>
      </div>
    );
  }

  const currentStageIndex = STAGES.findIndex((s) => s.stage === orderData.current_status);
  const dateTime = (value?: string | null) => value
    ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
    : 'Pending';
  const isActivated = orderData.current_status === 'ACTIVATED' && Boolean(orderData.activated_at);
  const activationDate = isActivated ? orderData.activated_at : orderData.estimated_activation_date;
  const activationDeltaDays = activationDate
    ? Math.ceil((new Date(activationDate).getTime() - clockNow) / 86_400_000)
    : null;

  const handleAdvanceStage = async () => {
    if (currentStageIndex < STAGES.length - 1) {
      const nextStage = STAGES[currentStageIndex + 1].stage;
      setUpdating(true);
      try {
        const updated = await updateOrderStatus(orderData.order_id, nextStage, `Advanced to ${nextStage} via Judge Demo Toolbar`);
        onOrderUpdated(updated);
      } catch (e) {
        console.error(e);
      } finally {
        setUpdating(false);
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6">
      {/* Title & Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 mb-2">
            <Clock className="w-3.5 h-3.5 text-red-600" />
            <span>Module 4 · Activation & Order Tracker</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Real-Time Service Delivery & Installation Timeline
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Order milestones, site details, quoted charges, and activation target from the current order record.
          </p>
        </div>

        {/* Demo Fast Forward Action */}
        <div className="flex items-center gap-3">
          {orderData.current_status !== 'ACTIVATED' ? (
            <button
              onClick={handleAdvanceStage}
              disabled={updating}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-md shadow-red-600/30 transition-all cursor-pointer"
            >
              <FastForward className="w-4 h-4" />
              <span>{updating ? 'Updating...' : 'Advance to Next Stage'}</span>
            </button>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-extrabold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Service Fully Live & Operational
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
            <div className="flex flex-wrap items-center justify-between border-b border-slate-100 pb-4 mb-6 gap-2">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400">Tracking Reference</span>
                <p className="font-mono text-base font-bold text-slate-900">{orderData.order_number}</p>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-slate-400">{isActivated ? 'Activated At' : 'Estimated Target Activation'}</span>
                <p className="text-xs font-bold text-red-600">{dateTime(activationDate)}</p>
                {!isActivated && activationDeltaDays !== null && (
                  <p className={`text-[10px] font-semibold ${activationDeltaDays < 0 ? 'text-red-700' : 'text-slate-500'}`}>
                    {activationDeltaDays < 0 ? `${Math.abs(activationDeltaDays)} day(s) overdue` : activationDeltaDays === 0 ? 'Target is today' : `In ${activationDeltaDays} day(s)`}
                  </p>
                )}
                {orderData.is_demo && <span className="mt-1 inline-block rounded bg-amber-100 px-2 py-0.5 text-[9px] font-bold uppercase text-amber-800">Demo sample order</span>}
                {orderData.updated_at && <p className="mt-1 text-[9px] text-slate-400">Updated {dateTime(orderData.updated_at)}</p>}
              </div>
            </div>

            {/* Stepper */}
            <div className="relative pl-6 space-y-8 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
              {STAGES.map((s, idx) => {
                const isCompleted = idx <= currentStageIndex;
                const isCurrent = idx === currentStageIndex;

                return (
                  <div key={s.stage} className="relative flex items-start gap-4">
                    <div
                      className={`absolute -left-6 top-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                        isCompleted
                          ? 'bg-red-600 text-white ring-4 ring-red-100'
                          : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      {isCompleted ? <Check className="w-3.5 h-3.5" /> : idx + 1}
                    </div>

                    <div className="pl-3">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-bold ${isCurrent ? 'text-red-600' : isCompleted ? 'text-slate-900' : 'text-slate-400'}`}>
                          {s.title}
                        </span>
                        {isCurrent && (
                          <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-bold animate-pulse">
                            Current Stage
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{s.desc}</p>
                      {orderData.status_history[idx]?.timestamp && (
                        <p className="mt-1 text-[10px] text-slate-400">{dateTime(orderData.status_history[idx].timestamp)}</p>
                      )}
                      {orderData.status_history[idx]?.note && (
                        <p className="text-[11px] text-slate-600 bg-slate-50 border border-slate-100 rounded-lg p-2 mt-2">
                          <strong>Update:</strong> {orderData.status_history[idx].note}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Simulated Notifications Feed */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2 mb-3">
              <Bell className="w-4 h-4 text-red-600" />
              <span>Simulated Customer Notification History</span>
            </h3>
            <div className="space-y-2 text-xs">
              {orderData.notifications && orderData.notifications.map((n, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-start gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    n.channel === 'WhatsApp' ? 'bg-emerald-100 text-emerald-800' : 'bg-sky-100 text-sky-800'
                  }`}>
                    {n.channel}
                  </span>
                  <p className="text-slate-700">{n.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Technician & Order Metadata */}
        <div className="space-y-6">
          {/* Technician Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <h3 className="font-bold text-slate-900 text-sm">Assigned Field Team</h3>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-red-50 text-red-600 flex items-center justify-center font-bold">
                <User className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900">{orderData.assigned_technician}</p>
                <p className="text-[11px] text-slate-500">Accel Enterprise Fiber Operations</p>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500">Contact Desk</span>
              <a 
                href={`tel:${orderData.technician_contact}`}
                className="font-bold text-red-600 hover:underline flex items-center gap-1"
              >
                <Phone className="w-3.5 h-3.5" />
                <span>{orderData.technician_contact}</span>
              </a>
            </div>
          </div>

          {/* Installation Details */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-3 text-xs">
            <h3 className="font-bold text-slate-900 text-sm mb-1">Site & Commercial Details</h3>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Business Name</span>
              <span className="font-semibold text-slate-800">{orderData.business_name}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Installation Address</span>
              <span className="text-slate-700 flex items-start gap-1 mt-0.5">
                <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
                <span>{orderData.installation_address}</span>
              </span>
              {orderData.installation_address_source && <span className="ml-4 text-[10px] text-slate-400">Source: {orderData.installation_address_source.replaceAll('_', ' ').toLowerCase()}</span>}
            </div>
            {(orderData.city || orderData.pincode) && (
              <div className="flex justify-between">
                <span className="text-slate-500">City / PIN</span>
                <span className="font-semibold text-slate-800">{[orderData.city, orderData.pincode].filter(Boolean).join(' · ')}</span>
              </div>
            )}
            {orderData.num_sites !== undefined && (
              <div className="flex justify-between">
                <span className="text-slate-500">Sites on quote</span>
                <span className="font-semibold text-slate-800">{orderData.num_sites}</span>
              </div>
            )}
            {orderData.items_summary?.length > 0 && (
              <div className="border-t border-slate-100 pt-3 space-y-2">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Selected quote items</span>
                {orderData.items_summary.map((item: any, index: number) => (
                  <div key={`${item.name}-${index}`} className="flex justify-between gap-3 text-[11px]">
                    <span className="text-slate-600">{item.name} × {item.qty}</span>
                    <span className="font-semibold text-slate-800">₹{Number(item.monthly || 0).toLocaleString()}/mo</span>
                  </div>
                ))}
              </div>
            )}
            <div className="border-t border-slate-100 pt-3 flex justify-between">
              <span className="text-slate-500">Quoted monthly subtotal</span>
              <span className="font-bold text-slate-900">₹{orderData.monthly_amount_inr.toLocaleString()}/mo</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">One-Time Setup Fee</span>
              <span className="font-semibold text-slate-800">₹{orderData.setup_charges_inr.toLocaleString()}</span>
            </div>
            {orderData.quote_id && <p className="border-t border-slate-100 pt-2 text-[10px] text-slate-400">Quote reference: {orderData.quote_id}</p>}
          </div>
        </div>
      </div>
    </div>
  );
};
