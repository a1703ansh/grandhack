export type CourseSource = 'MIT OCW' | 'Khan Academy' | 'NPTEL' | 'Coursera Audit' | 'YouTube';
export type Difficulty = 'Beginner' | 'Intermediate' | 'Advanced';

export interface Course {
  id: string;
  title: string;
  source: CourseSource;
  difficulty: Difficulty;
  durationHours: number;
  rating: number;
  url: string;
  tags: string[];
}

export interface RoadmapStage {
  id: string;
  weekStart: number;
  weekEnd: number;
  title: string;
  description: string;
  difficulty: Difficulty;
  estimatedHours: number;
  whyNext: string;
  prerequisites: string[];
  recommendedCourses: Course[];
  completed?: boolean;
}

export interface GraphNode {
  id: string;
  label: string;
  difficulty: Difficulty;
  completed?: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphEdge[];
}

export interface UserPreferences {
  goal: string;
  currentKnowledge: string;
  weeksAvailable: number;
  weeklyHours: number;
}

export interface Roadmap {
  id: string;
  goal: string;
  totalWeeks: number;
  totalHours: number;
  stages: RoadmapStage[];
  graph: GraphData;
}
