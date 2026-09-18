import { RoadmapStage } from '@/types';
import { CourseCard } from './CourseCard';
import { cn } from '@/lib/utils';
import { CheckCircle2, Circle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface RoadmapTimelineProps {
  stages: RoadmapStage[];
  onToggleComplete: (stageId: string) => void;
}

export function RoadmapTimeline({ stages, onToggleComplete }: RoadmapTimelineProps) {
  return (
    <div className="relative border-l border-navy-lighter ml-6 space-y-12 pb-12">
      {stages.map((stage, index) => (
        <motion.div 
          key={stage.id} 
          className="relative pl-8 sm:pl-12"
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.4, delay: index * 0.1, ease: 'easeOut' }}
        >
          {/* Timeline Node */}
          <button
            onClick={() => onToggleComplete(stage.id)}
            className="absolute -left-[17px] top-1 bg-background rounded-full p-0.5 hover:scale-110 transition-transform focus:outline-none"
          >
            {stage.completed ? (
              <CheckCircle2 className="w-8 h-8 text-mint" />
            ) : (
              <Circle className="w-8 h-8 text-navy-lighter hover:text-electric transition-colors" />
            )}
          </button>

          <div className={cn(
            "transition-all duration-300",
            stage.completed ? "opacity-60 grayscale-[30%]" : "opacity-100"
          )}>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
              <span className="text-electric font-mono text-sm font-semibold tracking-wider uppercase">
                Week {stage.weekStart}{stage.weekStart !== stage.weekEnd ? `-${stage.weekEnd}` : ''}
              </span>
              <span className="hidden sm:inline text-gray-500">•</span>
              <span className="text-sm text-gray-400">{stage.estimatedHours}h total</span>
              <span className="hidden sm:inline text-gray-500">•</span>
              <span className={cn(
                "text-xs px-2 py-0.5 rounded-full border w-fit",
                stage.difficulty === 'Beginner' ? 'bg-mint/10 text-mint border-mint/20' :
                stage.difficulty === 'Intermediate' ? 'bg-electric/10 text-electric border-electric/20' :
                'bg-violet/10 text-violet border-violet/20'
              )}>
                {stage.difficulty}
              </span>
            </div>

            <h3 className="text-2xl font-bold text-white mb-3">{stage.title}</h3>
            
            <p className="text-gray-300 mb-6 leading-relaxed">
              {stage.description}
            </p>
            
            <div className="bg-navy p-4 rounded-lg border border-navy-lighter mb-8 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-electric shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-white mb-1">Why this comes next</h4>
                <p className="text-sm text-gray-400 leading-relaxed">{stage.whyNext}</p>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Recommended Free Courses</h4>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {stage.recommendedCourses.map((course, idx) => (
                  <CourseCard key={course.id} course={course} isBestMatch={idx === 0} />
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
