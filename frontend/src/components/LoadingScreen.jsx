import React, { useState, useEffect, useMemo } from 'react';

const FUN_FACTS = [
    "Setting up the digital judge's panel...",
    "The world's first hackathon took place in Calgary back in 1999.",
    "Many hackathon winners start their pitch by explaining the core problem first.",
    "The most common project commit message at 3 AM is usually 'final fix'.",
    "Judges often focus on the impact and usability of your project.",
    "A typical hackathon team consumes a lot of high-energy drinks and snacks.",
    "The term 'hack' refers to a clever and efficient solution to a problem.",
    "Many great startups actually began as simple weekend hackathon projects.",
    "Pro tip: Test your demo thoroughly before the final presentation.",
    "Our AI is looking for clean code and meaningful variable names.",
    "A smooth user interface makes a great first impression on any judge.",
    "Selecting different judge personas provides diverse perspectives on your code.",
    "Some of the world's largest hackathons host thousands of participants.",
    "We are scanning for security best practices and potential vulnerabilities.",
    "Our engine is evaluating the architecture and scalability of your app.",
    "Analyzing your build scripts for efficiency and optimization."
];

const TypewriterText = ({ text }) => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        setIndex(0);
    }, [text]);

    useEffect(() => {
        if (index < text.length) {
            const timeout = setTimeout(() => {
                setIndex(prev => prev + 1);
            }, 30);
            return () => clearTimeout(timeout);
        }
    }, [index, text]);

    return <span>{text.substring(0, index)}<span className="animate-pulse">_</span></span>;
};

const LoadingScreen = () => {
    const [factIndex, setFactIndex] = useState(0);
    const [progress, setProgress] = useState(0);

    // Background particles
    const particles = useMemo(() => {
        return Array.from({ length: 20 }).map((_, i) => ({
            id: i,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            size: Math.random() * 3 + 1,
            duration: Math.random() * 10 + 10,
            delay: Math.random() * 5
        }));
    }, []);

    useEffect(() => {
        // Fact cycle
        const factInterval = setInterval(() => {
            setFactIndex((prev) => (prev + 1) % FUN_FACTS.length);
        }, 5000);

        // Progress simulation (0 to 99)
        const progressInterval = setInterval(() => {
            setProgress(prev => {
                if (prev < 30) return prev + 0.5;
                if (prev < 70) return prev + 0.2;
                if (prev < 95) return prev + 0.1;
                if (prev < 99) return prev + 0.05;
                return prev;
            });
        }, 100);

        return () => {
            clearInterval(factInterval);
            clearInterval(progressInterval);
        };
    }, []);

    return (
        <div className="relative min-h-[600px] w-full flex flex-col items-center justify-center overflow-hidden bg-slate-50/50 rounded-3xl border border-slate-100/50">
            <style>
                {`
                    @keyframes shard-rotate {
                        0% { transform: rotate(0deg) scale(1.1); opacity: 0.3; }
                        50% { transform: rotate(180deg) scale(1.3); opacity: 0.8; }
                        100% { transform: rotate(360deg) scale(1.1); opacity: 0.3; }
                    }
                    @keyframes float-particle {
                        0% { transform: translateY(0) rotate(0deg); opacity: 0; }
                        20% { opacity: 0.4; }
                        80% { opacity: 0.4; }
                        100% { transform: translateY(-300px) rotate(360deg); opacity: 0; }
                    }
                    .particle {
                        animation: float-particle linear infinite;
                    }
                    .shard-1 { animation: shard-rotate 8s infinite linear; }
                    .shard-2 { animation: shard-rotate 12s infinite linear reverse; }
                    .shard-3 { animation: shard-rotate 15s infinite ease-in-out; }
                `}
            </style>

            {/* Ambient Background Elements */}
            <div className="absolute inset-0 pointer-events-none">
                {particles.map(p => (
                    <div
                        key={p.id}
                        className="particle absolute bg-indigo-200/40 rounded-full"
                        style={{
                            left: p.left,
                            top: p.top,
                            width: `${p.size}px`,
                            height: `${p.size}px`,
                            '--duration': `${p.duration}s`,
                            animationDelay: `${p.delay}s`,
                            animationDuration: `${p.duration}s`
                        }}
                    />
                ))}
            </div>

            {/* Central Visualizer */}
            <div className="relative mb-16 scale-110">
                {/* Decorative Shards */}
                <div className="shard-1 absolute -inset-12 border border-indigo-200/30 rounded-[35%] opacity-40"></div>
                <div className="shard-2 absolute -inset-16 border border-purple-200/20 rounded-[45%] opacity-30"></div>
                <div className="shard-3 absolute -inset-20 border border-blue-200/10 rounded-[40%] opacity-20"></div>

                {/* Main Progress Hexagon/Circle Container */}
                <div className="relative w-48 h-48 flex items-center justify-center">
                    {/* Progress Ring (SVG) */}
                    <svg className="w-full h-full transform -rotate-90 drop-shadow-[0_0_15px_rgba(99,102,241,0.2)]">
                        <circle
                            cx="96"
                            cy="96"
                            r="88"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="transparent"
                            className="text-slate-100"
                        />
                        <circle
                            cx="96"
                            cy="96"
                            r="88"
                            stroke="currentColor"
                            strokeWidth="6"
                            fill="transparent"
                            strokeDasharray={2 * Math.PI * 88}
                            strokeDashoffset={2 * Math.PI * 88 * (1 - progress / 100)}
                            className="text-indigo-600 transition-all duration-300 ease-out stroke-round"
                        />
                    </svg>

                    {/* Counter Content */}
                    <div className="absolute flex flex-col items-center justify-center">
                        <div className="text-5xl font-black text-slate-800 tracking-tighter tabular-nums">
                            {Math.floor(progress)}<span className="text-2xl text-indigo-400">%</span>
                        </div>
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">
                            Analyzing...
                        </div>
                    </div>

                    {/* Spinning Indicator Dots */}
                    <div className="absolute inset-0 animate-[spin_4s_linear_infinite]">
                        <div className="absolute top-2 left-1/2 -translate-x-1/2 w-3 h-3 bg-indigo-500 rounded-full shadow-[0_0_12px_rgba(99,102,241,0.6)]"></div>
                    </div>
                </div>
            </div>

            {/* Information Feed */}
            <div className="text-center max-w-lg px-8 relative z-10">

                <h2 className="text-3xl font-black text-slate-800 mb-4 tracking-tight">
                    Reviewing Your Masterpiece
                </h2>

                {/* System Logs / Fun Facts */}
                <div className="bg-slate-900/90 backdrop-blur-xl p-8 rounded-2xl border border-slate-800 shadow-2xl w-full min-h-[140px] max-h-[140px] flex flex-col items-center justify-center text-center font-mono overflow-hidden">

                    <div className="space-y-2">
                        <div className="text-slate-300 text-sm leading-relaxed overflow-hidden py-2">
                            <TypewriterText text={FUN_FACTS[factIndex]} />
                        </div>
                    </div>
                </div>

                <p className="mt-8 text-slate-400 text-xs font-medium">
                    Please hold tight. Our AI is debating your architectural choices.
                </p>
            </div>
        </div>
    );
};

export default LoadingScreen;
