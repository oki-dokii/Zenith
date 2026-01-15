
'use client';

import React, { useState, useEffect } from 'react';
import { Activity, Brain, Lock, Wifi } from 'lucide-react';

export default function IntelligenceHUD() {
    // Mock state for demonstration
    const [intent, setIntent] = useState('Idle');
    const [appContext, setAppContext] = useState('Detecting...');
    const [confidence, setConfidence] = useState(0);

    // Simulate "Alive" behavior & Listen to Electron
    useEffect(() => {
        // Poll for "Thinking" visual
        const interval = setInterval(() => {
            setConfidence(prev => Math.min(100, Math.max(80, prev + (Math.random() - 0.5) * 10)));
        }, 1000);

        // Listen to IPC messages from Main Process
        if (typeof window !== 'undefined' && window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.on('active-window-change', (event: any, data: any) => {
                // Simple Heuristic for Demo
                const appName = data.owner || "Unknown";
                setAppContext(appName);

                // Heuristic Context Switch
                if (appName.toLowerCase().includes('code') || appName.includes('Terminal')) {
                    setIntent('Coding');
                } else if (appName.toLowerCase().includes('chrome') || appName.includes('browser')) {
                    setIntent('Browsing / Research');
                } else if (appName.toLowerCase().includes('slack') || appName.includes('whatsapp')) {
                    setIntent('Communication');
                } else if (appName.toLowerCase().includes('notepad') || appName.includes('text')) {
                    setIntent('Drafting');
                } else if (appName.toLowerCase().includes('calc')) {
                    setIntent('Calculation');
                } else {
                    setIntent('General Task');
                }
            });
        }

        return () => clearInterval(interval);
    }, []);

    // Toggle Click-Through Logic
    const setIgnoreMouseEvents = (ignore: boolean) => {
        if (typeof window !== 'undefined' && window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.send('set-ignore-mouse-events', ignore);
        }
    };

    // Force "Click-Through" on mount to be safe
    useEffect(() => {
        setIgnoreMouseEvents(true);
    }, []);

    return (
        <div
            className="fixed bottom-10 left-1/2 -translate-x-1/2 w-[700px] pointer-events-auto transition-all duration-300"
            onMouseEnter={() => setIgnoreMouseEvents(false)} // Trap clicks when hovering HUD
            onMouseLeave={() => setIgnoreMouseEvents(true)}  // Forward clicks when leaving HUD
        >
            {/* Main Glass Panel */}
            <div className="bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-5 text-white flex items-center gap-6">

                {/* Brain/Status Icon */}
                <div className="relative group shrink-0">
                    <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 animate-pulse"></div>
                    <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-4 rounded-xl relative z-10 shadow-inner border border-white/20">
                        <Brain className="w-8 h-8 text-white" />
                    </div>
                </div>

                {/* Metrics & Context */}
                <div className="flex-1 space-y-3 min-w-0">
                    <div className="flex items-center justify-between text-[11px] text-gray-400 font-medium uppercase tracking-wider">
                        <span className="flex items-center gap-2">
                            <Activity className="w-3 h-3 text-green-400" />
                            Avg Latency: <span className="text-white font-bold">18ms</span>
                        </span>
                        <span className="flex items-center gap-2 bg-green-500/10 px-2 py-0.5 rounded-full border border-green-500/20">
                            <Lock className="w-3 h-3 text-green-400" />
                            <span className="text-green-400">Secure (On-Device)</span>
                        </span>
                    </div>

                    <div className="flex items-center gap-3 whitespace-nowrap overflow-hidden">
                        <div className="text-base font-semibold text-gray-300 bg-white/5 px-3 py-1 rounded-lg border border-white/5 flex items-center gap-2">
                            <span className="text-gray-500 text-xs uppercase tracking-wide">App</span>
                            <span className="text-white truncate max-w-[150px]">{appContext}</span>
                        </div>
                        <div className="text-base font-semibold text-purple-300 flex items-center gap-2">
                            <span className="text-purple-500/70 text-xs uppercase tracking-wide">Intent</span>
                            <span className="text-purple-100">{intent}</span>
                        </div>
                    </div>

                    {/* Confidence Bar */}
                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 transition-all duration-500 ease-out shadow-[0_0_10px_rgba(168,85,247,0.5)]"
                            style={{ width: `${confidence}%` }}
                        />
                    </div>
                </div>

                {/* Connection Status */}
                <div className="flex flex-col items-center justify-center gap-1 text-[10px] text-gray-500">
                    <Wifi className="w-4 h-4 text-gray-600" />
                    <span>OFFLINE</span>
                </div>
            </div>
        </div>
    );
}
