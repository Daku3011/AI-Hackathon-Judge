import React from 'react';

const FeedbackSection = ({ feedback, whyWontWin }) => {
    return (
        <div className="space-y-8 h-full">
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
