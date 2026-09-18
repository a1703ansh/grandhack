import { Course } from '@/types';
import { ExternalLink, Clock, Star, GraduationCap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { useMemo } from 'react';

interface CourseCardProps {
  course: Course;
  isBestMatch?: boolean;
}

export function CourseCard({ course, isBestMatch }: CourseCardProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-mint/10 text-mint-light border-mint/20';
      case 'Intermediate': return 'bg-electric/10 text-electric-hover border-electric/20';
      case 'Advanced': return 'bg-violet/10 text-violet-light border-violet/20';
      default: return 'bg-gray-500/10 text-gray-300 border-gray-500/20';
    }
  };

  // Stable illustrative progress derived from the course id (no randomness,
  // so server-rendered and client markup always agree).
  const progress = useMemo(() => {
    let hash = 0;
    for (let i = 0; i < course.id.length; i += 1) {
      hash = (hash * 31 + course.id.charCodeAt(i)) % 1000;
    }
    return 35 + (hash % 55);
  }, [course.id]);

  return (
    <div className="glass-panel p-5 rounded-xl hover:-translate-y-1 hover:shadow-[0_4px_30px_rgba(212,175,55,0.15)] hover:border-primary-gold/30 transition-all duration-300 group flex flex-col h-full relative overflow-hidden">
      {isBestMatch && (
        <div className="absolute top-0 right-0 bg-gradient-to-r from-dark-gold to-light-gold text-black text-[10px] font-bold px-3 py-1 uppercase tracking-wider rounded-bl-lg z-10">
          Best Match
        </div>
      )}
      
      <div className="flex items-center gap-2 mb-3 mt-1 relative z-10">
        <GraduationCap className="w-4 h-4 text-gray-400" />
        <span className="text-sm text-gray-400 font-medium">{course.source}</span>
      </div>
      
      <h4 className="text-lg font-semibold text-white mb-2 leading-tight group-hover:text-electric transition-colors relative z-10">{course.title}</h4>
      
      <div className="flex items-center gap-3 mb-4 relative z-10">
        <span className={cn("text-xs px-2 py-0.5 rounded-full border", getDifficultyColor(course.difficulty))}>
          {course.difficulty}
        </span>
        <div className="flex items-center text-xs text-gray-400">
          <Clock className="w-3 h-3 mr-1" />
          {course.durationHours}h
        </div>
        <div className="flex items-center text-xs text-gray-400">
          <Star className="w-3 h-3 mr-1 text-yellow-500" />
          {course.rating}
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 mb-6 mt-auto relative z-10">
        {course.tags.map((tag) => (
          <span key={tag} className="text-[10px] bg-navy-light text-gray-300 px-2 py-1 rounded-md">
            {tag}
          </span>
        ))}
      </div>
      
      <a 
        href={course.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="mt-auto flex items-center justify-center w-full gap-2 py-2.5 rounded-lg bg-navy-lighter hover:bg-primary-gold/20 text-sm font-medium transition-colors text-white border border-transparent hover:border-primary-gold/30 relative z-10"
      >
        View Course <ExternalLink className="w-4 h-4" />
      </a>

      {/* Animated progress bar indicator at the bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-navy-lighter">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: 'easeOut', delay: 0.2 }}
          className="h-full bg-primary-gold"
        />
      </div>
    </div>
  );
}
