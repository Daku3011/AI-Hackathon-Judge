import React from 'react';
import ReactMarkdown from 'react-markdown';

const LanguageBar = ({ languages }) => {
    if (!languages || typeof languages === 'string' || Object.keys(languages).length === 0) {
        return (
            <div className="bg-white/60 backdrop-blur-md p-4 rounded-xl border border-white/80 shadow-sm col-span-2">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Languages</div>
                <div className="text-lg font-bold text-slate-700 flex items-center gap-2">
                    <span className="text-indigo-500">💻</span> {typeof languages === 'string' ? languages : "Unknown"}
                </div>
            </div>
        );
    }

    const totalBytes = Object.values(languages).reduce((a, b) => a + b, 0);
    const sortedLanguages = Object.entries(languages)
        .sort(([, a], [, b]) => b - a)
        .map(([name, bytes]) => ({
            name,
            percentage: ((bytes / totalBytes) * 100).toFixed(1),
            color: getLanguageColor(name)
        }));

    return (
        <div className="bg-white/60 backdrop-blur-md p-4 rounded-xl border border-white/80 shadow-sm col-span-2">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Languages</div>

            {/* Percentage Bar */}
            <div className="w-full h-3 flex rounded-full overflow-hidden mb-3 bg-slate-100">
                {sortedLanguages.map((lang, i) => (
                    <div
                        key={i}
                        className="h-full first:rounded-l-full last:rounded-r-full"
                        style={{
                            width: `${lang.percentage}%`,
                            backgroundColor: lang.color,
                            transition: 'width 1s ease-out'
                        }}
                        title={`${lang.name}: ${lang.percentage}%`}
                    />
                ))}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-x-4 gap-y-1">
                {sortedLanguages.slice(0, 5).map((lang, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-xs font-medium text-slate-600">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: lang.color }} />
                        <span>{lang.name}</span>
                        <span className="text-slate-400 font-normal">{lang.percentage}%</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

const getLanguageColor = (lang) => {
    const colors = {
        'JavaScript': '#f1e05a',
        'TypeScript': '#3178c6',
        'Python': '#3572A5',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Vue': '#41b883',
        'React': '#61dafb',
        'PHP': '#4F5D95',
        'Java': '#b07219',
        'C++': '#f34b7d',
        'C#': '#178600',
        'Go': '#00ADD8',
        'Ruby': '#701516',
        'Rust': '#dea584',
        'Dart': '#00B4AB',
        'Swift': '#F05138',
        'Kotlin': '#A97BFF',
        'Shell': '#89e051',
        'Dockerfile': '#384d54',
    };
    return colors[lang] || '#CBD5E1'; // Default slate-300
};

const FeedbackSection = ({ 
    feedback, 
    whyWontWin, 
    strengths = [], 
    improvements = [], 
    questions = [], 
    pptAnalysis = {}, 
    videoAnalysis = {}, 
    winProbability = 0, 
    roadmap = [], 
    securityIssues = [], 
    languages = "Unknown", 
    filesCount = 0, 
    estimatedLoc = 0,
    siteAnalysis = null,
    isGithub = true,
    judgeName = "AI Judge" 
}) => {
    return (
        <div className="space-y-6 h-full pb-10">
            {/* Project Overview Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <LanguageBar languages={isGithub ? languages : (siteAnalysis?.tech_stack || "Web Stack")} />

                <div className="bg-white/60 backdrop-blur-md p-4 rounded-xl border border-white/80 shadow-sm">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                        {isGithub ? "Codebase" : "Site Size"}
                    </div>
                    <div className="text-lg font-bold text-slate-700 flex items-center gap-2">
                        {isGithub ? (
                            <>
                                <span className="text-emerald-500 text-xl">📁</span> {filesCount} Files
                            </>
                        ) : (
                            <>
                                <span className="text-blue-500 text-xl">📄</span> {siteAnalysis?.page_size_kb?.toFixed(1) || 0} KB
                            </>
                        )}
                    </div>
                </div>

                {isGithub && estimatedLoc > 0 && (
                    <div className="bg-white/60 backdrop-blur-md p-4 rounded-xl border border-white/80 shadow-sm">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Lines of Code</div>
                        <div className="text-lg font-bold text-slate-700 flex items-center gap-2">
                            <span className="text-orange-500 text-xl">📏</span> {estimatedLoc.toLocaleString()} LOC
                        </div>
                    </div>
                )}

                {!isGithub && siteAnalysis && (
                    <div className="bg-white/60 backdrop-blur-md p-4 rounded-xl border border-white/80 shadow-sm">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Routes</div>
                        <div className="text-lg font-bold text-slate-700 flex items-center gap-2">
                            <span className="text-purple-500 text-xl">🔗</span> {siteAnalysis.routes_count} Pinpoints
                        </div>
                    </div>
                )}

                <div className={`p-4 rounded-xl border backdrop-blur-md shadow-sm flex flex-col justify-center ${winProbability > 70 ? 'bg-emerald-50/80 border-emerald-100' : winProbability > 40 ? 'bg-amber-50/80 border-amber-100' : 'bg-red-50/80 border-red-100'}`}>
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Win Probability™</div>
                    <div className={`text-lg font-black flex items-center gap-2 ${winProbability > 70 ? 'text-emerald-600' : winProbability > 40 ? 'text-amber-600' : 'text-red-600'}`}>
                        {winProbability}%
                        <span className="text-[10px] font-medium opacity-60">{winProbability > 70 ? "Legendary" : winProbability > 40 ? "Candidate" : "Needs Pivot"}</span>
                    </div>
                </div>
            </div>

            {/* Security Alerts */}
            {securityIssues.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                    <h3 className="text-red-800 font-bold flex items-center gap-2 mb-2">
                        <span>🛡️</span> Security Critical Alerts
                    </h3>
                    <ul className="space-y-1">
                        {securityIssues.map((issue, i) => (
                            <li key={i} className="text-red-700 text-sm font-mono bg-red-100/50 p-2 rounded">{issue}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* AI Feedback Card */}
            <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/60 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-indigo-100 transition-colors duration-500 pointer-events-none"></div>

                <div className="flex items-center gap-4 mb-8 relative z-10">
                    <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center text-2xl shadow-sm border border-indigo-100 text-indigo-600">
                        🤖
                    </div>
                    <div>
                        <h3 className="text-2xl font-black text-slate-800 tracking-tight">
                            Consensus Verdict
                        </h3>
                        <div className="flex items-center gap-2 mt-0.5">
                            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">5 Judges Aggregated</span>
                        </div>
                    </div>
                </div>

                <div className="space-y-6 relative z-10">
                    {/* Split feedback by judge if it follows the [JUDGE] format */}
                    {feedback.split(/\[(VC|CTO|PRODUCT|UIUX|PROFESSOR)\]/i).filter(Boolean).map((part, i, arr) => {
                        if (['VC', 'CTO', 'PRODUCT', 'UIUX', 'PROFESSOR'].includes(part.toUpperCase())) {
                            const judgeLabel = part.toUpperCase();
                            const judgeContent = arr[i + 1] || "";

                            const judgeStyles = {
                                'VC': { bg: 'bg-blue-50/50', border: 'border-blue-100', text: 'text-blue-700', icon: '💰' },
                                'CTO': { bg: 'bg-slate-50/50', border: 'border-slate-200', text: 'text-slate-700', icon: '💻' },
                                'PRODUCT': { bg: 'bg-purple-50/50', border: 'border-purple-100', text: 'text-purple-700', icon: '🎨' },
                                'UIUX': { bg: 'bg-pink-50/50', border: 'border-pink-100', text: 'text-pink-700', icon: '✨' },
                                'PROFESSOR': { bg: 'bg-emerald-50/50', border: 'border-emerald-100', text: 'text-emerald-700', icon: '🎓' }
                            }[judgeLabel] || { bg: 'bg-slate-50', border: 'border-slate-100', text: 'text-slate-600', icon: '⚖️' };

                            return (
                                <div key={i} className={`${judgeStyles.bg} ${judgeStyles.border} border p-5 rounded-xl transition-all hover:bg-white shadow-sm hover:shadow-md`}>
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="text-lg">{judgeStyles.icon}</span>
                                        <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${judgeStyles.text}`}>{judgeLabel} Persona</span>
                                    </div>
                                    <div className="prose prose-slate max-w-none prose-p:text-slate-600 prose-p:text-base prose-p:leading-relaxed">
                                        <ReactMarkdown>{judgeContent.trim()}</ReactMarkdown>
                                    </div>
                                </div>
                            );
                        }
                        return null;
                    })}

                    {/* Fallback if no judge markers found */}
                    {!feedback.match(/\[(VC|CTO|PRODUCT|UIUX|PROFESSOR)\]/i) && (
                        <div className="prose prose-slate max-w-none prose-p:text-slate-600 prose-p:text-lg prose-p:leading-relaxed">
                            <ReactMarkdown>{feedback}</ReactMarkdown>
                        </div>
                    )}
                </div>
            </div>

            {/* Why Won't Win Card */}
            <div className="bg-white/95 backdrop-blur-xl p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-red-100 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-red-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-50 pointer-events-none"></div>

                <div className="flex items-center gap-4 mb-6 relative z-10">
                    <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center text-2xl shadow-sm border border-red-100 text-red-500">
                        ⚠️
                    </div>
                    <h3 className="text-2xl font-black text-red-600 tracking-tight">Reality Check: Why It Won't Win</h3>
                </div>

                <div className="bg-red-50/30 p-6 rounded-xl border border-red-100 relative z-10 prose prose-red max-w-none prose-p:text-slate-700 prose-p:text-lg prose-p:font-medium prose-p:leading-relaxed">
                    <ReactMarkdown>{whyWontWin}</ReactMarkdown>
                </div>
            </div>

            {/* Strengths & Improvements Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Key Strengths */}
                <div className="bg-emerald-50/50 backdrop-blur-xl p-6 rounded-2xl border border-emerald-100 shadow-sm">
                    <h3 className="text-lg font-bold text-emerald-800 mb-4 flex items-center gap-2">
                        <span>💪</span> Key Strengths
                    </h3>
                    <ul className="space-y-3">
                        {strengths.map((str, i) => (
                            <li key={i} className="text-emerald-700 text-sm flex items-start gap-2">
                                <span className="mt-1 bg-emerald-100 text-emerald-600 rounded-full p-0.5">
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                                </span>
                                <span>{str}</span>
                            </li>
                        ))}
                        {strengths.length === 0 && <li className="text-emerald-700/50 text-sm italic">No specific strengths highlighted.</li>}
                    </ul>
                </div>

                {/* Areas for Improvement */}
                <div className="bg-amber-50/50 backdrop-blur-xl p-6 rounded-2xl border border-amber-100 shadow-sm">
                    <h3 className="text-lg font-bold text-amber-800 mb-4 flex items-center gap-2">
                        <span>🔨</span> Areas for Improvement
                    </h3>
                    <ul className="space-y-3">
                        {improvements.map((imp, i) => (
                            <li key={i} className="text-amber-700 text-sm flex items-start gap-2">
                                <span className="mt-1 bg-amber-100 text-amber-600 rounded-full p-0.5">
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                                </span>
                                <span>{imp}</span>
                            </li>
                        ))}
                        {improvements.length === 0 && <li className="text-amber-700/50 text-sm italic">No specific improvements suggested.</li>}
                    </ul>
                </div>
            </div>

            {/* Project Roadmap */}
            {roadmap.length > 0 && (
                <div className="bg-indigo-50/50 backdrop-blur-xl p-6 rounded-2xl border border-indigo-100 shadow-sm">
                    <h3 className="text-lg font-bold text-indigo-800 mb-4 flex items-center gap-2">
                        <span>🚀</span> Recommended Roadmap (Mentor Mode)
                    </h3>
                    <div className="space-y-4 relative before:absolute before:left-[11px] before:top-2 before:h-full before:w-[2px] before:bg-indigo-200">
                        {roadmap.map((step, i) => (
                            <div key={i} className="relative pl-8">
                                <div className="absolute left-0 top-1 w-6 h-6 bg-indigo-100 border-2 border-indigo-500 rounded-full flex items-center justify-center text-[10px] font-bold text-indigo-700 z-10">
                                    {i + 1}
                                </div>
                                <p className="text-indigo-900 text-sm font-medium">{step}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Specialized Analysis Grid */}
            {/* Specialized Analysis Grid */}
            {(Object.keys(pptAnalysis).length > 0 || Object.keys(videoAnalysis).length > 0) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* PPT Analysis */}
                    {Object.keys(pptAnalysis).length > 0 && (
                        <div className="bg-orange-50/50 backdrop-blur-xl p-6 rounded-2xl border border-orange-100 shadow-sm">
                            <h3 className="text-lg font-bold text-orange-800 mb-4 flex items-center gap-2">
                                <span>📑</span> Presentation Analysis
                            </h3>
                            <div className="space-y-3">
                                <div className="flex gap-2">
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${pptAnalysis.is_relevant ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                        {pptAnalysis.is_relevant ? "Relevant" : "Irrelevant"}
                                    </span>
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${pptAnalysis.is_ai_generated ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                                        {pptAnalysis.is_ai_generated ? "AI-Gen" : "Manual"}
                                    </span>
                                </div>
                                <p className="text-orange-900/80 text-sm leading-relaxed italic">
                                    "{pptAnalysis.comments || "No specific comments provided."}"
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Video Analysis */}
                    {Object.keys(videoAnalysis).length > 0 && (
                        <div className="bg-cyan-50/50 backdrop-blur-xl p-6 rounded-2xl border border-cyan-100 shadow-sm">
                            <h3 className="text-lg font-bold text-cyan-800 mb-4 flex items-center gap-2">
                                <span>🎥</span> Video Pitch Analysis
                            </h3>
                            <div className="space-y-3">
                                <div className="flex gap-2 items-center mb-2">
                                    <span className="text-[10px] font-black uppercase tracking-widest text-cyan-700">Clarity:</span>
                                    <div className="flex gap-1">
                                        {[...Array(5)].map((_, i) => (
                                            <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < (videoAnalysis.clarity_score || 0) / 2 ? 'bg-cyan-500' : 'bg-cyan-200'}`} />
                                        ))}
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-2 mb-2">
                                    <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${videoAnalysis.confidence_score > 7 ? 'bg-teal-100 text-teal-700' : 'bg-slate-100 text-slate-600'}`}>
                                        Conf: {videoAnalysis.confidence_score !== undefined ? `${videoAnalysis.confidence_score}/10` : "N/A"}
                                    </span>
                                    <span className="inline-block px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-sky-100 text-sky-700">
                                        Pace: {videoAnalysis.pacing_score !== undefined ? `${videoAnalysis.pacing_score}/10` : "N/A"}
                                    </span>
                                    <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${videoAnalysis.filler_words === 'low' ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'}`}>
                                        Filler: {videoAnalysis.filler_words || "N/A"}
                                    </span>
                                </div>
                                <p className="text-cyan-900/80 text-sm leading-relaxed italic">
                                    "{videoAnalysis.comments || "No specific comments provided."}"
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Suggested Questions */}
            <div className="bg-blue-50/50 backdrop-blur-xl p-6 rounded-2xl border border-blue-100 shadow-sm">
                <h3 className="text-lg font-bold text-blue-800 mb-4 flex items-center gap-2">
                    <span>🤔</span> Likely Q&A Questions
                </h3>
                <ul className="space-y-3">
                    {questions.map((q, i) => (
                        <li key={i} className="text-blue-700 text-sm flex items-start gap-3 bg-white/40 p-3 rounded-lg border border-blue-100/50">
                            <span className="font-black text-blue-400">Q:</span>
                            <span className="font-medium text-slate-700">{q}</span>
                        </li>
                    ))}
                    {questions.length === 0 && <li className="text-blue-700/50 text-sm italic text-center py-4">No questions generated.</li>}
                </ul>
            </div>
        </div>
    );
};

export default FeedbackSection;
