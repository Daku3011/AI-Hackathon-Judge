import React from 'react';

const ScoreCard = ({ scores, onRetry }) => {
    // scores: { innovation: number, quality: number, uiux: number, impact: number }
    const overallScore = ((scores.innovation + scores.quality + scores.uiux + scores.impact) / 4).toFixed(1);

    const getScoreColor = (value) => {
        if (value >= 8) return 'from-emerald-400 to-teal-500';
        if (value >= 5) return 'from-amber-400 to-orange-500';
        return 'from-red-400 to-pink-500';
    };

    const ScoreItem = ({ label, score }) => (
        <div className="mb-5 group">
            <div className="flex justify-between mb-2 items-end">
                <span className="text-slate-500 font-semibold text-xs uppercase tracking-wider group-hover:text-slate-700 transition-colors">{label}</span>
                <span className="text-slate-800 font-bold text-lg tabular-nums">{score}<span className="text-slate-400 text-sm font-medium">/10</span></span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                    className={`h-full rounded-full bg-gradient-to-r ${getScoreColor(score)} transition-all duration-1000 ease-out shadow-sm`}
                    style={{ width: `${(score / 10) * 100}%` }}
                ></div>
            </div>
        </div>
    );

    return (
        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/60 h-full flex flex-col justify-between">
            <div>
                <h3 className="text-xl font-bold text-slate-800 mb-6">Scorecard</h3>

                {/* Overall Score Circle */}
                <div className="flex flex-col items-center justify-center mb-10 relative">
                    <div className="relative group">
                        <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-full blur-xl opacity-70 group-hover:opacity-100 transition-opacity duration-500"></div>
                        <div className="w-40 h-40 rounded-full border-8 border-slate-50 flex items-center justify-center bg-white shadow-xl relative z-10">
                            <div className="text-center">
                                <div className={`text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br ${getScoreColor(overallScore)}`}>
                                    {overallScore}
                                </div>
                                <div className="text-slate-400 text-[10px] font-bold tracking-[0.2em] mt-1 uppercase">Overall</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-1">
                    <ScoreItem label="Innovation" score={scores.innovation} />
                    <ScoreItem label="Code Quality" score={scores.quality} />
                    <ScoreItem label="UI/UX" score={scores.uiux} />
                    <ScoreItem label="Impact" score={scores.impact} />
                </div>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100">
                <button
                    onClick={onRetry}
                    className="w-full py-3 rounded-lg font-bold bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-indigo-600 transition-all border border-slate-200 hover:border-indigo-200"
                >
                    Analyze Another Project
                </button>
            </div>
        </div>
    );
};

export default ScoreCard;
