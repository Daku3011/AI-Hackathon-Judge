import React from 'react';

const FeedbackSection = ({ feedback, whyWontWin, strengths = [], improvements = [], questions = [], pptAnalysis = {}, videoAnalysis = {} }) => {
    return (
        <div className="space-y-6 h-full">
            {/* Strengths & Improvements Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Key Strengths */}
                <div className="bg-emerald-50/50 backdrop-blur-xl p-6 rounded-2xl border border-emerald-100">
                    <h3 className="text-lg font-bold text-emerald-800 mb-4 flex items-center gap-2">
                        <span>💪</span> Key Strengths
                    </h3>
                    <ul className="space-y-2">
                        {strengths.map((str, i) => (
                            <li key={i} className="text-emerald-700 text-sm flex items-start gap-2">
                                <span className="mt-1">✓</span>
                                <span>{str}</span>
                            </li>
                        ))}
                        {strengths.length === 0 && <li className="text-emerald-700/50 text-sm italic">No specific strengths highlighted.</li>}
                    </ul>
                </div>

                {/* Areas for Improvement */}
                <div className="bg-amber-50/50 backdrop-blur-xl p-6 rounded-2xl border border-amber-100">
                    <h3 className="text-lg font-bold text-amber-800 mb-4 flex items-center gap-2">
                        <span>🔨</span> Areas for Improvement
                    </h3>
                    <ul className="space-y-2">
                        {improvements.map((imp, i) => (
                            <li key={i} className="text-amber-700 text-sm flex items-start gap-2">
                                <span className="mt-1">⚡</span>
                                <span>{imp}</span>
                            </li>
                        ))}
                        {improvements.length === 0 && <li className="text-amber-700/50 text-sm italic">No specific improvements suggested.</li>}
                    </ul>
                </div>
            </div>

            {/* Specialized Analysis Grid */}
            {(pptAnalysis.comments || videoAnalysis.comments) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* PPT Analysis */}
                    {pptAnalysis.comments && (
                        <div className="bg-orange-50/50 backdrop-blur-xl p-6 rounded-2xl border border-orange-100">
                            <h3 className="text-lg font-bold text-orange-800 mb-4 flex items-center gap-2">
                                <span>📑</span> Presentation Analysis
                            </h3>
                            <div className="space-y-3">
                                <div className="flex gap-2">
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${pptAnalysis.is_relevant ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                        {pptAnalysis.is_relevant ? "Relevant to Project" : "Irrelevant Content"}
                                    </span>
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${pptAnalysis.is_ai_generated ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                                        {pptAnalysis.is_ai_generated ? "Likely AI-Generated" : "Manually Created"}
                                    </span>
                                </div>
                                <p className="text-orange-900/80 text-sm leading-relaxed">
                                    {pptAnalysis.comments}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Video Analysis */}
                    {videoAnalysis.comments && (
                        <div className="bg-cyan-50/50 backdrop-blur-xl p-6 rounded-2xl border border-cyan-100">
                            <h3 className="text-lg font-bold text-cyan-800 mb-4 flex items-center gap-2">
                                <span>🎥</span> Video Analysis
                            </h3>
                            <div className="space-y-3">
                                <div className="flex gap-2 items-center mb-2">
                                    <span className="text-sm font-semibold text-cyan-700">Clarity Score:</span>
                                    <div className="flex gap-1">
                                        {[...Array(5)].map((_, i) => (
                                            <div key={i} className={`w-2 h-2 rounded-full ${i < (videoAnalysis.clarity_score || 0) ? 'bg-cyan-500' : 'bg-cyan-200'}`} />
                                        ))}
                                    </div>
                                </div>
                                <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold mb-2 ${videoAnalysis.is_engaging ? 'bg-teal-100 text-teal-700' : 'bg-slate-100 text-slate-600'}`}>
                                    {videoAnalysis.is_engaging ? "Highly Engaging" : "Needs More Energy"}
                                </span>
                                <p className="text-cyan-900/80 text-sm leading-relaxed">
                                    {videoAnalysis.comments}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Suggested Questions */}
            <div className="bg-blue-50/50 backdrop-blur-xl p-6 rounded-2xl border border-blue-100">
                <h3 className="text-lg font-bold text-blue-800 mb-4 flex items-center gap-2">
                    <span>🤔</span> Suggested Q&A Questions
                </h3>
                <ul className="space-y-2">
                    {questions.map((q, i) => (
                        <li key={i} className="text-blue-700 text-sm flex items-start gap-2">
                            <span className="font-bold text-blue-400">Q:</span>
                            <span>{q}</span>
                        </li>
                    ))}
                    {questions.length === 0 && <li className="text-blue-700/50 text-sm italic">No questions generated.</li>}
                </ul>
            </div>

            {/* AI Feedback Card */}
            <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/60 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-indigo-100 transition-colors duration-500"></div>

                <div className="flex items-center gap-4 mb-6 relative z-10">
                    <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center text-2xl shadow-sm text-indigo-600">
                        🤖
                    </div>
                    <h3 className="text-2xl font-bold text-slate-800">
                        AI Verdict
                    </h3>
                </div>

                <div className="prose prose-slate max-w-none relative z-10">
                    <p className="text-slate-600 leading-relaxed text-lg whitespace-pre-wrap">
                        {feedback}
                    </p>
                </div>
            </div>

            {/* Why Won't Win Card */}
            <div className="bg-white/90 backdrop-blur-xl p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-red-100 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-red-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-50"></div>

                <div className="flex items-center gap-4 mb-6 relative z-10">
                    <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center text-2xl shadow-sm text-red-500">
                        ⚠️
                    </div>
                    <h3 className="text-2xl font-bold text-red-600">Why It Won't Win</h3>
                </div>

                <div className="bg-red-50/50 p-6 rounded-xl border border-red-100 relative z-10">
                    <p className="text-slate-700 leading-relaxed text-lg whitespace-pre-wrap font-medium">
                        {whyWontWin}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default FeedbackSection;
