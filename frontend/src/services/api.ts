export const API_BASE = '/api/v1';

export async function fetchCatalogue() {
  const res = await fetch(`${API_BASE}/catalogue`);
  return res.json();
}

export async function getRecommendations(payload: any) {
  const res = await fetch(`${API_BASE}/advisor/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function processVoiceTranscript(payload: { transcript: string; language: string }) {
  const res = await fetch(`${API_BASE}/advisor/process-transcript`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to process voice transcript');
  }
  return res.json();
}

export async function calculateQuote(payload: any) {
  const res = await fetch(`${API_BASE}/quote/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function createQuote(payload: any) {
  const res = await fetch(`${API_BASE}/quote/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function lookupGstin(gstin: string) {
  const res = await fetch(`${API_BASE}/kyc/lookup-gstin/${encodeURIComponent(gstin)}`);
  return res.json();
}

export async function lookupUdyam(udyam: string) {
  const res = await fetch(`${API_BASE}/kyc/lookup-udyam/${encodeURIComponent(udyam)}`);
  return res.json();
}

export async function validateKyc(payload: any) {
  const res = await fetch(`${API_BASE}/kyc/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function verifyKycDocuments(formData: FormData) {
  const res = await fetch(`${API_BASE}/kyc/verify-documents`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to verify KYC documents');
  }
  return res.json();
}

export async function fetchSpecimenDoc(specimenId: string, docType: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/kyc/specimen-file/${encodeURIComponent(specimenId)}/${encodeURIComponent(docType)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Specimen ${specimenId} ${docType} not available.`);
  }
  return res.blob();
}

export async function createOrder(payload: any) {
  const res = await fetch(`${API_BASE}/order/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function getOrder(orderId: string) {
  const res = await fetch(`${API_BASE}/order/${orderId}`);
  return res.json();
}

export async function updateOrderStatus(orderId: string, status: string, notes?: string) {
  const res = await fetch(`${API_BASE}/order/${orderId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, notes })
  });
  return res.json();
}

export async function fetchPartnerLeads(filters: { segment?: string; stage?: string; priority?: string }) {
  const params = new URLSearchParams();
  if (filters.segment) params.append('segment', filters.segment);
  if (filters.stage) params.append('stage', filters.stage);
  if (filters.priority) params.append('priority', filters.priority);
  const res = await fetch(`${API_BASE}/partner/leads?${params.toString()}`);
  return res.json();
}

export async function logPartnerAction(leadId: string, actionType: string, assignedTo?: string) {
  const res = await fetch(`${API_BASE}/partner/lead/${leadId}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_type: actionType, assigned_to: assignedTo })
  });
  return res.json();
}

export async function fetchAnalyticsFunnel() {
  const res = await fetch(`${API_BASE}/analytics/funnel`);
  return res.json();
}

export async function fetchDemoScenarios() {
  const res = await fetch(`${API_BASE}/demo/scenarios`);
  return res.json();
}

export async function downloadQuotePdf(quoteData: any): Promise<Blob> {
  const res = await fetch(`${API_BASE}/quote/generate-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(quoteData)
  });
  if (!res.ok) throw new Error('Failed to generate PDF');
  return res.blob();
}

