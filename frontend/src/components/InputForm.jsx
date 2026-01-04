import React, { useState } from 'react';

const InputForm = ({ onSubmit, isLoading }) => {
    const [githubUrl, setGithubUrl] = useState('');
    const [videoUrl, setVideoUrl] = useState('');
    const [manualTranscript, setManualTranscript] = useState('');
    const [persona, setPersona] = useState('standard');

    const [pptFile, setPptFile] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('github_url', githubUrl);
        formData.append('video_url', videoUrl);
        formData.append('manual_transcript', manualTranscript);
        formData.append('persona', persona);
        if (pptFile) {
            formData.append('ppt_file', pptFile);
        }
        onSubmit(formData);
    };

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            {/* Feature Highlights Grid - Now at the Top */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { icon: '👥', title: 'Multi-Judge Panel', desc: 'VC, CTO, and PM personas evaluate your pitch in parallel.' },
                    { icon: '🛡️', title: 'Security Scan', desc: 'Auto-detects API key leaks and vulnerable configurations.' },
                    { icon: '🚀', title: 'Mentor Roadmap', desc: 'Get a clear path to turn your prototype into a product.' },
                ].map((feat, i) => (
                    <div key={i} className="p-4 rounded-xl bg-white/40 border border-white/60 text-center backdrop-blur-sm transition-transform hover:scale-[1.02]">
                        <div className="text-3xl mb-2">{feat.icon}</div>
                        <h4 className="font-bold text-slate-800 text-sm mb-1">{feat.title}</h4>
                        <p className="text-slate-500 text-[11px] leading-relaxed">{feat.desc}</p>
                    </div>
                ))}
            </div>

            <div className="bg-white/80 backdrop-blur-xl p-6 md:p-10 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/50 relative overflow-hidden">
                {/* Decoration */}
                <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-indigo-500 to-purple-600"></div>

                <h2 className="text-3xl font-bold mb-8 text-slate-800">Submit Project</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="block text-sm font-semibold text-slate-700 uppercase tracking-wide">
                            GitHub Repository
                        </label>
                        <div className="relative">
                            <input
                                type="text"
                                className="w-full p-4 pl-12 rounded-xl bg-slate-50 border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-slate-800 placeholder-slate-400 font-medium"
                                placeholder="https://github.com/username/repo"
                                value={githubUrl}
                                onChange={(e) => setGithubUrl(e.target.value)}
                            />
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-xl opacity-50">📦</div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-sm font-semibold text-slate-700 uppercase tracking-wide">
                            Demo Video <span className="text-slate-400 font-normal normal-case">(YouTube)</span>
                        </label>
                        <div className="relative">
                            <input
                                type="text"
                                className="w-full p-4 pl-12 rounded-xl bg-slate-50 border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-slate-800 placeholder-slate-400 font-medium"
                                placeholder="https://youtube.com/watch?v=..."
                                value={videoUrl}
                                onChange={(e) => setVideoUrl(e.target.value)}
                            />
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-xl opacity-50">🎬</div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-sm font-semibold text-slate-700 uppercase tracking-wide">
                            Manual Transcript <span className="text-slate-400 font-normal normal-case">(Optional - fallback)</span>
                        </label>
                        <div className="relative">
                            <textarea
                                className="w-full p-4 pl-12 rounded-xl bg-slate-50 border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-slate-800 placeholder-slate-400 font-medium"
                                placeholder="Paste transcript here if YouTube fetch fails..."
                                value={manualTranscript}
                                onChange={(e) => setManualTranscript(e.target.value)}
                                rows="3"
                            />
                            <div className="absolute left-4 top-6 text-xl opacity-50">📝</div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-sm font-semibold text-slate-700 uppercase tracking-wide">
                            Presentation <span className="text-slate-400 font-normal normal-case">(Optional)</span>
                        </label>
                        <div className="relative">
                            <input
                                type="file"
                                accept=".ppt,.pptx,.pdf"
                                className="w-full p-4 pl-12 rounded-xl bg-slate-50 border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-slate-800 font-medium file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                                onChange={(e) => setPptFile(e.target.files[0])}
                            />
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-xl opacity-50">📊</div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-sm font-semibold text-slate-700 uppercase tracking-wide">
                            Judge Persona
                        </label>
                        <div className="relative">
                            <select
                                value={persona}
                                onChange={(e) => setPersona(e.target.value)}
                                className="w-full p-4 pl-12 rounded-xl bg-slate-50 border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-slate-800 font-medium appearance-none cursor-pointer"
                            >
                                <option value="standard">⚖️ Standard Judge (Balanced)</option>
                                <option value="consensus">🗳️ Multi-Judge Consensus (Panel)</option>
                                <option value="vc">💸 The VC (Business & Scale)</option>
                                <option value="cto">🧔🏻‍♂️ The Grumpy CTO (Code Quality)</option>
                                <option value="roast">🔥 Roast Master (Ruthless & Funny)</option>
                            </select>
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-xl opacity-50">🎭</div>
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">▼</div>
                        </div>
                    </div>

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className={`w-full py-4 rounded-xl font-bold text-lg shadow-xl shadow-indigo-500/20 transition-all transform hover:-translate-y-0.5 active:translate-y-0 ${isLoading
                                ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
                                : 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white'
                                }`}
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center gap-2">
                                    Analyzing...
                                </span>
                            ) : (
                                'Judge My Project 🚀'
                            )}
                        </button>
                    </div>
                </form>
            </div>

            <div className="text-center text-slate-400 text-sm">
                <p>Ensure your repo is public. We don't store your code.</p>
            </div>
        </div>
    );
};

export default InputForm;
