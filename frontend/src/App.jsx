import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ScoreCard from './components/Scorecard';
import FeedbackSection from './components/FeedbackSection';
import LoadingScreen from './components/LoadingScreen';

import { YoutubeTranscript } from 'youtube-transcript';

function App() {
  const [appState, setAppState] = useState('input'); // input, analyzing, results
  const [results, setResults] = useState(null);

  const handleAnalyze = async (data) => {
    setAppState('analyzing');

    // Browser-side Transcript Fetching (Bypass Render IP Block)
    if (data instanceof FormData) {
      const videoUrl = data.get('video_url');
      const currentTranscript = data.get('manual_transcript');

      if (videoUrl && (!currentTranscript || currentTranscript.trim() === '')) {
        try {
          console.log("Attempting to fetch transcript in browser...");
          const transcriptItems = await YoutubeTranscript.fetchTranscript(videoUrl);
          const fullTranscript = transcriptItems.map(t => t.text).join(' ');

          if (fullTranscript) {
            console.log("Transcript fetched successfully via browser!");
            data.set('manual_transcript', fullTranscript);
          }
        } catch (error) {
          console.warn("Browser transcript fetch failed (likely no captions or popup blocker):", error);
          // alert(`Browser-side transcript fetch blocked by CORS (YouTube security).\n\nQUICK FIX (For Demo):\nInstall "Allow CORS" Chrome Extension and toggle it ON.\n\nOR\nManually paste the transcript in the text box below.`);
          console.log("Browser fetch failed, falling back to Backend (Cookie Auth) analysis.");
          // Fallback to backend (which might fail on Render, but worth a try or just error out)
        }
      }
    }

    try {
      // Use relative path for production (same origin), localhost for local dev
      const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');
      const options = {
        method: 'POST',
        body: data instanceof FormData ? data : JSON.stringify(data),
      };

      if (!(data instanceof FormData)) {
        options.headers = {
          'Content-Type': 'application/json',
        };
      }

      const response = await fetch(`${API_URL}/analyze`, options);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Handle potential mock fallback or real structure
      setResults({
        scores: result.scores || { innovation: 0, technical: 0, relevance: 0, uiux: 0, impact: 0, presentation: 0 },
        feedback: result.feedback || "No feedback generated.",
        whyWontWin: result.whyWontWin || "N/A",
        strengths: result.strengths || [],
        improvements: result.improvements || [],
        questions: result.questions || [],
        ppt_analysis: result.ppt_analysis || {},
        video_analysis: result.video_analysis || {},
        win_probability: result.win_probability || 0,
        project_roadmap: result.project_roadmap || [],
        security_issues: result.security_issues || [],
        languages: result.languages || "Unknown",
        files_count: result.files_count || 0,
        estimated_loc: result.estimated_loc || 0,
        site_analysis: result.site_analysis || null,
        is_github: result.is_github ?? true,
        judge_name: result.judge_name || "AI Judge"
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
          <LoadingScreen />
        )}

        {appState === 'results' && results && (
          <div className="grid lg:grid-cols-3 gap-8 animate-in slide-in-from-bottom-8 duration-700 fade-in">
            <div className="lg:col-span-1 order-2 lg:order-1">
              <ScoreCard
                scores={results.scores}
                overallScore={
                  results.scores.overall_score ||
                  ((Object.values(results.scores).reduce((a, b) => a + b, 0) + (results.security_issues.length === 0 ? 10 : 3)) / 7).toFixed(1)
                }
                securityIssues={results.security_issues}
                onRetry={() => setAppState('input')}
              />
            </div>
            <div className="lg:col-span-2 order-1 lg:order-2">
              <FeedbackSection
                feedback={results.feedback}
                whyWontWin={results.whyWontWin}
                strengths={results.strengths}
                improvements={results.improvements}
                questions={results.questions}
                pptAnalysis={results.ppt_analysis}
                videoAnalysis={results.video_analysis}
                winProbability={results.win_probability}
                roadmap={results.project_roadmap}
                securityIssues={results.security_issues}
                languages={results.languages}
                filesCount={results.files_count}
                estimatedLoc={results.estimated_loc}
                siteAnalysis={results.site_analysis}
                isGithub={results.is_github}
                judgeName={results.judge_name}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
