import React, { useState, useRef } from 'react';
import { 
  ShieldCheck, CheckCircle2, AlertOctagon, AlertTriangle, FileText, 
  Upload, Search, ArrowRight, Lock, Eye, RefreshCw, Check, Sparkles,
  X, Trash2, AlertCircle, Loader2, File, Image as ImageIcon
} from 'lucide-react';
import type { KYCResult, QuoteData } from '../types';
import { lookupGstin, lookupUdyam, verifyKycDocuments, fetchSpecimenDoc, extractKycIdentifiers, validateKycIdentifiers } from '../services/api';

interface KycTabProps {
  quoteData: QuoteData | null;
  onKycApproved: (kycResult: KYCResult) => void;
  selectedKycPreset?: string;
}

type DocType = 'gst_certificate' | 'udyam_certificate' | 'signatory_id' | 'address_proof';

interface UploadedDocState {
  file: File | null;
  status: 'Not Uploaded' | 'Uploaded' | 'Processing' | 'Verified' | 'Needs Review' | 'Failed';
  previewUrl: string | null;
  error: string | null;
  dragOver: boolean;
}

export const KycTab: React.FC<KycTabProps> = ({
  quoteData,
  onKycApproved,
  selectedKycPreset
}) => {
  // DPDP Consent State
  const [consentGiven, setConsentGiven] = useState(true);
  const [purposes, setPurposes] = useState({
    gstin_lookup: true,
    udyam_verification: true,
    telecom_regulatory_compliance: true
  });

  // Business IDs
  const [businessName, setBusinessName] = useState(quoteData?.business_name || 'Harmony Dental Care');
  const [gstin, setGstin] = useState(quoteData?.items?.[0] ? '19EOGXH4115Y1ZL' : '19EOGXH4115Y1ZL');
  const [udyamNumber, setUdyamNumber] = useState('UDYAM-WB-00-5053330');
  const [applicantName, setApplicantName] = useState('Joseph Shah');
  const [applicantRole, setApplicantRole] = useState('Authorized Signatory & Managing Partner');

  // Lookup results
  const [gstLookup, setGstLookup] = useState<any>(null);
  const [udyamLookup, setUdyamLookup] = useState<any>(null);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState<any>(null);
  const [identifierValidation, setIdentifierValidation] = useState<any>(null);
  const [identifiersConfirmed, setIdentifiersConfirmed] = useState(false);

  // Validation results
  const [validationResult, setValidationResult] = useState<KYCResult | null>(null);
  const [validating, setValidating] = useState(false);
  const [attachLoading, setAttachLoading] = useState(false);

  // Uploaded documents state (initial status: "Not Uploaded" in neutral grey)
  const [docFiles, setDocFiles] = useState<Record<DocType, UploadedDocState>>({
    gst_certificate: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false },
    udyam_certificate: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false },
    signatory_id: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false },
    address_proof: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false }
  });

  // File input refs for each document card
  const fileInputRefs = {
    gst_certificate: useRef<HTMLInputElement | null>(null),
    udyam_certificate: useRef<HTMLInputElement | null>(null),
    signatory_id: useRef<HTMLInputElement | null>(null),
    address_proof: useRef<HTMLInputElement | null>(null)
  };

  // All 12 Student Specimen Applicants (K01 to K12)
  const allSpecimens = [
    { id: 'K02', label: 'K02: Harmony Dental (Valid Pass)', name: 'Harmony Dental Care', gstin: '19EOGXH4115Y1ZL', udyam: 'UDYAM-WB-00-5053330', applicant: 'Joseph Shah', status: 'PASS', issue: 'Clean, fully compliant specimen' },
    { id: 'K01', label: 'K01: Vindhya Tours (Cancelled GST)', name: 'Vindhya Tours & Travels', gstin: '37IHKXV5167L1ZS', udyam: '', applicant: 'Neha Kaur', status: 'FAILED', issue: 'Planted Cancelled GSTIN' },
    { id: 'K03', label: 'K03: Ganesh Woodcraft (Valid Pass)', name: 'Ganesh Woodcraft', gstin: '27XUIXG0767D1ZP', udyam: 'UDYAM-MH-00-9516696', applicant: 'Joseph Singh', status: 'PASS', issue: 'Valid GSTIN & Udyam' },
    { id: 'K04', label: 'K04: Saffron Dental (Blank GST Doc)', name: 'Saffron Dental Care LLP', gstin: '27PZSXS1936O1ZH', udyam: 'UDYAM-MH-00-6131836', applicant: 'Fatima Pillai', status: 'FAILED', issue: 'Planted Blank/corrupted GST cert image' },
    { id: 'K05', label: 'K05: Balaji Realty (Missing Udyam)', name: 'Balaji Realty LLP', gstin: '32TZAXB5481U1Z1', udyam: 'UDYAM-KL-00-5521886', applicant: 'Anita Shah', status: 'REVIEW_REQUIRED', issue: 'Planted Missing Udyam certificate file' },
    { id: 'K06', label: 'K06: Saffron Salon (Valid Pass)', name: 'Saffron Unisex Salon', gstin: '08YKZXS5189L1ZO', udyam: 'UDYAM-RJ-00-6577157', applicant: 'Pooja Shah', status: 'PASS', issue: 'Valid GSTIN & Udyam' },
    { id: 'K07', label: 'K07: Shri Physio (Name Mismatch)', name: 'Shri Physio Clinic', gstin: '07CPCXN0398P1ZT', udyam: 'UDYAM-DL-00-9565547', applicant: 'Neha Banerjee', status: 'REVIEW_REQUIRED', issue: 'Planted Name mismatch vs Neelgiri Physio doc' },
    { id: 'K08', label: 'K08: Green Leaf Legal (Valid Pass)', name: 'Green Leaf Legal Associates', gstin: '24XORXG9365M1Z3', udyam: 'UDYAM-GJ-00-9158296', applicant: 'Joseph Rao', status: 'PASS', issue: 'Valid GSTIN & Udyam' },
    { id: 'K09', label: 'K09: Kaveri Insurance (Valid Pass)', name: 'Kaveri Insurance Advisors', gstin: '37LDYXK0296F1ZB', udyam: 'UDYAM-AP-00-9751562', applicant: 'Anita Kulkarni', status: 'PASS', issue: 'Valid GSTIN & Udyam' },
    { id: 'K10', label: 'K10: Kaveri Stays (Valid Pass)', name: 'Kaveri Stays LLP', gstin: '27QHJXK0658U1ZL', udyam: 'UDYAM-MH-00-7183141', applicant: 'Nisha Arora', status: 'PASS', issue: 'Valid GSTIN & Udyam' },
    { id: 'K11', label: 'K11: Trinity Bake (Expired Bill)', name: 'Trinity Bake House Pvt Ltd', gstin: '03KGZXT1320R1ZZ', udyam: 'UDYAM-PB-00-9719478', applicant: 'Vikram Pillai', status: 'REVIEW_REQUIRED', issue: 'Planted Expired bill (>90d from 2026-07-15)' },
    { id: 'K12', label: 'K12: Star Electronics (Valid Pass)', name: 'Star Electronics', gstin: '37NBLXS1145E1ZU', udyam: 'UDYAM-AP-00-5186772', applicant: 'Pooja Agarwal', status: 'PASS', issue: 'Valid GSTIN & Udyam' }
  ];

  const [activeSpecimenId, setActiveSpecimenId] = useState('K02');

  // Quick preset loader
  const loadPreset = (presetId: string) => {
    setActiveSpecimenId(presetId);
    const spec = allSpecimens.find(s => s.id === presetId);
    if (spec) {
      setBusinessName(spec.name);
      setGstin(spec.gstin);
      setUdyamNumber(spec.udyam);
      setApplicantName(spec.applicant);
    }
    setGstLookup(null);
    setUdyamLookup(null);
    setValidationResult(null);
    setOcrResult(null);
    setIdentifierValidation(null);
    setIdentifiersConfirmed(false);

    // Reset document states to Not Uploaded
    setDocFiles({
      gst_certificate: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false },
      udyam_certificate: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false },
      signatory_id: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false },
      address_proof: { file: null, status: 'Not Uploaded', previewUrl: null, error: null, dragOver: false }
    });
  };

  // Auto-attach genuine specimen documents from server
  const handleAutoAttachSpecimens = async () => {
    setAttachLoading(true);
    try {
      const docTypes: DocType[] = ['gst_certificate', 'udyam_certificate', 'signatory_id', 'address_proof'];
      const updated = { ...docFiles };

      for (const dtype of docTypes) {
        try {
          const blob = await fetchSpecimenDoc(activeSpecimenId, dtype);
          const fileName = `${activeSpecimenId}_${dtype}.png`;
          const file = new File([blob], fileName, { type: 'image/png' });
          const previewUrl = URL.createObjectURL(file);
          updated[dtype] = {
            file,
            status: 'Uploaded',
            previewUrl,
            error: null,
            dragOver: false
          };
        } catch (err: any) {
          // Planted missing defect (e.g. K05 udyam document file missing)
          updated[dtype] = {
            file: null,
            status: 'Not Uploaded',
            previewUrl: null,
            error: 'Document file not found (Planted missing defect in specimen)',
            dragOver: false
          };
        }
      }
      setDocFiles(updated);
      setValidationResult(null);
      setOcrResult(null);
      setIdentifierValidation(null);
      setIdentifiersConfirmed(false);
      setGstLookup(null);
      setUdyamLookup(null);
    } catch (err) {
      console.error(err);
    } finally {
      setAttachLoading(false);
    }
  };

  // File validation
  const validateSelectedFile = (file: File): string | null => {
    const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg'];
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedExtensions.includes(ext)) {
      return `Invalid format "${ext}". Accepted formats: PDF, PNG, JPG, JPEG.`;
    }
    const maxBytes = 10 * 1024 * 1024; // 10MB
    if (file.size > maxBytes) {
      return `File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds 10 MB limit.`;
    }
    return null;
  };

  // Handle single file upload
  const handleFileUpload = (docType: DocType, file: File) => {
    const errorMsg = validateSelectedFile(file);
    if (errorMsg) {
      setDocFiles(prev => ({
        ...prev,
        [docType]: {
          ...prev[docType],
          error: errorMsg
        }
      }));
      return;
    }

    // Revoke previous preview URL if present
    if (docFiles[docType].previewUrl) {
      URL.revokeObjectURL(docFiles[docType].previewUrl!);
    }

    let previewUrl: string | null = null;
    if (file.type.startsWith('image/')) {
      previewUrl = URL.createObjectURL(file);
    }

    setDocFiles(prev => ({
      ...prev,
      [docType]: {
        file,
        status: 'Uploaded',
        previewUrl,
        error: null,
        dragOver: false
      }
    }));
    setValidationResult(null);
    if (docType === 'gst_certificate' || docType === 'udyam_certificate') {
      setOcrResult(null);
      setIdentifierValidation(null);
      setIdentifiersConfirmed(false);
      setGstLookup(null);
      setUdyamLookup(null);
    }
  };

  // Remove document
  const handleRemoveFile = (docType: DocType) => {
    if (docFiles[docType].previewUrl) {
      URL.revokeObjectURL(docFiles[docType].previewUrl!);
    }
    setDocFiles(prev => ({
      ...prev,
      [docType]: {
        file: null,
        status: 'Not Uploaded',
        previewUrl: null,
        error: null,
        dragOver: false
      }
    }));
    setValidationResult(null);
    if (docType === 'gst_certificate' || docType === 'udyam_certificate') {
      setOcrResult(null);
      setIdentifierValidation(null);
      setIdentifiersConfirmed(false);
      setGstLookup(null);
      setUdyamLookup(null);
    }
  };

  // Drag and drop handlers
  const handleDragOver = (docType: DocType, e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!docFiles[docType].dragOver) {
      setDocFiles(prev => ({
        ...prev,
        [docType]: { ...prev[docType], dragOver: true }
      }));
    }
  };

  const handleDragLeave = (docType: DocType, e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDocFiles(prev => ({
      ...prev,
      [docType]: { ...prev[docType], dragOver: false }
    }));
  };

  const handleDrop = (docType: DocType, e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDocFiles(prev => ({
      ...prev,
      [docType]: { ...prev[docType], dragOver: false }
    }));
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(docType, e.dataTransfer.files[0]);
    }
  };

  // Mock registry query
  const handleExtractIdentifiers = async () => {
    const gstFile = docFiles.gst_certificate.file;
    const udyamFile = docFiles.udyam_certificate.file;
    if (!gstFile || !udyamFile) return;
    setOcrLoading(true);
    setOcrResult(null);
    setIdentifierValidation(null);
    setIdentifiersConfirmed(false);
    setGstLookup(null);
    setUdyamLookup(null);
    try {
      const data = new FormData();
      data.append('gst_certificate', gstFile);
      data.append('udyam_certificate', udyamFile);
      const result = await extractKycIdentifiers(data);
      setOcrResult(result);
      if (result.gstin?.value) setGstin(result.gstin.value);
      if (result.udyam?.value) setUdyamNumber(result.udyam.value);
    } catch (err: any) {
      alert(err.message || 'OCR extraction failed. Re-upload a clearer certificate.');
    } finally {
      setOcrLoading(false);
    }
  };

  const handleValidateIdentifiers = async () => {
    try {
      const result = await validateKycIdentifiers(gstin, udyamNumber);
      setIdentifierValidation(result);
      setIdentifiersConfirmed(false);
      setGstLookup(null);
      setUdyamLookup(null);
    } catch (err: any) {
      alert(err.message || 'Identifier format check failed.');
    }
  };

  const handleLookup = async () => {
    if (!identifiersConfirmed || !identifierValidation?.gstin?.valid || !identifierValidation?.udyam?.valid) return;
    setLookupLoading(true);
    setLookupError(null);
    try {
      if (gstin) {
        const gRes = await lookupGstin(gstin);
        setGstLookup(gRes);
      }
      if (udyamNumber) {
        const uRes = await lookupUdyam(udyamNumber);
        setUdyamLookup(uRes);
      }
    } catch (e) {
      console.error(e);
      setLookupError('Simulated registry lookup failed. Check the connection and try again.');
    } finally {
      setLookupLoading(false);
    }
  };

  // Check upload completion
  const allFourUploaded = Boolean(
    docFiles.gst_certificate.file &&
    docFiles.udyam_certificate.file &&
    docFiles.signatory_id.file &&
    docFiles.address_proof.file
  );

  const lookupCompleted = Boolean(gstLookup && udyamLookup);

  const canExecute = Boolean(
    consentGiven &&
    businessName.trim() &&
    applicantName.trim() &&
    identifiersConfirmed &&
    lookupCompleted &&
    allFourUploaded &&
    !validating
  );

  // Execute verification
  const handleRunValidation = async () => {
    if (!canExecute) return;
    setValidating(true);

    // Update document statuses to 'Processing'
    setDocFiles(prev => ({
      gst_certificate: { ...prev.gst_certificate, status: 'Processing' },
      udyam_certificate: { ...prev.udyam_certificate, status: 'Processing' },
      signatory_id: { ...prev.signatory_id, status: 'Processing' },
      address_proof: { ...prev.address_proof, status: 'Processing' }
    }));

    try {
      const formData = new FormData();
      formData.append('business_name', businessName);
      formData.append('applicant_name', applicantName);
      formData.append('applicant_role', applicantRole);
      if (gstin) formData.append('gstin', gstin);
      if (udyamNumber) formData.append('udyam_number', udyamNumber);
      formData.append('consent_given', String(consentGiven));
      formData.append('identifiers_confirmed', String(identifiersConfirmed));
      formData.append('purposes', JSON.stringify(purposes));
      formData.append('quote_id', quoteData?.quote_id || 'DEMO-QUOTE');

      if (docFiles.gst_certificate.file) {
        formData.append('gst_certificate', docFiles.gst_certificate.file);
      }
      if (docFiles.udyam_certificate.file) {
        formData.append('udyam_certificate', docFiles.udyam_certificate.file);
      }
      if (docFiles.signatory_id.file) {
        formData.append('signatory_id', docFiles.signatory_id.file);
      }
      if (docFiles.address_proof.file) {
        formData.append('address_proof', docFiles.address_proof.file);
      }

      const res = await verifyKycDocuments(formData);
      setValidationResult(res);

      // Update individual document statuses from backend
      if (res.document_results) {
        setDocFiles(prev => {
          const next = { ...prev };
          for (const [key, docRes] of Object.entries(res.document_results)) {
            const k = key as DocType;
            if (next[k]) {
              let statusBadge: UploadedDocState['status'] = 'Verified';
              if ((docRes as any).status === 'NEEDS_REVIEW') statusBadge = 'Needs Review';
              else if ((docRes as any).status === 'FAILED') statusBadge = 'Failed';
              else if ((docRes as any).status === 'NOT_UPLOADED') statusBadge = 'Not Uploaded';
              else statusBadge = 'Verified';

              next[k] = { ...next[k], status: statusBadge };
            }
          }
          return next;
        });
      }

      if (res.overall_status === 'PASS' || res.overall_status === 'REVIEW_REQUIRED') {
        onKycApproved(res);
      }
    } catch (err: any) {
      console.error(err);
      alert(err.message || 'Verification execution failed.');
    } finally {
      setValidating(false);
    }
  };

  // Helper for document status pill style
  const getStatusBadge = (status: UploadedDocState['status']) => {
    switch (status) {
      case 'Not Uploaded':
        return 'bg-slate-100 text-slate-600 border border-slate-300';
      case 'Uploaded':
        return 'bg-blue-50 text-blue-700 border border-blue-200';
      case 'Processing':
        return 'bg-amber-50 text-amber-700 border border-amber-300 animate-pulse';
      case 'Verified':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-300 font-bold';
      case 'Needs Review':
        return 'bg-amber-100 text-amber-800 border border-amber-300 font-bold';
      case 'Failed':
        return 'bg-red-50 text-red-700 border border-red-300 font-bold';
    }
  };

  // Helper to render individual document upload card
  const renderDocumentCard = (
    docType: DocType,
    title: string,
    spec: string,
    description: string
  ) => {
    const docState = docFiles[docType];
    const isUploaded = Boolean(docState.file);

    return (
      <div 
        onDragOver={(e) => handleDragOver(docType, e)}
        onDragLeave={(e) => handleDragLeave(docType, e)}
        onDrop={(e) => handleDrop(docType, e)}
        className={`p-4 rounded-xl border transition-all ${
          docState.dragOver 
            ? 'border-red-500 bg-red-50/50 shadow-md ring-2 ring-red-400' 
            : isUploaded 
            ? 'border-slate-300 bg-white shadow-sm' 
            : 'border-slate-200 bg-slate-50'
        }`}
      >
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
              isUploaded ? 'bg-red-100 text-red-600' : 'bg-slate-200 text-slate-500'
            }`}>
              {docState.file?.name.endsWith('.pdf') ? (
                <File className="w-4 h-4 text-red-600" />
              ) : isUploaded ? (
                <ImageIcon className="w-4 h-4 text-red-600" />
              ) : (
                <FileText className="w-4 h-4 text-slate-500" />
              )}
            </div>
            <div>
              <span className="font-bold text-slate-900 text-xs block">{title}</span>
              <span className="text-[10px] text-slate-500">{spec}</span>
            </div>
          </div>

          <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full ${getStatusBadge(docState.status)}`}>
            {docState.status}
          </span>
        </div>

        <p className="text-[11px] text-slate-500 mb-3">{description}</p>

        {/* Upload Controls / File Info */}
        {isUploaded ? (
          <div className="space-y-2 pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between text-xs bg-slate-50 p-2 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 overflow-hidden">
                {docState.previewUrl ? (
                  <img 
                    src={docState.previewUrl} 
                    alt="Preview" 
                    className="w-7 h-7 object-cover rounded border border-slate-200 flex-shrink-0" 
                  />
                ) : (
                  <File className="w-5 h-5 text-red-500 flex-shrink-0" />
                )}
                <div className="truncate">
                  <span className="font-semibold text-slate-800 text-[11px] block truncate" title={docState.file!.name}>
                    {docState.file!.name}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {(docState.file!.size / 1024).toFixed(1)} KB · {docState.file!.type || 'application/octet-stream'}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  type="button"
                  onClick={() => fileInputRefs[docType].current?.click()}
                  className="px-2 py-1 text-[10px] font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 rounded shadow-sm cursor-pointer"
                  title="Replace file"
                >
                  Replace
                </button>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(docType)}
                  className="p-1 text-slate-400 hover:text-red-600 rounded cursor-pointer"
                  title="Remove file"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100">
            <span className="text-[10px] text-slate-400">PDF, PNG, JPG (Max 10MB)</span>
            <button
              type="button"
              onClick={() => fileInputRefs[docType].current?.click()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:border-red-400 hover:text-red-600 shadow-sm transition-all cursor-pointer"
            >
              <Upload className="w-3 h-3 text-red-600" />
              <span>Upload Document</span>
            </button>
          </div>
        )}

        {/* Hidden File Input */}
        <input 
          type="file" 
          ref={fileInputRefs[docType]}
          accept=".pdf,image/png,image/jpeg,image/jpg"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFileUpload(docType, e.target.files[0]);
            }
          }}
          className="hidden" 
        />

        {/* Error message if validation failed */}
        {docState.error && (
          <div className="mt-2 text-[10px] text-red-600 bg-red-50 p-1.5 rounded border border-red-200 flex items-center gap-1">
            <AlertCircle className="w-3 h-3 flex-shrink-0" />
            <span>{docState.error}</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6">
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Module 3 · Smart Digital KYC & Genuine Document Verification</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Instant Regulatory Verification Under DPDP Act, 2023
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Document-driven OCR verification against 3,534 GSTINs and 2,723 Udyam certificates with DoT compliance checks.
          </p>
        </div>

        {/* Quick Presets for Demo - All 12 Specimens */}
        <div className="flex flex-wrap items-center gap-2 bg-slate-100 p-2 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold uppercase text-slate-500 whitespace-nowrap">Test Specimen (K01–K12):</span>
          <select
            value={activeSpecimenId}
            onChange={(e) => loadPreset(e.target.value)}
            className="bg-white border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            {allSpecimens.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
            allSpecimens.find(s => s.id === activeSpecimenId)?.status === 'PASS'
              ? 'bg-emerald-100 text-emerald-800'
              : allSpecimens.find(s => s.id === activeSpecimenId)?.status === 'FAILED'
              ? 'bg-red-100 text-red-800'
              : 'bg-amber-100 text-amber-800'
          }`}>
            {allSpecimens.find(s => s.id === activeSpecimenId)?.status}
          </span>

          <button
            type="button"
            onClick={handleAutoAttachSpecimens}
            disabled={attachLoading}
            className="flex items-center gap-1 px-2.5 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer disabled:opacity-50"
            title="Auto-attach genuine specimen documents for instant verification testing"
          >
            {attachLoading ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <Sparkles className="w-3 h-3 text-yellow-300" />
            )}
            <span>Auto-Attach Specimen Files</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Input Form & Uploads */}
        <div className="lg:col-span-2 space-y-6">
          {/* STEP 1: DPDP Act Consent Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Lock className="w-4 h-4 text-emerald-600" />
                  <span>Step 1: Transparent DPDP Act, 2023 Consent</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Purpose-specific notice required prior to accessing business verification registries.
                </p>
              </div>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                DPDP-2026-V1.0
              </span>
            </div>

            <div className="space-y-3 bg-slate-50 rounded-xl p-4 border border-slate-100 text-xs">
              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={purposes.gstin_lookup}
                  onChange={(e) => setPurposes({ ...purposes, gstin_lookup: e.target.checked })}
                  className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500"
                />
                <div>
                  <span className="font-semibold text-slate-900">GSTIN Verification Purpose</span>
                  <p className="text-slate-500">Query mock GST portal to confirm active status, legal name, and tax filing location.</p>
                </div>
              </label>

              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={purposes.udyam_verification}
                  onChange={(e) => setPurposes({ ...purposes, udyam_verification: e.target.checked })}
                  className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500"
                />
                <div>
                  <span className="font-semibold text-slate-900">Udyam MSME Registry Purpose</span>
                  <p className="text-slate-500">Query mock MSME registry to confirm micro/small enterprise class.</p>
                </div>
              </label>

              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={purposes.telecom_regulatory_compliance}
                  onChange={(e) => setPurposes({ ...purposes, telecom_regulatory_compliance: e.target.checked })}
                  className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500"
                />
                <div>
                  <span className="font-semibold text-slate-900">Department of Telecom (DoT) Mandatory KYC</span>
                  <p className="text-slate-500">Verify authorized signatory identity and physical premises address proof.</p>
                </div>
              </label>

              <div className="border-t border-slate-200 pt-3 flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer font-bold text-slate-900">
                  <input
                    type="checkbox"
                    checked={consentGiven}
                    onChange={(e) => setConsentGiven(e.target.checked)}
                    className="rounded text-emerald-600 focus:ring-emerald-500"
                  />
                  <span>I grant explicit purpose-bound digital consent as the authorized signatory.</span>
                </label>
              </div>
            </div>
          </div>

          {/* STEP 2: Business Identification & Lookup */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <Search className="w-4 h-4 text-red-600" />
              <span>Step 2: Business Identification & Mock Registry Lookup</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Business Entity Name
                </label>
                <input
                  type="text"
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  GSTIN (15 Alphanumeric)
                </label>
                <input
                  type="text"
                  value={gstin}
                  onChange={(e) => {
                    setGstin(e.target.value.toUpperCase());
                    setIdentifierValidation(null); setIdentifiersConfirmed(false); setGstLookup(null); setUdyamLookup(null);
                  }}
                  placeholder="e.g. 19EOGXH4115Y1ZL"
                  maxLength={15}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-mono focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
                <p className="mt-1 text-[11px] text-slate-500">If OCR misreads a character, correct it from your certificate, check the number format, then confirm it before lookup.</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Udyam Registration Number
                </label>
                <input
                  type="text"
                  value={udyamNumber}
                  onChange={(e) => {
                    setUdyamNumber(e.target.value.toUpperCase());
                    setIdentifierValidation(null); setIdentifiersConfirmed(false); setGstLookup(null); setUdyamLookup(null);
                  }}
                  placeholder="UDYAM-XX-00-XXXXXXX"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-mono focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Authorized Signatory Name & Role
                </label>
                <input
                  type="text"
                  value={applicantName}
                  onChange={(e) => setApplicantName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>
            </div>

            {ocrResult && (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs space-y-2">
                <p className="font-bold text-slate-800">OCR extraction review — check and correct both numbers before registry lookup.</p>
                {(['gstin', 'udyam'] as const).map((key) => {
                  const item = ocrResult[key];
                  const low = !item || item.confidence < 0.8;
                  return (
                    <div key={key} className={`rounded-lg border p-2 ${low || !item?.validation?.valid ? 'border-amber-300 bg-amber-50' : 'border-emerald-200 bg-white'}`}>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="font-bold text-slate-800">{key === 'gstin' ? 'GSTIN' : 'Udyam number'}</span>
                        <span className={low ? 'font-semibold text-amber-800' : 'text-slate-600'}>Number confidence: {Math.round((item?.confidence || 0) * 100)}% · Document OCR: {Math.round((item?.document_confidence || 0) * 100)}% · {item?.engine || 'OCR unavailable'}</span>
                      </div>
                      {item?.value && <p className="mt-1 font-mono font-semibold text-slate-900">OCR candidate: {item.value}</p>}
                      <p className={`mt-1 ${item?.validation?.valid ? 'text-emerald-800' : 'text-red-700'}`}>
                        {item?.validation?.valid ? 'Extracted format is valid.' : item?.validation?.reason || 'Number was not extracted. Enter it manually or re-upload a clearer document.'}
                      </p>
                      {!item?.value && <p className="mt-1 text-amber-900">{item?.engine && item.engine !== 'none' ? `OCR read ${item.recognized_text_length || 0} characters but did not find a complete ${key === 'gstin' ? 'GSTIN' : 'Udyam number'}. Re-upload a clearer, upright image or enter the printed number manually.` : 'No OCR engine text was returned. Confirm RapidOCR is installed in the backend Python environment and restart the backend.'}</p>}
                      {item?.fields && <p className="mt-1 text-slate-600">{key === 'gstin' ? `Legal name: ${item.fields.legal_name || 'not extracted'} · Trade name: ${item.fields.trade_name || 'not extracted'} · State: ${item.fields.state || 'not extracted'}` : `Enterprise: ${item.fields.enterprise_name || 'not extracted'} · Organisation: ${item.fields.organisation_type || 'not extracted'} · Registration date: ${item.fields.registration_date || 'not extracted'}`}</p>}
                    </div>
                  );
                })}
                <p className="text-slate-500">OCR and format checks do not establish registration status. Registry lookup below uses the project’s simulated local dataset.</p>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-3">
              <button type="button" onClick={handleValidateIdentifiers} className="px-3 py-2 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-700 hover:bg-slate-50">
                Check number formats
              </button>
              {identifierValidation && (
                <span className={`text-xs font-semibold ${identifierValidation.gstin.valid && identifierValidation.udyam.valid ? 'text-emerald-700' : 'text-red-700'}`}>
                  {identifierValidation.gstin.valid && identifierValidation.udyam.valid ? 'Both number formats passed.' : `${!identifierValidation.gstin.valid ? `GSTIN: ${identifierValidation.gstin.reason} ` : ''}${!identifierValidation.udyam.valid ? `Udyam: ${identifierValidation.udyam.reason}` : ''}`}
                </span>
              )}
            </div>
            {identifierValidation?.gstin?.valid && identifierValidation?.udyam?.valid && (
              <label className="flex items-start gap-2 rounded-lg border border-slate-200 bg-white p-3 text-xs text-slate-700">
                <input type="checkbox" checked={identifiersConfirmed} onChange={(e) => setIdentifiersConfirmed(e.target.checked)} className="mt-0.5 rounded text-emerald-600" />
                <span>I reviewed and confirm the GSTIN and Udyam number above. I understand the next step checks the simulated local registry separately.</span>
              </label>
            )}

            <div className="flex items-center gap-3">
              <button
                onClick={handleLookup}
                disabled={lookupLoading || !identifiersConfirmed || !identifierValidation?.gstin?.valid || !identifierValidation?.udyam?.valid}
                className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold cursor-pointer transition-all disabled:bg-slate-300 disabled:cursor-not-allowed"
              >
                <Search className="w-3.5 h-3.5" />
                <span>{lookupLoading ? 'Querying Simulated Registries...' : 'Check Simulated Registries'}</span>
              </button>
              <span className="text-[11px] text-slate-400">
                {lookupCompleted ? '✓ Simulated registry query complete' : 'Requires successful format validation and your confirmation'}
              </span>
            </div>
            {lookupError && <p role="alert" className="text-xs text-red-700">{lookupError}</p>}

            {/* Live Lookup Status Badges */}
            {(gstLookup || udyamLookup) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-100 text-xs">
                {gstLookup && (
                  <div className={`p-3 rounded-xl border ${
                    gstLookup.valid ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-red-50 border-red-200 text-red-900'
                  }`}>
                    <div className="flex items-center justify-between font-bold mb-1">
                      <span>Simulated GST registry: {gstLookup.status}</span>
                      {gstLookup.valid ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertOctagon className="w-4 h-4 text-red-600" />}
                    </div>
                    <p className="text-[11px]">{gstLookup.message}</p>
                    {gstLookup.data && (
                      <div className="mt-1 text-[10px] text-slate-600 space-y-0.5">
                        <p>Legal: {gstLookup.data.legal_name}</p>
                        <p>Address: {gstLookup.data.principal_place_of_business}</p>
                      </div>
                    )}
                  </div>
                )}

                {udyamLookup && (
                  <div className={`p-3 rounded-xl border ${
                    udyamLookup.valid ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-red-50 border-red-200 text-red-900'
                  }`}>
                    <div className="flex items-center justify-between font-bold mb-1">
                      <span>Simulated Udyam registry: {udyamLookup.status}</span>
                      {udyamLookup.valid ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertOctagon className="w-4 h-4 text-red-600" />}
                    </div>
                    <p className="text-[11px]">{udyamLookup.message}</p>
                    {udyamLookup.data && (
                      <div className="mt-1 text-[10px] text-slate-600 space-y-0.5">
                        <p>Enterprise: {udyamLookup.data.enterprise_name}</p>
                        <p>Class: {udyamLookup.data.enterprise_type} ({udyamLookup.data.city})</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* STEP 3: Individual Document Upload Controls */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Upload className="w-4 h-4 text-red-600" />
                  <span>Step 3: Document Uploads & Genuine OCR Verification</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Attach all 4 official documents (PDF, PNG, JPG). Drag and drop or browse files.
                </p>
              </div>
              <span className="text-[10px] text-slate-500 font-medium">
                {Object.values(docFiles).filter(d => d.file).length} of 4 Uploaded
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              {renderDocumentCard(
                'gst_certificate',
                'GST Certificate',
                'Form REG-06 spec',
                'Extracts GSTIN, legal business name, and registered operational address.'
              )}
              {renderDocumentCard(
                'udyam_certificate',
                'Udyam Registration',
                'Ministry of MSME spec',
                'Extracts Udyam registration number, enterprise name, and MSME category.'
              )}
              {renderDocumentCard(
                'signatory_id',
                'Signatory Photo ID',
                'Aadhaar / Voter ID / PAN',
                'Extracts authorized signatory name. ID numbers are masked for DPDP Act privacy.'
              )}
              {renderDocumentCard(
                'address_proof',
                'Address Proof (Electricity Bill)',
                'Max 90 days validity',
                'Extracts consumer name, premises address, and bill issue date (<=90 days required).'
              )}
            </div>

            <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-3 flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-bold text-indigo-950">Extract and review identifiers</p>
                <p className="text-[11px] text-indigo-800">OCR reads the GST and Udyam certificates only. It does not query a registry.</p>
              </div>
              <button type="button" onClick={handleExtractIdentifiers}
                disabled={ocrLoading || !docFiles.gst_certificate.file || !docFiles.udyam_certificate.file}
                className="px-4 py-2 rounded-lg bg-indigo-700 hover:bg-indigo-800 text-white text-xs font-semibold disabled:bg-slate-300 disabled:cursor-not-allowed">
                {ocrLoading ? 'Processing certificates…' : 'Extract identifiers for review'}
              </button>
            </div>

            {/* Execution Button & Readiness Validation Message */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleRunValidation}
                disabled={!canExecute}
                className="w-full py-3.5 px-4 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-md shadow-red-600/30 transition-all cursor-pointer disabled:bg-slate-300 disabled:cursor-not-allowed disabled:shadow-none"
              >
                {validating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-white" />
                    <span>Executing Genuine OCR & Cross-Document Validation...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-yellow-300" />
                    <span>Execute Smart KYC Verification</span>
                  </>
                )}
              </button>

              {!canExecute && (
                <div className="mt-2 text-center text-[11px] text-slate-500">
                  {!consentGiven && <span className="text-red-500 block">• Step 1 statutory DPDP consent is required.</span>}
                  {(!businessName.trim() || !applicantName.trim()) && <span className="text-red-500 block">• Step 2 business entity and signatory names are required.</span>}
                  {!lookupCompleted && <span className="text-amber-600 block">• Click "Instant Mock Registry Lookup" in Step 2 to query registry records.</span>}
                  {!allFourUploaded && <span className="text-slate-500 block">• All 4 required documents must be uploaded before executing verification.</span>}
                </div>
              )}
            </div>
          </div>

          {/* DEDICATED RESULTS SECTION (Rendered directly below Step 3 upon verification) */}
          {validationResult && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-md p-6 space-y-6 animate-fade-in">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Verification Outcome
                  </span>
                  <h3 className="text-lg font-black text-slate-900 mt-0.5">
                    Structured Cross-Document Evaluation
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  {validationResult.overall_status === 'PASS' && (
                    <span className="px-4 py-1.5 rounded-full bg-emerald-100 text-emerald-800 font-black text-xs flex items-center gap-1.5 border border-emerald-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      KYC APPROVED (PASS)
                    </span>
                  )}
                  {validationResult.overall_status === 'REVIEW_REQUIRED' && (
                    <span className="px-4 py-1.5 rounded-full bg-amber-100 text-amber-800 font-black text-xs flex items-center gap-1.5 border border-amber-300">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      OFFICER REVIEW REQUIRED
                    </span>
                  )}
                  {validationResult.overall_status === 'FAILED' && (
                    <span className="px-4 py-1.5 rounded-full bg-red-100 text-red-800 font-black text-xs flex items-center gap-1.5 border border-red-300">
                      <AlertOctagon className="w-4 h-4 text-red-600" />
                      VERIFICATION FAILED
                    </span>
                  )}
                  <span className="text-xs text-slate-500 font-medium">
                    OCR Confidence: {Math.round(validationResult.confidence_score * 100)}%
                  </span>
                </div>
              </div>

              {/* 4 Individual Document Breakdown Cards */}
              {validationResult.document_results && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                    Individual Document Extraction & Match Analysis
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {Object.entries(validationResult.document_results).map(([docKey, docInfo]: [string, any]) => (
                      <div key={docKey} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-xs">
                            {docInfo.doc_name || docKey}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getStatusBadge(docInfo.status)}`}>
                            {docInfo.status}
                          </span>
                        </div>

                        {/* Extracted Fields Summary */}
                        {docInfo.extracted_fields && Object.keys(docInfo.extracted_fields).length > 0 && (
                          <div className="bg-white p-2.5 rounded-lg border border-slate-100 text-[11px] space-y-1 text-slate-600">
                            {docInfo.extracted_fields.gstin && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">{docInfo.extracted_fields.gstin_source === 'MANUAL_CONFIRMED' ? 'Manually confirmed GSTIN:' : 'Extracted GSTIN:'}</span>
                                <span className="font-mono font-bold text-slate-800">{docInfo.extracted_fields.gstin}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.gstin_source === 'MANUAL_CONFIRMED' && docInfo.extracted_fields.gstin_ocr_candidate && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">OCR candidate:</span>
                                <span className="font-mono text-amber-800">{docInfo.extracted_fields.gstin_ocr_candidate}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.trade_name && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Trade Name:</span>
                                <span className="font-medium text-slate-800">{docInfo.extracted_fields.trade_name}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.udyam_number && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Udyam No:</span>
                                <span className="font-mono font-bold text-slate-800">{docInfo.extracted_fields.udyam_number}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.enterprise_name && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Enterprise:</span>
                                <span className="font-medium text-slate-800">{docInfo.extracted_fields.enterprise_name}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.signatory_name && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Signatory:</span>
                                <span className="font-medium text-slate-800">{docInfo.extracted_fields.signatory_name}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.masked_id && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Masked ID:</span>
                                <span className="font-mono text-slate-700 bg-slate-100 px-1 rounded">{docInfo.extracted_fields.masked_id}</span>
                              </div>
                            )}
                            {docInfo.extracted_fields.bill_date && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Bill Date:</span>
                                <span className="font-medium text-slate-800">
                                  {docInfo.extracted_fields.bill_date} ({docInfo.extracted_fields.days_old} days old)
                                </span>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Match/Mismatch Verification Checks */}
                        {docInfo.checks && docInfo.checks.length > 0 && (
                          <div className="space-y-1 pt-1">
                            {docInfo.checks.map((chk: any, idx: number) => (
                              <div key={idx} className="flex items-center justify-between text-[11px] p-1.5 rounded bg-white border border-slate-100">
                                <span className="font-medium text-slate-700">{chk.field}</span>
                                <span className={`font-bold px-1.5 py-0.2 rounded text-[10px] ${
                                  chk.status === 'MATCH'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : chk.status === 'EXPIRED'
                                    ? 'bg-amber-100 text-amber-800'
                                    : chk.status === 'MISMATCH'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-slate-100 text-slate-700'
                                }`}>
                                  {chk.status}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Document specific issues */}
                        {docInfo.issues && docInfo.issues.length > 0 && (
                          <div className="text-[10px] text-red-700 bg-red-50 p-2 rounded border border-red-200">
                            {docInfo.issues.map((iss: string, i: number) => (
                              <p key={i}>• {iss}</p>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detected Irregularities & Next Steps */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {validationResult.detected_issues && validationResult.detected_issues.length > 0 && (
                  <div className="bg-red-50 rounded-xl p-4 border border-red-200 text-xs">
                    <span className="font-bold text-red-900 block mb-1.5">Detected Irregularities:</span>
                    <ul className="space-y-1 text-red-800">
                      {validationResult.detected_issues.map((iss, i) => (
                        <li key={i} className="flex items-start gap-1">
                          <span>•</span>
                          <span>{iss}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {validationResult.corrective_actions && validationResult.corrective_actions.length > 0 && (
                  <div className="bg-sky-50 rounded-xl p-4 border border-sky-200 text-xs">
                    <span className="font-bold text-sky-900 block mb-1.5">Recommended Next Action:</span>
                    <p className="font-semibold text-sky-900 mb-1">
                      {validationResult.recommended_next_action || 'Proceed to Service Activation.'}
                    </p>
                    <ul className="space-y-1 text-sky-800">
                      {validationResult.corrective_actions.map((act, i) => (
                        <li key={i} className="flex items-start gap-1">
                          <span>→</span>
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Tamper-Evident Audit Trail */}
              {validationResult.audit_trail && (
                <div className="pt-2 border-t border-slate-100">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                    Tamper-Evident Statutory Audit Trail
                  </span>
                  <div className="space-y-1.5 text-[11px] text-slate-600 max-h-40 overflow-y-auto pr-1">
                    {validationResult.audit_trail.map((item, idx) => (
                      <div key={idx} className="p-2 rounded bg-slate-50 border border-slate-100 flex items-center justify-between">
                        <div>
                          <span className="font-semibold text-slate-800">{item.event}</span>
                          <span className="text-[10px] text-slate-400 ml-2">({item.agent})</span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {item.timestamp?.slice(11, 19)} UTC
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Button for Approved Verification */}
              {validationResult.overall_status === 'PASS' && (
                <button
                  type="button"
                  onClick={() => onKycApproved(validationResult)}
                  className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-md shadow-emerald-600/30 transition-all cursor-pointer"
                >
                  <span>Proceed to Service Activation</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Right Sidebar: Guidelines & Simulated Registry Disclosure */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4 text-xs">
            <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Document Verification Guidelines</span>
            </h4>

            <div className="space-y-2.5 text-slate-600">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="font-semibold text-slate-800 block">Form REG-06 GST Certificate:</span>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Must display legal name and 15-character GSTIN. Active tax status validated against mock registry.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="font-semibold text-slate-800 block">Udyam MSME Registration:</span>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Must match UDYAM-XX-00-XXXXXXX specification. Enterprise category verified for regulatory concessions.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="font-semibold text-slate-800 block">Authorized Signatory Photo ID:</span>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Full ID numbers are masked on ingestion to guarantee DPDP Act 2023 data minimization compliance.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="font-semibold text-slate-800 block">Physical Premises Address Proof:</span>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Electricity bill must be dated within 90 days of reference date (2026-07-15) per DoT regulations.
                </p>
              </div>
            </div>

            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 text-[11px] space-y-1">
              <span className="font-bold block flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                <span>Simulated Verification Disclosure</span>
              </span>
              <p className="text-amber-800">
                This hackathon prototype evaluates uploads against mock registries and synthetic test documents. No live government APIs are invoked.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
