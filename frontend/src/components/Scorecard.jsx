import React from 'react';

const ScoreCard = ({ scores, overallScore, onRetry, securityIssues = [] }) => {
    // scores: { innovation, technical, relevance, uiux, impact, presentation }

    const getScoreColor = (value) => {
        if (value >= 8) return 'from-emerald-400 to-teal-500';
        if (value >= 5) return 'from-amber-400 to-orange-500';
        return 'from-red-400 to-pink-500';
    };

    const ScoreItem = ({ label, score, customValue }) => (
        <div className="mb-6 group w-full">
            <div className="flex justify-between mb-2 items-end gap-4">
                <span className="text-slate-400 font-bold text-[11px] uppercase tracking-[0.15em] group-hover:text-slate-600 transition-colors pt-0.5 leading-tight">{label}</span>
                <span className="text-slate-800 font-black text-lg tabular-nums whitespace-nowrap">
                    {customValue || (
                        <>
                            {score || 0}<span className="text-slate-400 text-sm font-bold">/10</span>
                        </>
                    )}
                </span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden shadow-inner">
                <div
                    className={`h-full rounded-full bg-gradient-to-r ${getScoreColor(score || 0)} transition-all duration-1000 ease-out shadow-sm`}
                    style={{ width: `${((score || 0) / 10) * 100}%` }}
                ></div>
            </div>
        </div>
    );

    return (
        <div className="bg-white/80 backdrop-blur-2xl p-10 rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.05)] border border-white/60 h-full flex flex-col justify-between relative overflow-hidden group/card">
            {/* Background Gradient Detail */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50/50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover/card:bg-indigo-100/50 transition-colors duration-700"></div>

            <div className="relative z-10">
                <div className="flex items-center justify-between mb-8">
                    <h3 className="text-2xl font-black text-slate-800 tracking-tight">Project Scorecard</h3>
                </div>

                {/* Overall Score Circle */}
                <div className="flex flex-col items-center justify-center mb-12 relative">
                    <div className="relative group">
                        <div className="absolute -inset-6 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-full blur-2xl opacity-70 group-hover:opacity-100 transition-opacity duration-500 animate-pulse"></div>
                        <div className="w-44 h-44 rounded-full border-4 border-slate-50/50 flex items-center justify-center bg-white shadow-[0_15px_35px_rgba(0,0,0,0.1)] relative z-10 p-2">
                            <div className="w-full h-full rounded-full border-4 border-indigo-50 flex items-center justify-center">
                                <div className="text-center">
                                    <div className={`text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br ${getScoreColor(overallScore)} tracking-tighter`}>
                                        {overallScore}
                                    </div>
                                    <div className="text-slate-400 text-[10px] font-black tracking-[0.3em] mt-1 uppercase">Overall</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col gap-1 max-w-md mx-auto">
                    <ScoreItem label="Innovation" score={scores.innovation} />
                    <ScoreItem label="Tech Implementation" score={scores.technical} />
                    <ScoreItem label="Problem Relevance" score={scores.relevance} />
                    <ScoreItem label="UI/UX Design" score={scores.uiux} />
                    <ScoreItem label="Impact & Feasibility" score={scores.impact} />
                    <ScoreItem label="Presentation" score={scores.presentation} />
                    <ScoreItem
                        label="Security Status"
                        score={securityIssues.length === 0 ? 10 : 3}
                        customValue={securityIssues.length === 0 ? "Protected" : "Vulnerable"}
                    />
                </div>
            </div>

            <div className="mt-10 pt-8 border-t border-slate-100 relative z-10">
                <button
                    onClick={onRetry}
                    className="w-full py-4 rounded-xl font-black text-sm uppercase tracking-widest bg-slate-900 text-white hover:bg-indigo-600 hover:shadow-xl hover:shadow-indigo-500/20 transition-all active:scale-[0.98]"
                >
                    Analyze New Project
                </button>
            </div>
        </div>
    );
};

export default ScoreCard;
