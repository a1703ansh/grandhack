'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, ArrowRight, Brain, Clock, Target, Compass } from 'lucide-react';
import { UserPreferences } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';

const MOCK_TOPICS = [
  "Deep Learning",
  "Data Science",
  "Full Stack Web Development",
  "UI/UX Design",
  "Cloud Computing"
];

export default function Home() {
  const router = useRouter();
  const [goal, setGoal] = useState('');
  const [currentKnowledge, setCurrentKnowledge] = useState('');
  const [weeks, setWeeks] = useState(12);
  const [hours, setHours] = useState(10);
  const [isLoading, setIsLoading] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredTopics, setFilteredTopics] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleGoalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setGoal(value);
    
    if (value.trim()) {
      const filtered = MOCK_TOPICS.filter(t => t.toLowerCase().includes(value.toLowerCase()));
      setFilteredTopics(filtered);
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
    setActiveIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown || filteredTopics.length === 0) return;
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex(prev => (prev < filteredTopics.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex(prev => (prev > 0 ? prev - 1 : prev));
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      selectTopic(filteredTopics[activeIndex]);
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const selectTopic = (topic: string) => {
    setGoal(topic);
    setShowDropdown(false);
    setActiveIndex(-1);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal) return;
    
    setIsLoading(true);
    
    const prefs: UserPreferences = {
      goal,
      currentKnowledge,
      weeksAvailable: weeks,
      weeklyHours: hours
    };
    
    localStorage.setItem('cf_preferences', JSON.stringify(prefs));
    
    // Simulate loading for better UX
    setTimeout(() => {
      router.push('/roadmap');
    }, 1200);
  };

  const quickStarts = [
    'Deep Learning',
    'Data Analyst',
    'Web Development',
    'GATE CS Prep'
  ];

  return (
    <main className="flex-1 flex flex-col items-center justify-center min-h-screen pt-20 pb-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      
      {/* Background decorations */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-electric/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-violet/20 rounded-full blur-[100px] pointer-events-none" />
      
      <div className="max-w-4xl w-full text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-primary-gold text-sm font-medium mb-8">
          <Sparkles className="w-4 h-4" />
          <span>Learn anything for free</span>
        </div>
        
        <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight mb-6 text-white drop-shadow-sm">
          Your free, personalized path to <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-gold to-light-gold">any skill.</span>
        </h1>
        
        <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
          Tell us what you want to learn. We analyze prerequisites and generate an ordered learning roadmap using the best free courses from MIT, Khan Academy, and YouTube.
        </p>
        
        <div className="relative max-w-3xl mx-auto group">
          {/* Gradient Border Glow */}
          <div className="absolute -inset-[1px] bg-gradient-to-r from-dark-gold via-primary-gold to-light-gold rounded-2xl opacity-30 group-hover:opacity-60 transition duration-500 blur-sm"></div>
          
          <div className="relative glass-panel bg-navy/80 p-6 sm:p-8 rounded-2xl text-left shadow-2xl backdrop-blur-2xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2 relative" ref={dropdownRef}>
                <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary-gold" /> What is your goal?
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Master Deep Learning"
                  value={goal}
                  onChange={handleGoalChange}
                  onKeyDown={handleKeyDown}
                  onFocus={() => {
                    if (goal.trim() && filteredTopics.length > 0) setShowDropdown(true);
                  }}
                  className="w-full bg-navy/50 border border-navy-lighter rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary-gold focus:ring-1 focus:ring-primary-gold transition-all"
                />
                
                <AnimatePresence>
                  {showDropdown && filteredTopics.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                      className="absolute left-0 right-0 top-full mt-2 bg-[#121212] border border-primary-gold/30 rounded-lg overflow-hidden z-50 shadow-xl"
                    >
                      <ul className="py-1">
                        {filteredTopics.map((topic, index) => (
                          <li
                            key={topic}
                            onClick={() => selectTopic(topic)}
                            onMouseEnter={() => setActiveIndex(index)}
                            className={`px-4 py-3 cursor-pointer transition-colors text-sm ${
                              activeIndex === index 
                                ? 'bg-[#1A1A1A] text-primary-gold' 
                                : 'text-gray-300 hover:bg-[#1A1A1A] hover:text-primary-gold'
                            }`}
                          >
                            {topic}
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-dark-gold" /> What do you already know?
                </label>
                <input
                  type="text"
                  placeholder="e.g. Python basics"
                  value={currentKnowledge}
                  onChange={(e) => setCurrentKnowledge(e.target.value)}
                  className="w-full bg-navy/50 border border-navy-lighter rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary-gold focus:ring-1 focus:ring-primary-gold transition-all"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center justify-between">
                  <span className="flex items-center gap-2"><Clock className="w-4 h-4 text-light-gold" /> Weeks available</span>
                  <span className="text-primary-gold">{weeks} weeks</span>
                </label>
                <input
                  type="range"
                  min="4"
                  max="52"
                  value={weeks}
                  onChange={(e) => setWeeks(Number(e.target.value))}
                  className="w-full accent-primary-gold"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center justify-between">
                  <span className="flex items-center gap-2"><Compass className="w-4 h-4 text-light-gold" /> Hours per week</span>
                  <span className="text-primary-gold">{hours} hrs/wk</span>
                </label>
                <input
                  type="range"
                  min="2"
                  max="40"
                  value={hours}
                  onChange={(e) => setHours(Number(e.target.value))}
                  className="w-full accent-primary-gold"
                />
              </div>
            </div>
            
            <button
              type="submit"
              disabled={isLoading || !goal}
              className="w-full bg-white text-navy font-bold py-4 rounded-xl hover:bg-gray-100 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group mt-4"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-navy border-t-transparent rounded-full animate-spin" />
                  Analyzing prerequisite graph...
                </>
              ) : (
                <>
                  Generate Roadmap
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
                )}
              </button>
            </form>
          </div>
        </div>
        
        <div className="mt-12 flex flex-col items-center">
          <p className="text-sm text-gray-500 mb-4">Or try a quick start:</p>
          <div className="flex flex-wrap justify-center gap-3">
            {quickStarts.map(start => (
              <button
                key={start}
                onClick={() => setGoal(start)}
                className="px-4 py-2 rounded-full border border-navy-lighter bg-navy-light/50 text-gray-300 hover:text-white hover:border-primary-gold transition-colors text-sm"
              >
                {start}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
