import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DemoToolbar } from './components/DemoToolbar';
import { AdvisorTab } from './components/AdvisorTab';
import { BundleTab } from './components/BundleTab';
import { KycTab } from './components/KycTab';
import { TrackerTab } from './components/TrackerTab';
import { PartnerTab } from './components/PartnerTab';
import { LeadIntelligenceTab } from './components/LeadIntelligenceTab';
import { AnalyticsTab } from './components/AnalyticsTab';
import { SubmissionModals } from './components/SubmissionModals';

import type { 
  Product, AdvisorResponse, RecommendedTier, 
  QuoteData, KYCResult, OrderData 
} from './types';
import { 
  fetchCatalogue, getRecommendations, calculateQuote, 
  createQuote, createOrder, getOrder, updateOrderStatus 
} from './services/api';

export function App() {
  // Navigation & Mode
  const [activeTab, setActiveTab] = useState<string>('advisor');
  const [portalMode, setPortalMode] = useState<'customer' | 'partner'>('customer');
  const [language, setLanguage] = useState<string>('en');
  const [activeModal, setActiveModal] = useState<'architecture' | 'business_case' | 'privacy' | 'script' | null>(null);

  // Core Data State
  const [catalogue, setCatalogue] = useState<Product[]>([]);
  const [recommendations, setRecommendations] = useState<AdvisorResponse | null>(null);
  const [advisorLoading, setAdvisorLoading] = useState(false);
  const [quoteData, setQuoteData] = useState<QuoteData | null>(null);
  const [kycResult, setKycResult] = useState<KYCResult | null>(null);
  const [orderData, setOrderData] = useState<OrderData | null>(null);

  // Selected Demo Trackers
  const [currentScenario, setCurrentScenario] = useState<string>('');
  const [currentKycCase, setCurrentKycCase] = useState<string>('');

  // Form State
  const [formData, setFormData] = useState({
    business_name: 'Dr. Meera Diagnostic & Dental Clinic',
    business_type: 'clinic',
    segment: 'prof',
    city: 'Bengaluru',
    city_tier: 1,
    pincode: '560034',
    employee_count: 8,
    num_sites: 1,
    monthly_budget_inr: 4500,
    current_internet: 'home_broadband',
    need_sims: 3,
    need_pos: true,
    need_whatsapp: true,
    need_cctv: true,
    cctv_cameras_count: 3,
    need_cloud_email: true,
    need_cloud_backup: true,
    need_security: true,
    need_failover_backup: false,
    need_dedicated_leased_line: false,
    has_gstin: true,
    gstin: '29CPSXS6426Z1ZL',
    preferred_language: 'en'
  });

  // Load Catalogue on Mount
  useEffect(() => {
    fetchCatalogue().then(setCatalogue).catch(console.error);
    getOrder('ORD-2026-88219').then(setOrderData).catch(console.error);
  }, []);

  // Sync language with form
  useEffect(() => {
    setFormData((prev) => ({ ...prev, preferred_language: language }));
  }, [language]);

  // Advisor Recommendation Handler
  const handleGetRecommendations = async () => {
    setAdvisorLoading(true);
    try {
      const res = await getRecommendations(formData);
      setRecommendations(res);
      if (res.recommendations && res.recommendations.length > 1) {
        handleSelectTier(res.recommendations[1]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAdvisorLoading(false);
    }
  };

  // Voice Transcript Recommendation Handler
  const handleApplyVoiceRecommendations = (data: any) => {
    if (data.recommendations) {
      setRecommendations(data.recommendations);
      if (data.recommendations.recommendations && data.recommendations.recommendations.length > 1) {
        const targetTier = data.recommendations.recommendations[1] || data.recommendations.recommendations[0];
        handleSelectTier(targetTier);
      }
    }
  };

  // Tier Selection Handler
  const handleSelectTier = async (tier: RecommendedTier) => {
    const selected = tier.products.map((p) => ({
      product_id: p.product_id,
      quantity: p.quantity,
      is_addon: false
    }));

    const reqPayload = {
      business_name: formData.business_name,
      business_type: formData.business_type,
      segment: formData.segment || 'prof',
      city: formData.city,
      city_tier: formData.city_tier,
      employee_count: formData.employee_count,
      num_sites: formData.num_sites,
      has_gstin: formData.has_gstin,
      tier_name: tier.tier_name,
      selected_products: selected
    };

    try {
      const q = await createQuote(reqPayload);
      setQuoteData(q);
      setActiveTab('bundle');
    } catch (e) {
      console.error(e);
    }
  };

  // Bundle Add-on Toggles
  const handleToggleAddon = async (addon: Product) => {
    if (!quoteData) return;
    const currentItems = [...quoteData.items];
    const exists = currentItems.find((i) => i.product_id === addon.product_id);
    let updatedSelected = [];

    if (exists) {
      updatedSelected = currentItems.filter((i) => i.product_id !== addon.product_id).map((i) => ({
        product_id: i.product_id,
        quantity: i.quantity,
        is_addon: i.is_addon
      }));
    } else {
      updatedSelected = currentItems.map((i) => ({
        product_id: i.product_id,
        quantity: i.quantity,
        is_addon: i.is_addon
      }));
      updatedSelected.push({
        product_id: addon.product_id,
        quantity: 1,
        is_addon: true
      });
    }

    const payload = {
      business_name: quoteData.business_name,
      business_type: formData.business_type,
      segment: quoteData.segment,
      city: quoteData.city,
      city_tier: quoteData.city_tier,
      employee_count: formData.employee_count,
      num_sites: formData.num_sites,
      has_gstin: formData.has_gstin,
      tier_name: quoteData.tier_name || 'Custom',
      selected_products: updatedSelected
    };

    const recalculated = await calculateQuote(payload);
    setQuoteData(recalculated);
  };

  const handleUpdateQuantity = async (productId: string, quantity: number) => {
    if (!quoteData) return;
    const updatedSelected = quoteData.items.map((i) => ({
      product_id: i.product_id,
      quantity: i.product_id === productId ? quantity : i.quantity,
      is_addon: i.is_addon
    }));

    const payload = {
      business_name: quoteData.business_name,
      business_type: formData.business_type,
      segment: quoteData.segment,
      city: quoteData.city,
      city_tier: quoteData.city_tier,
      employee_count: formData.employee_count,
      num_sites: formData.num_sites,
      has_gstin: formData.has_gstin,
      tier_name: quoteData.tier_name || 'Custom',
      selected_products: updatedSelected
    };

    const recalculated = await calculateQuote(payload);
    setQuoteData(recalculated);
  };

  const handleRemoveItem = async (productId: string) => {
    if (!quoteData) return;
    const updatedSelected = quoteData.items
      .filter((i) => i.product_id !== productId)
      .map((i) => ({
        product_id: i.product_id,
        quantity: i.quantity,
        is_addon: i.is_addon
      }));

    const payload = {
      business_name: quoteData.business_name,
      business_type: formData.business_type,
      segment: quoteData.segment,
      city: quoteData.city,
      city_tier: quoteData.city_tier,
      employee_count: formData.employee_count,
      num_sites: formData.num_sites,
      has_gstin: formData.has_gstin,
      tier_name: quoteData.tier_name || 'Custom',
      selected_products: updatedSelected
    };

    const recalculated = await calculateQuote(payload);
    setQuoteData(recalculated);
  };

  // Demo Scenario Handler
  const handleSelectScenario = (scenId: string) => {
    setCurrentScenario(scenId);
    if (scenId === 'scenario-kirana') {
      setFormData({
        business_name: 'Ramesh Provision Store',
        business_type: 'retail',
        segment: 'micro',
        city: 'Jaipur',
        city_tier: 2,
        pincode: '302001',
        employee_count: 3,
        num_sites: 1,
        monthly_budget_inr: 1800,
        current_internet: 'mobile_hotspot',
        need_sims: 1,
        need_pos: true,
        need_whatsapp: true,
        need_cctv: false,
        cctv_cameras_count: 0,
        need_cloud_email: false,
        need_cloud_backup: false,
        need_security: false,
        need_failover_backup: false,
        need_dedicated_leased_line: false,
        has_gstin: false,
        gstin: '',
        preferred_language: 'hi'
      });
      setLanguage('hi');
    } else if (scenId === 'scenario-clinic') {
      setFormData({
        business_name: 'Dr. Meera Diagnostic & Dental Clinic',
        business_type: 'clinic',
        segment: 'prof',
        city: 'Bengaluru',
        city_tier: 1,
        pincode: '560034',
        employee_count: 8,
        num_sites: 1,
        monthly_budget_inr: 4500,
        current_internet: 'home_broadband',
        need_sims: 3,
        need_pos: true,
        need_whatsapp: true,
        need_cctv: true,
        cctv_cameras_count: 3,
        need_cloud_email: true,
        need_cloud_backup: true,
        need_security: true,
        need_failover_backup: false,
        need_dedicated_leased_line: false,
        has_gstin: true,
        gstin: '29CPSXS6426Z1ZL',
        preferred_language: 'en'
      });
      setLanguage('en');
    } else if (scenId === 'scenario-restaurant') {
      setFormData({
        business_name: 'Spice Route Kitchens',
        business_type: 'restaurant',
        segment: 'multi',
        city: 'Chennai',
        city_tier: 1,
        pincode: '600004',
        employee_count: 22,
        num_sites: 3,
        monthly_budget_inr: 12000,
        current_internet: 'local_cable',
        need_sims: 6,
        need_pos: true,
        need_whatsapp: true,
        need_cctv: true,
        cctv_cameras_count: 6,
        need_cloud_email: true,
        need_cloud_backup: false,
        need_security: true,
        need_failover_backup: true,
        need_dedicated_leased_line: false,
        has_gstin: true,
        gstin: '33MFTXS9954Q1Z9',
        preferred_language: 'ta'
      });
      setLanguage('ta');
    } else if (scenId === 'scenario-manufacturer') {
      setFormData({
        business_name: 'Precision Auto Components Ltd',
        business_type: 'mfg',
        segment: 'mfg',
        city: 'Pune',
        city_tier: 1,
        pincode: '411018',
        employee_count: 35,
        num_sites: 1,
        monthly_budget_inr: 35000,
        current_internet: 'leased_line',
        need_sims: 10,
        need_pos: false,
        need_whatsapp: false,
        need_cctv: true,
        cctv_cameras_count: 8,
        need_cloud_email: true,
        need_cloud_backup: true,
        need_security: true,
        need_failover_backup: true,
        need_dedicated_leased_line: true,
        has_gstin: true,
        gstin: '27DGKXS9651J1Z2',
        preferred_language: 'en'
      });
      setLanguage('en');
    }
    setActiveTab('advisor');
  };

  const handleSelectKycCase = (kId: string) => {
    setCurrentKycCase(kId);
    setActiveTab('kyc');
  };

  const handleAdvanceOrderStage = async () => {
    if (!orderData) return;
    const stages = ['PLACED', 'KYC_VERIFIED', 'CONFIRMED', 'FEASIBILITY_CHECKED', 'INSTALLATION_SCHEDULED', 'INSTALLATION_IN_PROGRESS', 'ACTIVATED'];
    const idx = stages.indexOf(orderData.current_status);
    if (idx < stages.length - 1) {
      const nextStage = stages[idx + 1];
      const updated = await updateOrderStatus(orderData.order_id, nextStage, 'Advanced via Demo Toolbar');
      setOrderData(updated);
    }
  };

  const handleResetDemo = () => {
    setCurrentScenario('');
    setCurrentKycCase('');
    setRecommendations(null);
    setQuoteData(null);
    setKycResult(null);
    setActiveTab('advisor');
  };

  // Order Creation from KYC
  const handleKycApproved = async (kycRes: KYCResult) => {
    setKycResult(kycRes);
    if (!quoteData) return;

    try {
      const newOrder = await createOrder({
        quote_id: quoteData.quote_id,
        kyc_id: kycRes.verification_id,
        business_name: quoteData.business_name,
        contact_name: formData.business_name.includes('Dr.') ? 'Dr. Meera' : 'Ramesh Kumar',
        contact_phone: '+91 98765 43210',
        contact_email: 'contact@enterprise.in',
        installation_address: `${formData.city} Central Office, Pin ${formData.pincode}`,
        city: formData.city,
        pincode: formData.pincode
      });
      setOrderData(newOrder);
      setActiveTab('tracker');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        portalMode={portalMode}
        setPortalMode={setPortalMode}
        language={language}
        setLanguage={setLanguage}
        onOpenModal={setActiveModal}
      />

      {/* Demo Suite Control Bar */}
      <DemoToolbar
        onSelectScenario={handleSelectScenario}
        onSelectKycCase={handleSelectKycCase}
        onAdvanceOrderStage={handleAdvanceOrderStage}
        onReset={handleResetDemo}
        currentScenario={currentScenario}
        currentKycCase={currentKycCase}
      />

      {/* Main View Portals */}
      <main className="flex-1 pb-16">
        {portalMode === 'customer' ? (
          <>
            {activeTab === 'advisor' && (
              <AdvisorTab
                formData={formData}
                setFormData={setFormData}
                onGetRecommendations={handleGetRecommendations}
                recommendations={recommendations}
                loading={advisorLoading}
                onSelectTier={handleSelectTier}
                language={language}
                onApplyVoiceRecommendations={handleApplyVoiceRecommendations}
              />
            )}
            {activeTab === 'bundle' && (
              <BundleTab
                quoteData={quoteData}
                catalogue={catalogue}
                onToggleAddon={handleToggleAddon}
                onUpdateQuantity={handleUpdateQuantity}
                onRemoveItem={handleRemoveItem}
                onProceedToKyc={() => setActiveTab('kyc')}
              />
            )}
            {activeTab === 'kyc' && (
              <KycTab
                quoteData={quoteData}
                onKycApproved={handleKycApproved}
                selectedKycPreset={currentKycCase}
              />
            )}
            {activeTab === 'tracker' && (
              <TrackerTab
                orderData={orderData}
                onOrderUpdated={setOrderData}
              />
            )}
          </>
        ) : (
          <>
            {activeTab === 'partner' && <PartnerTab />}
            {activeTab === 'intelligence' && <LeadIntelligenceTab />}
            {activeTab === 'analytics' && <AnalyticsTab />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-6 text-slate-400 text-xs">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-white text-sm">UdyamOne</span>
            <span>· Airtel SYNC Hackathon 2026 Enterprise Track A</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Fictional operator Accel Business & synthetic dataset simulation. Zero production credentials exposed.
          </p>
        </div>
      </footer>

      {/* Presentation Modals (Deliverables 1, 2, 3, 4) */}
      <SubmissionModals
        type={activeModal}
        onClose={() => setActiveModal(null)}
      />
    </div>
  );
}

export default App;
