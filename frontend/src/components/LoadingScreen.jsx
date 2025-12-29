import React, { useState, useEffect } from 'react';

const FUN_FACTS = [
    "The first hackathon was held by OpenBSD in Calgary, 1999.",
    "90% of hackathon winners start their pitch with 'So, we had this idea...'",
    "The most used git commit message during a hackathon is 'pls work'.",
    "Hackathon judges can spend as little as 3 minutes on your GitHub repo.",
    "A typical hackathon participant consumes 3x their body weight in coffee.",
    "The word 'hack' originated from MIT in the 1950s for clever solutions.",
    "Most production code is just last-minute hackathon code with more comments.",
    "Hackathon rule #1: If it works on your machine, don't touch it.",
    "Our AI is currently checking if you used generic names like 'test_button'.",
    "Fact: A beautiful UI can hide a 0% test coverage backend.",
    "Fun Fact: This judge persona selection actually changes the AI's standard of 'good'.",
    "The longest hackathon ever lasted for over 250 hours!"
];

const LoadingScreen = () => {
    const [factIndex, setFactIndex] = useState(0);
    const [fade, setFade] = useState(true);

    useEffect(() => {
        const interval = setInterval(() => {
            setFade(false);
            setTimeout(() => {
                setFactIndex((prev) => (prev + 1) % FUN_FACTS.length);
                setFade(true);
            }, 500);
        }, 4000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center py-20 animate-in fade-in zoom-in duration-1000">
            {/* Premium Loader */}
            <div className="relative mb-12">
                {/* Outer Ring */}
                <div className="w-32 h-32 rounded-full border-4 border-slate-100 border-t-indigo-600 animate-spin"></div>

                {/* Inner Ring (Reverse Spin) */}
                <div className="absolute inset-4 rounded-full border-4 border-slate-50 border-b-purple-500 animate-[spin_1.5s_linear_infinite_reverse]"></div>

                {/* Pulsing Core */}
                <div className="absolute inset-10 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-full animate-pulse shadow-[0_0_30px_rgba(99,102,241,0.4)]"></div>

                {/* Scan Line Animation */}
                <div className="absolute -inset-2 rounded-full border border-indigo-200/50 animate-ping opacity-20"></div>
            </div>

            <div className="text-center max-w-md px-6">
                <h2 className="text-3xl font-black text-slate-800 mb-2 tracking-tight">
                    Analyzing Genius<span className="text-indigo-600 animate-pulse">...</span>
                </h2>
                <p className="text-slate-500 font-medium mb-12">
                    Scouring your codebase for bugs and brilliance.
                </p>

                {/* Fun Fact Card */}
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative bg-white/90 backdrop-blur-md p-6 rounded-2xl border border-white/50 shadow-sm min-h-[100px] flex flex-col items-center justify-center">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-3">
                            Hackathon Reality Check
                        </div>
                        <p className={`text-slate-700 font-bold leading-relaxed transition-opacity duration-500 text-lg ${fade ? 'opacity-100' : 'opacity-0'}`}>
                            "{FUN_FACTS[factIndex]}"
                        </p>
                    </div>
                </div>
            </div>

            {/* Status Steps */}
            <div className="mt-16 flex items-center gap-8 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                    Repository
                </div>
                <div className="w-8 h-[1px] bg-slate-200"></div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_8px_rgba(99,102,241,0.5)]"></div>
                    Presentation
                </div>
                <div className="w-8 h-[1px] bg-slate-200"></div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-slate-300"></div>
                    Verdict
                </div>
            </div>
        </div>
    );
};

export default LoadingScreen;
