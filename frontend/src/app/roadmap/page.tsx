'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Roadmap, UserPreferences } from '@/types';
import { generateRoadmap, exportUrl } from '@/lib/api';
import { InteractiveGraph } from '@/components/ui/InteractiveGraph';
import { RoadmapTimeline } from '@/components/ui/RoadmapTimeline';
import { Download, Calendar, ArrowLeft, Network } from 'lucide-react';
import Link from 'next/link';

export default function RoadmapPage() {
  const router = useRouter();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState<'markdown' | 'ics' | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [completedStages, setCompletedStages] = useState<Set<string>>(new Set());

  useEffect(() => {
    const prefsRaw = localStorage.getItem('cf_preferences');
    if (!prefsRaw) {
      router.push('/');
      return;
    }

    let prefs: UserPreferences;
    try {
      prefs = JSON.parse(prefsRaw) as UserPreferences;
    } catch {
      router.push('/');
      return;
    }

    generateRoadmap(prefs)
      .then(data => {
        // Restore any locally saved progress for this goal.
        const savedProgress = localStorage.getItem(`cf_progress_${prefs.goal}`);
        setCompletedStages(
          savedProgress ? new Set<string>(JSON.parse(savedProgress) as string[]) : new Set<string>(),
        );
        setPreferences(prefs);
        setRoadmap(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || 'Could not generate your roadmap.');
        setLoading(false);
      });
  }, [router]);

  const toggleComplete = (stageId: string) => {
    setCompletedStages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stageId)) {
        newSet.delete(stageId);
      } else {
        newSet.add(stageId);
      }
      
      // Save progress
      if (preferences) {
        localStorage.setItem(`cf_progress_${preferences.goal}`, JSON.stringify(Array.from(newSet)));
      }
      
      return newSet;
    });
  };

  const handleExport = (format: 'markdown' | 'ics') => {
    if (!roadmap) return;
    setExporting(format);
    const anchor = document.createElement('a');
    anchor.href = exportUrl(roadmap.id, format);
    anchor.rel = 'noopener';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setExporting(null);
  };

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
        <h1 className="text-2xl font-bold text-white mb-3">We couldn&apos;t build that roadmap</h1>
        <p className="text-gray-400 mb-6 max-w-md">{error}</p>
        <Link href="/" className="px-5 py-3 rounded-lg bg-primary-gold text-black font-semibold hover:bg-light-gold transition-colors">
          Try another goal
        </Link>
      </div>
    );
  }

  if (loading || !roadmap) {
    return (
      <div className="min-h-screen pb-20">
        <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-xl border-b border-navy-lighter">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between mb-4">
              <div className="w-24 h-4 bg-navy-lighter rounded animate-pulse-slow"></div>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-navy-lighter rounded-lg animate-pulse-slow"></div>
                <div className="w-10 h-10 bg-navy-lighter rounded-lg animate-pulse-slow"></div>
              </div>
            </div>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
              <div className="space-y-3">
                <div className="w-48 h-4 bg-navy-lighter rounded animate-pulse-slow"></div>
                <div className="w-64 md:w-96 h-10 bg-navy-light rounded-lg animate-pulse-slow"></div>
                <div className="w-56 h-4 bg-navy-lighter rounded animate-pulse-slow"></div>
              </div>
              <div className="w-full md:w-64 space-y-2">
                <div className="w-full flex justify-between"><div className="w-12 h-4 bg-navy-lighter rounded animate-pulse-slow"></div><div className="w-8 h-4 bg-navy-lighter rounded animate-pulse-slow"></div></div>
                <div className="h-2 w-full bg-navy-lighter rounded-full"></div>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
          {/* Skeleton Graph */}
          <section>
            <div className="w-48 h-8 bg-navy-light rounded mb-6 animate-pulse-slow"></div>
            <div className="w-full h-[300px] bg-navy-light/50 rounded-2xl animate-pulse-slow border border-navy-lighter"></div>
          </section>

          {/* Skeleton Timeline */}
          <section>
            <div className="w-56 h-8 bg-navy-light rounded mb-8 animate-pulse-slow"></div>
            <div className="relative border-l border-navy-lighter ml-6 space-y-12 pb-12">
              {[1, 2, 3].map((i) => (
                <div key={i} className="relative pl-8 sm:pl-12">
                  <div className="absolute -left-[17px] top-1 w-8 h-8 rounded-full bg-navy-lighter border-4 border-background animate-pulse-slow"></div>
                  <div className="flex gap-2 mb-4">
                    <div className="w-16 h-4 bg-navy-lighter rounded animate-pulse-slow"></div>
                    <div className="w-16 h-4 bg-navy-lighter rounded animate-pulse-slow"></div>
                  </div>
                  <div className="w-3/4 h-8 bg-navy-light rounded mb-4 animate-pulse-slow"></div>
                  <div className="w-full h-16 bg-navy-lighter rounded mb-6 animate-pulse-slow"></div>
                  <div className="w-full h-24 bg-navy rounded-lg mb-8 animate-pulse-slow"></div>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="w-full h-48 bg-navy-light/50 rounded-xl animate-pulse-slow border border-navy-lighter"></div>
                    <div className="w-full h-48 bg-navy-light/50 rounded-xl animate-pulse-slow border border-navy-lighter hidden lg:block"></div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </main>
      </div>
    );
  }

  // Inject completed status into stages and graph nodes
  const stagesWithStatus = roadmap.stages.map(s => ({
    ...s,
    completed: completedStages.has(s.id)
  }));
  
  const graphWithStatus = {
    ...roadmap.graph,
    nodes: roadmap.graph.nodes.map(n => ({
      ...n,
      completed: completedStages.has(n.id)
    }))
  };

  const progressPercentage = stagesWithStatus.length > 0 
    ? Math.round((completedStages.size / stagesWithStatus.length) * 100) 
    : 0;

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-xl border-b border-navy-lighter">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm font-medium">New Goal</span>
            </Link>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleExport('ics')}
                disabled={exporting !== null}
                title="Add to calendar (.ics)"
                aria-label="Add to calendar"
                className="p-2 text-gray-400 hover:text-white bg-white/5 rounded-lg border border-white/10 transition-colors disabled:opacity-50"
              >
                <Calendar className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => handleExport('markdown')}
                disabled={exporting !== null}
                title="Download as Markdown"
                aria-label="Download as Markdown"
                className="p-2 text-gray-400 hover:text-white bg-white/5 rounded-lg border border-white/10 transition-colors disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <p className="text-sm text-electric mb-1 font-mono uppercase tracking-wider">{roadmap.totalWeeks}-week plan • {roadmap.totalHours} hrs total</p>
              <h1 className="text-3xl md:text-4xl font-bold text-white">Your {roadmap.goal} Roadmap</h1>
              {preferences?.currentKnowledge && (
                <p className="text-sm text-gray-400 mt-2">Adapted for your existing knowledge in: {preferences.currentKnowledge}</p>
              )}
            </div>
            
            <div className="w-full md:w-64">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Progress</span>
                <span className="text-white font-medium">{progressPercentage}%</span>
              </div>
              <div className="h-2 w-full bg-navy-lighter rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-mint to-electric transition-all duration-500 ease-out"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
        
        {/* Graph Section */}
        <section>
          <div className="flex items-center gap-2 mb-6">
            <Network className="w-6 h-6 text-violet" />
            <h2 className="text-2xl font-bold text-white">Prerequisite Map</h2>
          </div>
          <InteractiveGraph data={graphWithStatus} />
        </section>

        {/* Timeline Section */}
        <section>
          <div className="flex items-center gap-2 mb-8">
            <h2 className="text-2xl font-bold text-white">Learning Timeline</h2>
          </div>
          <RoadmapTimeline stages={stagesWithStatus} onToggleComplete={toggleComplete} />
        </section>

      </main>
    </div>
  );
}
