import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ScoreCard from './components/Scorecard';
import FeedbackSection from './components/FeedbackSection';

function App() {
  const [appState, setAppState] = useState('input'); // input, analyzing, results
  const [results, setResults] = useState(null);

  const handleAnalyze = async (data) => {
    setAppState('analyzing');

    try {
      // Use localhost:8000 for backend
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Handle potential mock fallback or real structure
      setResults({
        scores: result.scores || { innovation: 0, quality: 0, uiux: 0, impact: 0 },
        feedback: result.feedback || "No feedback generated.",
        whyWontWin: result.whyWontWin || "N/A"
      });
      setAppState('results');

    } catch (error) {
      console.error(error);
      setAppState('input');
      alert(`Failed to connect to backend: ${error.message}\nMake sure backend is running on port 8000.`);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-4 md:p-8 relative overflow-hidden">
      {/* Background Decor - Blobs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-200/40 rounded-full blur-[120px]"></div>
        <div className="absolute top-[10%] right-[-10%] w-[40%] h-[40%] bg-indigo-200/40 rounded-full blur-[100px]"></div>
        <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[60%] bg-blue-100/40 rounded-full blur-[120px]"></div>
      </div>

      <header className="max-w-4xl mx-auto mb-10 md:mb-16 text-center pt-8">
        <h1 className="text-4xl md:text-6xl font-black mb-4 tracking-tight text-slate-900">
          AI <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Hackathon</span> Judge
        </h1>
        <p className="text-slate-500 text-lg md:text-xl font-medium max-w-2xl mx-auto leading-relaxed">
          Evaluate your project locally with <span className="text-indigo-600 font-semibold">brutal honesty</span> before the real judges do.
        </p>
      </header>

      <main className="max-w-5xl mx-auto pb-20">
        {appState === 'input' && (
          <InputForm onSubmit={handleAnalyze} isLoading={false} />
        )}

        {appState === 'analyzing' && (
          <div className="text-center py-32 animate-in fade-in duration-700">
            <div className="relative inline-block">
              <div className="absolute inset-0 bg-indigo-500 blur-xl opacity-20 animate-pulse"></div>
              <div className="relative inline-block animate-spin rounded-full h-16 w-16 border-4 border-indigo-100 border-t-indigo-600 mb-6"></div>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Analyzing Project...</h2>
            <p className="text-slate-500">Reading GitHub repo, watching video, and judging life choices.</p>
          </div>
        )}

        {appState === 'results' && results && (
          <div className="grid lg:grid-cols-3 gap-8 animate-in slide-in-from-bottom-8 duration-700 fade-in">
            <div className="lg:col-span-1 order-2 lg:order-1">
              <ScoreCard scores={results.scores} onRetry={() => setAppState('input')} />
            </div>
            <div className="lg:col-span-2 order-1 lg:order-2">
              <FeedbackSection
                feedback={results.feedback}
                whyWontWin={results.whyWontWin}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
