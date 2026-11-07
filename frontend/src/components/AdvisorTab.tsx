import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Sparkles, Check, ArrowRight, ArrowLeft, Volume2, ShieldCheck, 
  Store, Stethoscope, Utensils, Factory, Building, HelpCircle, 
  Wifi, Smartphone, CreditCard, MessageSquare, Camera, Mail, ShieldAlert,
  Mic, MicOff, Building2, MapPin, CheckCircle2, AlertCircle, Tag, Info,
  RotateCcw, Loader2, Sparkle, Square, Play
} from 'lucide-react';
import type { AdvisorResponse, RecommendedTier } from '../types';
import { processVoiceTranscript } from '../services/api';

interface AdvisorTabProps {
  formData: any;
  setFormData: React.Dispatch<React.SetStateAction<any>>;
  onGetRecommendations: () => Promise<void>;
  recommendations: AdvisorResponse | null;
  loading: boolean;
  onSelectTier: (tier: RecommendedTier) => void;
  language: string;
  onApplyVoiceRecommendations?: (data: any) => void;
}

export const AdvisorTab: React.FC<AdvisorTabProps> = ({
  formData,
  setFormData,
  onGetRecommendations,
  recommendations,
  loading,
  onSelectTier,
  language,
  onApplyVoiceRecommendations
}) => {
  const [step, setStep] = useState(1);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcriptNotice, setTranscriptNotice] = useState<string | null>(null);

  // Pause-Tolerant Voice Assistant State & Refs
  const [voiceTranscript, setVoiceTranscript] = useState<string>('');
  const [interimTranscript, setInterimTranscript] = useState<string>('');
  const [voiceStatus, setVoiceStatus] = useState<'idle' | 'listening' | 'ready' | 'processing' | 'done' | 'error'>('idle');
  const [isProcessingTranscript, setIsProcessingTranscript] = useState<boolean>(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [extractedResult, setExtractedResult] = useState<any | null>(null);
  const [showVoiceCard, setShowVoiceCard] = useState<boolean>(false);
  const [recordingSeconds, setRecordingSeconds] = useState<number>(0);

  const recognitionRef = useRef<any>(null);
  const isRecordingRef = useRef<boolean>(false);
  const finalTranscriptRef = useRef<string>('');
  const restartTimeoutRef = useRef<any>(null);
  const timerIntervalRef = useRef<any>(null);

  // Stop recording cleanly
  const stopRecording = useCallback((keepInterim = true) => {
    isRecordingRef.current = false;
    setIsListening(false);

    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        try {
          recognitionRef.current.abort();
        } catch {}
      }
      recognitionRef.current = null;
    }

    // Merge any trailing interim text into final
    setInterimTranscript((prevInterim) => {
      if (keepInterim && prevInterim.trim()) {
        const appended = finalTranscriptRef.current
          ? `${finalTranscriptRef.current.trim()} ${prevInterim.trim()}`
          : prevInterim.trim();
        finalTranscriptRef.current = appended;
        setVoiceTranscript(appended);
      }
      return '';
    });

    setVoiceStatus((prev) => {
      if (prev === 'error') return 'error';
      return finalTranscriptRef.current.trim() ? 'ready' : 'idle';
    });
  }, []);

  // Initialize and start recognition instance
  const initAndStartRecognition = useCallback(() => {
    if (!isRecordingRef.current) return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.lang = language === 'hi' ? 'hi-IN' : language === 'ta' ? 'ta-IN' : 'en-IN';

      recognition.onstart = () => {
        if (!isRecordingRef.current) {
          try { recognition.abort(); } catch {}
          return;
        }
        setIsListening(true);
        setVoiceStatus('listening');
        setVoiceError(null);
      };

      recognition.onresult = (event: any) => {
        let currentInterim = '';
        let newFinalChunk = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i];
          const text = item[0]?.transcript || '';
          if (item.isFinal) {
            newFinalChunk += (newFinalChunk ? ' ' : '') + text.trim();
          } else {
            currentInterim += (currentInterim ? ' ' : '') + text.trim();
          }
        }

        if (newFinalChunk) {
          const existing = finalTranscriptRef.current.trim();
          if (!existing) {
            finalTranscriptRef.current = newFinalChunk;
          } else if (!existing.endsWith(newFinalChunk)) {
            finalTranscriptRef.current = `${existing} ${newFinalChunk}`;
          }
          setVoiceTranscript(finalTranscriptRef.current);
          setInterimTranscript('');
          setVoiceStatus('listening');
        } else if (currentInterim) {
          setInterimTranscript(currentInterim);
        }
      };

      recognition.onerror = (event: any) => {
        const err = event.error;
        // Natural silence/pauses fire 'no-speech' in Chromium.
        // DO NOT terminate user recording session!
        if (err === 'no-speech') {
          return;
        }
        if (err === 'not-allowed' || err === 'service-not-allowed') {
          setVoiceError("Microphone access denied. Please allow microphone permissions in your browser.");
          setVoiceStatus('error');
          stopRecording(false);
          return;
        }
        if (err === 'audio-capture') {
          setVoiceError("No microphone device detected. Please verify microphone hardware.");
          setVoiceStatus('error');
          stopRecording(false);
          return;
        }
        // Other transient events (e.g. network or aborted during restart)
        console.warn("SpeechRecognition transient event:", err);
      };

      recognition.onend = () => {
        setInterimTranscript('');
        // If user is still actively recording, restart smoothly across pause
        if (isRecordingRef.current) {
          restartTimeoutRef.current = setTimeout(() => {
            if (isRecordingRef.current) {
              initAndStartRecognition();
            }
          }, 350);
        } else {
          setIsListening(false);
          if (voiceStatus !== 'error') {
            setVoiceStatus(finalTranscriptRef.current.trim() ? 'ready' : 'idle');
          }
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.warn("SpeechRecognition start exception:", err);
      // Attempt retry if recording is still active
      if (isRecordingRef.current) {
        restartTimeoutRef.current = setTimeout(() => {
          if (isRecordingRef.current) initAndStartRecognition();
        }, 500);
      }
    }
  }, [language, stopRecording, voiceStatus]);

  // Start continuous recording with 120s safety limit
  const startRecording = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is supported in Chrome & Edge browsers. You can also type directly in the fields or use the sample transcripts.");
      setShowVoiceCard(true);
      return;
    }

    // Clear any previous timers
    if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

    isRecordingRef.current = true;
    setIsListening(true);
    setShowVoiceCard(true);
    setVoiceStatus('listening');
    setVoiceError(null);
    setRecordingSeconds(0);
    setTranscriptNotice("Listening... Natural pauses are supported. Click 'Stop Recording' when finished.");

    // Start 120-second safety countdown
    const startTime = Date.now();
    timerIntervalRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setRecordingSeconds(elapsed);
      if (elapsed >= 120) {
        stopRecording(true);
      }
    }, 1000);

    initAndStartRecognition();
  }, [initAndStartRecognition, stopRecording]);

  // Master toggle button
  const toggleListening = () => {
    if (isRecordingRef.current) {
      stopRecording(true);
    } else {
      startRecording();
    }
  };

  // Cleanup on unmount or language switch
  useEffect(() => {
    return () => {
      isRecordingRef.current = false;
      if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch {}
      }
    };
  }, []);

  const handleProcessVoiceTranscript = async () => {
    // If currently recording, stop first and grab latest text
    if (isRecordingRef.current) {
      stopRecording(true);
    }

    const trimmed = (finalTranscriptRef.current || voiceTranscript).trim();
    if (!trimmed) {
      setVoiceError("Please speak or enter a voice transcript before processing.");
      return;
    }
    if (isProcessingTranscript) return;

    setIsProcessingTranscript(true);
    setVoiceError(null);
    setVoiceStatus('processing');

    try {
      const res = await processVoiceTranscript({ transcript: trimmed, language });
      setExtractedResult(res);
      setVoiceStatus('done');
      setTranscriptNotice("Voice requirements extracted & bundles computed");

      // Populate form data
      const prof = res.extracted_profile;
      setFormData((prev: any) => ({
        ...prev,
        business_name: prof.business_name || prev.business_name,
        business_type: prof.business_type || prev.business_type,
        segment: prof.segment || prev.segment,
        city: prof.operating_city || prev.city,
        city_tier: prof.city_tier || prev.city_tier,
        employee_count: prof.employee_count || prev.employee_count,
        num_sites: prof.number_of_sites || prev.num_sites,
        monthly_budget_inr: prof.monthly_budget || prev.monthly_budget_inr,
        need_sims: prof.need_sims ?? prev.need_sims,
        need_pos: prof.need_pos ?? prev.need_pos,
        need_whatsapp: prof.need_whatsapp ?? prev.need_whatsapp,
        need_cctv: prof.need_cctv ?? prev.need_cctv,
        cctv_cameras_count: prof.cctv_cameras_count ?? prev.cctv_cameras_count,
        need_cloud_email: prof.need_cloud_email ?? prev.need_cloud_email,
        need_cloud_backup: prof.need_cloud_backup ?? prev.need_cloud_backup,
        need_security: prof.need_security ?? prev.need_security,
        need_failover_backup: prof.need_failover_backup ?? prev.need_failover_backup,
        need_dedicated_leased_line: prof.need_dedicated_leased_line ?? prev.need_dedicated_leased_line,
        has_gstin: prof.has_gstin ?? prev.has_gstin,
        gstin: prof.gstin || prev.gstin
      }));

      // Apply recommendations to parent
      if (onApplyVoiceRecommendations) {
        onApplyVoiceRecommendations(res);
      }
      setStep(4);
    } catch (err: any) {
      console.error(err);
      setVoiceError(err.message || "Failed to extract business requirements from transcript.");
      setVoiceStatus('error');
    } finally {
      setIsProcessingTranscript(false);
    }
  };

  const handleLoadSample = (sampleText: string) => {
    if (isRecordingRef.current) {
      stopRecording(false);
    }
    finalTranscriptRef.current = sampleText;
    setVoiceTranscript(sampleText);
    setInterimTranscript('');
    setVoiceStatus('ready');
    setShowVoiceCard(true);
    setVoiceError(null);
    setTranscriptNotice("Transcript ready");
  };

  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    if (isSpeaking) {
      setIsSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    if (language === 'hi') utterance.lang = 'hi-IN';
    else if (language === 'ta') utterance.lang = 'ta-IN';
    else utterance.lang = 'en-IN';
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleNext = async () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      await onGetRecommendations();
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6">
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto mb-8">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 mb-3">
          <Sparkles className="w-3.5 h-3.5 text-red-600" />
          <span>Module 1 · Intelligent AI Business Advisor</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          One Conversation. <span className="text-red-600">The Exact Connectivity Bundle</span> Your Business Needs.
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          No complex jargon or pushy sales calls. Tell our AI Advisor about your business in English, Hindi, or Tamil, and get an authoritatively matched bundle backed by the official Accel Business product catalogue.
        </p>
      </div>

      {/* Progressive Step Stepper */}
      <div className="mb-6 max-w-2xl mx-auto">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-500 mb-2">
          <span className={step >= 1 ? 'text-red-600 font-bold' : ''}>1. Business Profile</span>
          <span className={step >= 2 ? 'text-red-600 font-bold' : ''}>2. Scale & Sites</span>
          <span className={step >= 3 ? 'text-red-600 font-bold' : ''}>3. Digital Tools</span>
          <span className={step >= 4 ? 'text-red-600 font-bold' : ''}>4. Budget & Tax</span>
        </div>
        <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
          <div 
            className="bg-red-600 h-full transition-all duration-300 rounded-full"
            style={{ width: `${(step / 4) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Voice Assistant Banner */}
      <div className="max-w-3xl mx-auto mb-4 bg-gradient-to-r from-red-50 via-slate-50 to-slate-50 p-4 rounded-xl border border-red-100 shadow-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold">
              <Volume2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-900 flex items-center gap-2">
                <span>Multilingual Voice Assistant ({language.toUpperCase()})</span>
                {voiceStatus === 'listening' && (
                  <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-red-600 bg-red-100/80 px-2 py-0.5 rounded-full animate-pulse border border-red-200">
                    <span className="w-2 h-2 rounded-full bg-red-600"></span>
                    <span>Listening... ({String(Math.floor(recordingSeconds / 60)).padStart(2, '0')}:{String(recordingSeconds % 60).padStart(2, '0')} / 02:00)</span>
                  </span>
                )}
                {voiceStatus === 'ready' && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded-full border border-emerald-200">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    Recording Complete
                  </span>
                )}
                {voiceStatus === 'processing' && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full animate-pulse border border-amber-200">
                    <Loader2 className="w-3 h-3 animate-spin text-amber-600" />
                    Processing with AI Advisor...
                  </span>
                )}
                {voiceStatus === 'done' && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold text-sky-700 bg-sky-100 px-2 py-0.5 rounded-full border border-sky-200">
                    <CheckCircle2 className="w-3 h-3 text-sky-600" />
                    Requirements Extracted
                  </span>
                )}
              </h4>
              <p className="text-[11px] text-slate-500">
                Speak or review your business requirements in English, Hindi, or Tamil. Continuous pause-tolerant capture enabled.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {isListening ? (
              <button
                type="button"
                onClick={() => stopRecording(true)}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold bg-red-600 hover:bg-red-700 text-white shadow-md shadow-red-600/30 transition-all cursor-pointer animate-pulse"
                title="Stop recording voice input"
              >
                <Square className="w-3 h-3 fill-white" />
                <span>Stop Recording ({String(Math.floor(recordingSeconds / 60)).padStart(2, '0')}:{String(recordingSeconds % 60).padStart(2, '0')})</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={startRecording}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white border border-slate-300 text-slate-700 hover:border-red-400 hover:text-red-600 shadow-sm transition-all cursor-pointer"
                title="Click and speak continuously with pause support"
              >
                <Mic className="w-3.5 h-3.5 text-red-600" />
                <span>Voice Input (Mic)</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowVoiceCard(!showVoiceCard)}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-xs font-semibold rounded-lg shadow-sm cursor-pointer"
              title="Open or hide the transcript editor"
            >
              <span>{showVoiceCard ? 'Hide Transcript' : 'View / Edit Transcript'}</span>
            </button>

            <button
              onClick={() => {
                const currentStepText = step === 1 
                  ? "Please tell us your business name and category" 
                  : step === 2 
                  ? "Please tell us your team size and number of locations" 
                  : step === 3 
                  ? "Select your digital connectivity and payment tools" 
                  : "Select your monthly budget and tax registration status";
                speakText(currentStepText);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-xs font-semibold rounded-lg shadow-sm cursor-pointer"
              title="Listen to questions in audio narration"
            >
              <Volume2 className="w-3.5 h-3.5 text-slate-600" />
              <span>{isSpeaking ? 'Stop Audio' : 'Listen'}</span>
            </button>
          </div>
        </div>

        {/* Interactive Transcript Submission Panel */}
        {(showVoiceCard || voiceTranscript || voiceStatus !== 'idle') && (
          <div className="pt-3 border-t border-red-100 space-y-2.5 animate-fade-in">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <span>Recognized Voice Transcript (Editable)</span>
                {voiceTranscript && (
                  <span className="text-[10px] text-slate-400 font-normal">
                    ({voiceTranscript.length} characters)
                  </span>
                )}
              </label>

              {/* Sample Quick-Pills for Instant Testing */}
              <div className="flex items-center gap-1.5 text-[10px]">
                <span className="text-slate-400 hidden sm:inline">Quick Test Samples:</span>
                <button
                  type="button"
                  onClick={() => handleLoadSample("I run a small grocery shop called Sri Lakshmi Stores in Chennai. I have one shop and around three employees. I need reliable internet for UPI payments, online billing and WhatsApp orders. I also want CCTV connectivity for security. My monthly budget is around 3000 rupees.")}
                  className="px-2 py-0.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-md font-medium cursor-pointer"
                  title="Load Sri Lakshmi Stores example"
                >
                  Sri Lakshmi (EN)
                </button>
                <button
                  type="button"
                  onClick={() => handleLoadSample("मेरी दिल्ली में बालाजी डेंटल क्लिनिक नाम की एक क्लिनिक है। हमारे पास 4 कर्मचारी हैं। मुझे ऑनलाइन बिलिंग, यूपीआई पेमेंट और सीसीटीवी सुरक्षा के लिए इंटरनेट चाहिए। मेरा मासिक बजट 5000 रुपये है।")}
                  className="px-2 py-0.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-md font-medium cursor-pointer"
                  title="Load Clinic in Hindi"
                >
                  Clinic (HI)
                </button>
                <button
                  type="button"
                  onClick={() => handleLoadSample("நான் சென்னையில் ஸ்ரீ முருகன் ரெஸ்டாரன்ட் என்ற உணவகம் நடத்துகிறேன். என்னிடம் 2 கடைகள் மற்றும் 6 ஊழியர்கள் உள்ளனர். எனக்கு ஆன்லைன் பில்லிங், வாட்ஸ்அப் ஆர்டர்கள் மற்றும் சிசிடிவி பாதுகாப்பு தேவை. என் மாதாந்திர பட்ஜெட் 8000 ரூபாய்.")}
                  className="px-2 py-0.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-md font-medium cursor-pointer"
                  title="Load Restaurant in Tamil"
                >
                  Restaurant (TA)
                </button>
              </div>
            </div>

            <div className="relative">
              <textarea
                value={isListening && interimTranscript ? (voiceTranscript ? `${voiceTranscript} ${interimTranscript}` : interimTranscript) : voiceTranscript}
                onChange={(e) => {
                  finalTranscriptRef.current = e.target.value;
                  setVoiceTranscript(e.target.value);
                  setInterimTranscript('');
                  setVoiceStatus(e.target.value.trim() ? 'ready' : 'idle');
                  setVoiceError(null);
                }}
                placeholder="Your spoken transcript will appear here automatically. You can speak naturally across pauses, or type/paste directly..."
                className="w-full p-3 rounded-xl border border-slate-300 bg-white font-sans text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 min-h-[85px]"
              />
              {isListening && (
                <div className="absolute bottom-2 right-2 flex items-center gap-1.5 text-[10px] text-red-600 bg-red-50/90 px-2 py-0.5 rounded border border-red-200 pointer-events-none">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-ping"></span>
                  <span>Continuous Listening Active (Pause-Tolerant)</span>
                </div>
              )}
            </div>

            {/* Error Message */}
            {voiceError && (
              <div className="p-2.5 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                <span>{voiceError}</span>
              </div>
            )}

            {/* Submission Controls */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              <div className="text-[11px] text-slate-500">
                {voiceStatus === 'ready' && (
                  <span className="text-emerald-700 font-medium">
                    ✓ Recording Complete. Click <strong>Process with AI Advisor</strong> to parse requirements and match catalogue bundles.
                  </span>
                )}
                {voiceStatus === 'listening' && (
                  <span className="text-red-600 font-medium animate-pulse flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span>
                    Listening across natural pauses... Click <strong>Stop Recording</strong> when finished.
                  </span>
                )}
                {voiceStatus === 'idle' && !voiceTranscript && (
                  <span>Click <strong>Voice Input</strong> or choose a test sample above.</span>
                )}
              </div>

              <div className="flex items-center gap-2">
                {voiceTranscript && (
                  <button
                    type="button"
                    onClick={() => {
                      setVoiceTranscript('');
                      setVoiceStatus('idle');
                      setVoiceError(null);
                      setExtractedResult(null);
                    }}
                    className="px-2.5 py-1.5 text-xs text-slate-500 hover:text-slate-700 font-semibold cursor-pointer"
                  >
                    Clear
                  </button>
                )}

                <button
                  type="button"
                  onClick={handleProcessVoiceTranscript}
                  disabled={isProcessingTranscript || !voiceTranscript.trim()}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold text-xs rounded-xl shadow-md shadow-red-600/30 transition-all cursor-pointer"
                >
                  {isProcessingTranscript ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Processing with AI Advisor...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                      <span>Process with AI Advisor</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Extracted Structured Requirements Card */}
        {extractedResult && (
          <div className="mt-3 p-4 bg-white rounded-xl border border-emerald-200 shadow-sm space-y-3 animate-fade-in">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-bold text-slate-900">
                  Extracted Business Requirements (Structured Profile)
                </span>
              </div>
              <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                Matched to Accel Business Catalogue (25 SKUs)
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Business Name</span>
                <span className="font-bold text-slate-900">{extractedResult.extracted_profile.business_name}</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Category</span>
                <span className="font-bold text-slate-900">{extractedResult.extracted_profile.business_category}</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Operating City</span>
                <span className="font-bold text-slate-900">
                  {extractedResult.extracted_profile.operating_city} (Tier {extractedResult.extracted_profile.city_tier})
                </span>
              </div>
              <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Scale & Budget</span>
                <span className="font-bold text-slate-900">
                  {extractedResult.extracted_profile.number_of_sites} Site · {extractedResult.extracted_profile.employee_count} Staff · ₹{extractedResult.extracted_profile.monthly_budget.toLocaleString()}/mo
                </span>
              </div>
            </div>

            {/* Extracted Requirements & Matched Products */}
            <div className="space-y-2">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Identified Requirements:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {extractedResult.extracted_profile.requirements.map((req: string, idx: number) => (
                    <span key={idx} className="bg-slate-100 text-slate-800 border border-slate-300 px-2 py-0.5 rounded text-[11px] font-medium">
                      ✓ {req}
                    </span>
                  ))}
                </div>
              </div>

              {extractedResult.matched_catalogue_products.length > 0 && (
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 block mb-1">
                    Matched Catalogue Products (Official SKUs):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {extractedResult.matched_catalogue_products.map((p: any, idx: number) => (
                      <span key={idx} className="bg-emerald-50 text-emerald-800 border border-emerald-300 px-2 py-0.5 rounded text-[11px] font-semibold flex items-center gap-1">
                        <Tag className="w-3 h-3 text-emerald-600" />
                        <strong>{p.product_id}</strong>: {p.product_name} (₹{p.price_inr_per_month}/mo)
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {extractedResult.unmatched_requirements && extractedResult.unmatched_requirements.length > 0 && (
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 block mb-1">
                    Unmatched Requirements (Catalogue Gap):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {extractedResult.unmatched_requirements.map((u: string, idx: number) => (
                      <span key={idx} className="bg-amber-50 text-amber-800 border border-amber-300 px-2 py-0.5 rounded text-[11px]">
                        Notice: {u} (No matching SKU in Accel B2B catalogue)
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <p className="text-[10px] text-emerald-700 italic border-t border-slate-100 pt-2">
              ✓ All relevant form fields have been populated. Recommended catalogue bundles are displayed below with full itemized pricing.
            </p>
          </div>
        )}
      </div>

      {/* Interactive Step Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 mb-8 max-w-3xl mx-auto">
        {step === 1 && (
          <div className="space-y-5">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Store className="w-5 h-5 text-red-600" />
              <span>Step 1: What is the identity and location of your business?</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Business Legal / Trade Name
                </label>
                <input
                  type="text"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  placeholder="e.g. Ramesh Provision Store"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Business Category
                </label>
                <select
                  value={formData.business_type}
                  onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none bg-white"
                >
                  <option value="retail">Micro Retail / Kirana / Salon / Pharmacy</option>
                  <option value="clinic">Clinic / Healthcare / Diagnostic Center</option>
                  <option value="office">Professional Office / CA Firm / Law Office</option>
                  <option value="restaurant">Restaurant / Cafe / Food Chain</option>
                  <option value="mfg">Small Manufacturing / Auto Parts / Textile</option>
                  <option value="services">General Services & Contracting</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Operating City
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="e.g. Jaipur, Bengaluru, Chennai"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  City Tier
                </label>
                <select
                  value={formData.city_tier}
                  onChange={(e) => setFormData({ ...formData, city_tier: parseInt(e.target.value) })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none bg-white"
                >
                  <option value={1}>Tier 1 (Metro / Major Tech Hub)</option>
                  <option value={2}>Tier 2 (Emerging Industrial & Commercial Hub)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Building className="w-5 h-5 text-red-600" />
              <span>Step 2: Tell us about your operational scale & setup</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Number of Employees / Staff
                </label>
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={formData.employee_count}
                  onChange={(e) => setFormData({ ...formData, employee_count: parseInt(e.target.value) || 1 })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Number of Physical Sites / Branches
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={formData.num_sites}
                  onChange={(e) => setFormData({ ...formData, num_sites: parseInt(e.target.value) || 1 })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Current Internet Setup
                </label>
                <select
                  value={formData.current_internet}
                  onChange={(e) => setFormData({ ...formData, current_internet: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none bg-white"
                >
                  <option value="mobile_hotspot">Owner's Mobile Phone Hotspot</option>
                  <option value="home_broadband">Consumer Home Broadband</option>
                  <option value="local_cable">Local Cable ISP (Frequent cuts)</option>
                  <option value="leased_line">Dedicated Leased Line</option>
                  <option value="none">No current internet</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Current Monthly Telecom Spend (₹)
                </label>
                <input
                  type="number"
                  step="100"
                  value={formData.monthly_budget_inr}
                  onChange={(e) => setFormData({ ...formData, monthly_budget_inr: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-5">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-red-600" />
              <span>Step 3: Which digital capabilities does your business require?</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 hover:border-red-300 cursor-pointer transition-all bg-slate-50/50">
                <input
                  type="checkbox"
                  checked={formData.need_pos}
                  onChange={(e) => setFormData({ ...formData, need_pos: e.target.checked })}
                  className="mt-0.5 rounded text-red-600 focus:ring-red-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <CreditCard className="w-4 h-4 text-red-600" />
                    Cloud POS & UPI Billing
                  </span>
                  <p className="text-xs text-slate-500">Fast barcode billing, GST invoicing & UPI/card payment sync.</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 hover:border-red-300 cursor-pointer transition-all bg-slate-50/50">
                <input
                  type="checkbox"
                  checked={formData.need_whatsapp}
                  onChange={(e) => setFormData({ ...formData, need_whatsapp: e.target.checked })}
                  className="mt-0.5 rounded text-red-600 focus:ring-red-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <MessageSquare className="w-4 h-4 text-emerald-600" />
                    Official WhatsApp Business API
                  </span>
                  <p className="text-xs text-slate-500">Automated catalogue, booking confirmation & customer alerts.</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 hover:border-red-300 cursor-pointer transition-all bg-slate-50/50">
                <input
                  type="checkbox"
                  checked={formData.need_cloud_email}
                  onChange={(e) => setFormData({ ...formData, need_cloud_email: e.target.checked })}
                  className="mt-0.5 rounded text-red-600 focus:ring-red-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <Mail className="w-4 h-4 text-sky-600" />
                    Custom Domain & Cloud Email
                  </span>
                  <p className="text-xs text-slate-500">Professional company email addresses (e.g. care@mybusiness.com).</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 hover:border-red-300 cursor-pointer transition-all bg-slate-50/50">
                <input
                  type="checkbox"
                  checked={formData.need_cctv}
                  onChange={(e) => setFormData({ ...formData, need_cctv: e.target.checked })}
                  className="mt-0.5 rounded text-red-600 focus:ring-red-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <Camera className="w-4 h-4 text-amber-600" />
                    Cloud CCTV Cameras & Remote View
                  </span>
                  <p className="text-xs text-slate-500">HD cameras with 30-day cloud recording viewable on your mobile.</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 hover:border-red-300 cursor-pointer transition-all bg-slate-50/50">
                <input
                  type="checkbox"
                  checked={formData.need_security}
                  onChange={(e) => setFormData({ ...formData, need_security: e.target.checked })}
                  className="mt-0.5 rounded text-red-600 focus:ring-red-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-indigo-600" />
                    Endpoint Cybersecurity & Ransomware Defense
                  </span>
                  <p className="text-xs text-slate-500">Device-level antivirus protecting clinic/accounting records.</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 hover:border-red-300 cursor-pointer transition-all bg-slate-50/50">
                <input
                  type="checkbox"
                  checked={formData.need_failover_backup}
                  onChange={(e) => setFormData({ ...formData, need_failover_backup: e.target.checked })}
                  className="mt-0.5 rounded text-red-600 focus:ring-red-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <Wifi className="w-4 h-4 text-red-600" />
                    4G/5G Wireless Failover Router
                  </span>
                  <p className="text-xs text-slate-500">Automatic instant backup so billing never stops when fiber is cut.</p>
                </div>
              </label>
            </div>

            <div className="pt-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Business SIMs Required
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={formData.need_sims}
                onChange={(e) => setFormData({ ...formData, need_sims: parseInt(e.target.value) || 1 })}
                className="w-32 px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-5">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-red-600" />
              <span>Step 4: Target Budget & Registration Status</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Target Monthly Budget (₹)
                </label>
                <input
                  type="number"
                  step="500"
                  value={formData.monthly_budget_inr}
                  onChange={(e) => setFormData({ ...formData, monthly_budget_inr: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
                <p className="text-[11px] text-slate-500 mt-1">Advisor will optimize recommended tiers to fit this budget.</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Do you have a registered GSTIN?
                </label>
                <div className="flex items-center gap-4 mt-2">
                  <label className="flex items-center gap-2 text-sm text-slate-800 cursor-pointer">
                    <input
                      type="radio"
                      name="has_gstin"
                      checked={formData.has_gstin === true}
                      onChange={() => setFormData({ ...formData, has_gstin: true })}
                      className="text-red-600 focus:ring-red-500"
                    />
                    <span>Yes, have active GSTIN</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-800 cursor-pointer">
                    <input
                      type="radio"
                      name="has_gstin"
                      checked={formData.has_gstin === false}
                      onChange={() => setFormData({ ...formData, has_gstin: false, gstin: '' })}
                      className="text-red-600 focus:ring-red-500"
                    />
                    <span>No GSTIN (Micro business)</span>
                  </label>
                </div>
              </div>

              {formData.has_gstin && (
                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    GSTIN Number (Optional at this stage)
                  </label>
                  <input
                    type="text"
                    value={formData.gstin || ''}
                    onChange={(e) => setFormData({ ...formData, gstin: e.target.value.toUpperCase() })}
                    placeholder="e.g. 19EOGXH4115Y1ZL"
                    maxLength={15}
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-red-500 focus:outline-none"
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-100 mt-6">
          {step > 1 ? (
            <button
              onClick={handleBack}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-slate-700 hover:text-slate-900 transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
          ) : (
            <div></div>
          )}

          <button
            onClick={handleNext}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold text-sm shadow-md shadow-red-600/30 transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <span>Analyzing Catalogue...</span>
            ) : step < 4 ? (
              <>
                <span>Next Step</span>
                <ArrowRight className="w-4 h-4" />
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Recommendations</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recommendations Output */}
      {recommendations && (
        <div className="space-y-6 animate-fade-in">
          {/* Concise Business Profile Summary */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3 mb-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="w-2.5 h-2.5 rounded-full bg-red-600"></span>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Business Profile Summary
                </span>
                <span className="text-xs font-extrabold text-slate-900 bg-slate-100 px-2.5 py-0.5 rounded">
                  {formData.business_name || 'My Business'}
                </span>
                <span className="text-[11px] font-semibold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full uppercase">
                  {formData.business_type} · {formData.segment}
                </span>
              </div>
              <div className="text-[11px] text-slate-500 flex items-center gap-3">
                <span>Location: <strong>{formData.city}</strong> (Tier {formData.city_tier})</span>
                <span>•</span>
                <span>Scale: <strong>{formData.employee_count}</strong> Staff, <strong>{formData.num_sites}</strong> {formData.num_sites > 1 ? 'Sites' : 'Site'}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Target Monthly Budget</span>
                <span className="text-sm font-black text-slate-900 mt-0.5 block">
                  {formData.monthly_budget_inr > 0 ? `₹${formData.monthly_budget_inr.toLocaleString()}/mo` : 'Unspecified'}
                </span>
                <span className="text-[10px] text-slate-500">Optimization ceiling</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Registration Status</span>
                <span className="text-sm font-black text-slate-900 mt-0.5 block">
                  {formData.has_gstin ? 'GSTIN Registered' : 'Micro Exemption'}
                </span>
                <span className="text-[10px] text-slate-500">
                  {formData.has_gstin ? (formData.gstin || 'GSTIN Provided') : 'Udyam micro route'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 sm:col-span-2">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Identified Operational Needs</span>
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                    High-speed Fiber
                  </span>
                  {formData.need_sims > 0 && (
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                      {formData.need_sims} Business SIMs
                    </span>
                  )}
                  {formData.need_pos && (
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                      Smart POS / Soundbox
                    </span>
                  )}
                  {formData.need_cloud_email && (
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                      Cloud Email
                    </span>
                  )}
                  {formData.need_cctv && (
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                      Cloud CCTV
                    </span>
                  )}
                  {formData.need_security && (
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                      Cybersecurity
                    </span>
                  )}
                  {formData.need_failover_backup && (
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-semibold text-slate-700">
                      4G/5G Failover
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* AI Advisor Audio Summary Banner */}
          <div className="bg-gradient-to-r from-red-50 to-slate-50 border border-red-200 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-red-600 text-white flex items-center justify-center font-bold flex-shrink-0 shadow-sm">
                AI
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <span>AI Advisor Catalogue-Grounded Recommendation</span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-800">
                    25-SKU Ground Truth
                  </span>
                </h4>
                <p className="text-xs text-slate-700 mt-1 max-w-2xl leading-relaxed">
                  {recommendations.summary_message}
                </p>
              </div>
            </div>

            <button
              onClick={() => speakText(recommendations.summary_message)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:text-red-600 text-xs font-semibold shadow-sm transition-all cursor-pointer"
            >
              <Volume2 className="w-4 h-4 text-red-600" />
              <span>{isSpeaking ? 'Stop Audio' : 'Listen Voice'}</span>
            </button>
          </div>

          {/* 3 Comparison Tiers */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendations.recommendations.map((tier, idx) => {
              const isGrowth = tier.tier_name === 'Growth';
              const isBudgetExceeded = formData.monthly_budget_inr > 0 && tier.monthly_total_inr > formData.monthly_budget_inr;
              const lowerCostTier = recommendations.recommendations.find(t => t.monthly_total_inr < tier.monthly_total_inr);

              return (
                <div
                  key={tier.tier_name}
                  className={`rounded-2xl p-6 transition-all relative flex flex-col justify-between ${
                    isGrowth
                      ? 'bg-white border-2 border-red-600 shadow-xl shadow-red-600/10 -translate-y-1'
                      : 'bg-white border border-slate-200 shadow-sm hover:border-slate-300'
                  }`}
                >
                  {isGrowth && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-red-600 text-white text-[11px] font-extrabold px-3 py-0.5 rounded-full uppercase tracking-wider shadow">
                      Most Recommended Fit
                    </div>
                  )}

                  <div>
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <h3 className="text-xl font-extrabold text-slate-900">{tier.tier_name}</h3>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {tier.contract_months} Mo Tenure
                      </span>
                    </div>

                    <p className="text-xs text-slate-500 mb-4">{tier.tagline}</p>

                    {/* Price Block: Separate Monthly Recurring & Setup Charges */}
                    <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-100 mb-4 space-y-2">
                      <div className="flex items-baseline justify-between">
                        <div>
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Monthly Recurring (MRC)</span>
                          <div className="flex items-baseline gap-1 mt-0.5">
                            <span className="text-2xl font-black text-slate-900">₹{tier.monthly_total_inr.toLocaleString()}</span>
                            <span className="text-xs text-slate-500">/ month</span>
                          </div>
                        </div>
                        {tier.savings_inr > 0 && (
                          <div className="text-right">
                            <span className="text-[10px] uppercase font-bold text-emerald-600 block">Bundle Savings</span>
                            <span className="text-xs font-bold text-emerald-600">Save ₹{tier.savings_inr.toLocaleString()}/mo</span>
                          </div>
                        )}
                      </div>

                      <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-600">
                        <span>One-Time Setup Fee:</span>
                        <span className="font-bold text-slate-800">
                          {tier.one_time_setup_inr > 0 ? `₹${tier.one_time_setup_inr.toLocaleString()}` : 'Zero Setup Fee'}
                        </span>
                      </div>

                      {/* Budget Headroom or Excess Callout */}
                      {formData.monthly_budget_inr > 0 && (
                        <div className={`mt-1.5 p-2 rounded-lg text-[10px] font-semibold flex items-center gap-1.5 ${
                          !isBudgetExceeded
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200/80'
                            : 'bg-amber-50 text-amber-900 border border-amber-200/80'
                        }`}>
                          {!isBudgetExceeded ? (
                            <>
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                              <span>Within Budget (₹{(formData.monthly_budget_inr - tier.monthly_total_inr).toLocaleString()}/mo headroom)</span>
                            </>
                          ) : (
                            <>
                              <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                              <span>Exceeds Target Budget by ₹{(tier.monthly_total_inr - formData.monthly_budget_inr).toLocaleString()}/mo</span>
                            </>
                          )}
                        </div>
                      )}

                      {/* Lower-cost alternative indicator */}
                      {lowerCostTier ? (
                        <div className="text-[10px] text-slate-500 bg-white border border-slate-200 rounded-lg px-2 py-1 flex items-center justify-between">
                          <span>Lower-cost alternative:</span>
                          <span className="font-bold text-slate-700">{lowerCostTier.tier_name} (₹{lowerCostTier.monthly_total_inr.toLocaleString()}/mo)</span>
                        </div>
                      ) : (
                        <div className="text-[10px] text-emerald-700 bg-emerald-50/60 border border-emerald-200/50 rounded-lg px-2 py-1 font-semibold text-center">
                          ✓ Lowest Cost Entry-Level Bundle
                        </div>
                      )}
                    </div>

                    {/* Products List with Individual Catalogue Prices */}
                    <div className="space-y-2 mb-4">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                        Included Catalogue Products
                      </span>
                      <div className="space-y-1.5">
                        {tier.products.map((p: any) => (
                          <div key={p.product_id} className="p-2 rounded-lg bg-slate-50/80 border border-slate-100 flex items-start justify-between gap-2 text-xs">
                            <div className="flex items-start gap-1.5 min-w-0">
                              <Check className="w-3.5 h-3.5 text-emerald-600 mt-0.5 flex-shrink-0" />
                              <div className="truncate">
                                <span className="font-bold text-slate-900 block truncate">
                                  {p.product_name} {p.quantity > 1 ? `(×${p.quantity})` : ''}
                                </span>
                                <span className="text-[10px] text-slate-400 block truncate">{p.description}</span>
                              </div>
                            </div>
                            <div className="text-right flex-shrink-0">
                              <span className="font-semibold text-slate-900 block text-[11px]">
                                ₹{(p.price_inr_per_month || p.unit_price_monthly_inr || 0).toLocaleString()}/mo
                              </span>
                              {(p.one_time_setup_inr || p.unit_setup_inr) > 0 && (
                                <span className="text-[9px] text-slate-400 block">
                                  +₹{(p.one_time_setup_inr || p.unit_setup_inr).toLocaleString()} setup
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Optional Add-Ons Preview */}
                    {tier.optional_addons && tier.optional_addons.length > 0 && (
                      <div className="mb-4">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                          Compatible Optional Add-Ons
                        </span>
                        <div className="space-y-1">
                          {tier.optional_addons.slice(0, 2).map((addon: any) => (
                            <div key={addon.product_id} className="flex items-center justify-between text-[11px] text-slate-600 px-2 py-1 rounded bg-slate-50 border border-slate-100">
                              <span className="truncate max-w-[140px] text-[10px]">+ {addon.product_name}</span>
                              <span className="font-semibold text-slate-800 text-[10px]">₹{addon.price_inr_per_month.toLocaleString()}/mo</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Why Recommended Explanation */}
                    <div className="border-t border-slate-100 pt-3 mb-3">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                        Recommendation Logic & Persona Fit
                      </span>
                      <p className="text-xs text-slate-700 leading-relaxed">{tier.why_recommended}</p>
                    </div>

                    {/* Potential Limitations & Constraints */}
                    {tier.potential_limitations && (
                      <div className="bg-amber-50/70 border border-amber-200/60 rounded-lg p-2.5 mb-5 text-[11px] text-amber-800 flex items-start gap-1.5">
                        <HelpCircle className="w-3.5 h-3.5 text-amber-600 mt-0.5 flex-shrink-0" />
                        <span>{tier.potential_limitations}</span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => onSelectTier(tier)}
                    className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                      isGrowth
                        ? 'bg-red-600 hover:bg-red-700 text-white shadow-md shadow-red-600/30'
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                    }`}
                  >
                    <span>Customize & Build Quote</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}
          </div>

          <div className="text-center text-xs text-slate-400 pt-4">
            {recommendations.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};
