import { Roadmap, Course } from '../types';

export const mockCourses: Record<string, Course[]> = {
  python: [
    {
      id: 'c1',
      title: 'Python for Data Science and Machine Learning',
      source: 'YouTube',
      difficulty: 'Beginner',
      durationHours: 20,
      rating: 4.8,
      url: 'https://youtube.com',
      tags: ['Python', 'Data Science'],
    },
  ],
  linear_algebra: [
    {
      id: 'c2',
      title: 'Linear Algebra',
      source: 'MIT OCW',
      difficulty: 'Intermediate',
      durationHours: 35,
      rating: 4.9,
      url: 'https://ocw.mit.edu',
      tags: ['Math', 'Linear Algebra'],
    }
  ],
  prob_stats: [
    {
      id: 'c3',
      title: 'Statistics and Probability',
      source: 'Khan Academy',
      difficulty: 'Beginner',
      durationHours: 15,
      rating: 4.7,
      url: 'https://khanacademy.org',
      tags: ['Math', 'Statistics'],
    }
  ],
  neural_networks: [
    {
      id: 'c4',
      title: 'Neural Networks and Deep Learning',
      source: 'Coursera Audit',
      difficulty: 'Intermediate',
      durationHours: 24,
      rating: 4.9,
      url: 'https://coursera.org',
      tags: ['Deep Learning', 'Neural Networks'],
    }
  ],
  deep_learning: [
    {
      id: 'c5',
      title: 'Deep Learning Specialization',
      source: 'Coursera Audit',
      difficulty: 'Advanced',
      durationHours: 40,
      rating: 4.9,
      url: 'https://coursera.org',
      tags: ['Deep Learning', 'AI'],
    }
  ]
};

export const deepLearningRoadmap: Roadmap = {
  id: 'r_dl_1',
  goal: 'Master Deep Learning',
  totalWeeks: 12,
  totalHours: 134,
  stages: [
    {
      id: 's1',
      weekStart: 1,
      weekEnd: 2,
      title: 'Python for Data Science',
      description: 'Learn the fundamentals of Python programming, focusing on libraries used in data science like NumPy and Pandas.',
      difficulty: 'Beginner',
      estimatedHours: 20,
      whyNext: 'Python is the lingua franca of machine learning. You need it to build models.',
      prerequisites: [],
      recommendedCourses: mockCourses.python,
    },
    {
      id: 's2',
      weekStart: 3,
      weekEnd: 5,
      title: 'Linear Algebra Foundations',
      description: 'Understand vectors, matrices, and linear transformations.',
      difficulty: 'Intermediate',
      estimatedHours: 35,
      whyNext: 'Deep learning models rely heavily on matrix multiplications.',
      prerequisites: ['s1'],
      recommendedCourses: mockCourses.linear_algebra,
    },
    {
      id: 's3',
      weekStart: 6,
      weekEnd: 7,
      title: 'Probability & Statistics',
      description: 'Master probability distributions, bayes theorem, and statistical significance.',
      difficulty: 'Beginner',
      estimatedHours: 15,
      whyNext: 'Machine learning is fundamentally about probability and predicting uncertain outcomes.',
      prerequisites: ['s1'],
      recommendedCourses: mockCourses.prob_stats,
    },
    {
      id: 's4',
      weekStart: 8,
      weekEnd: 9,
      title: 'Neural Networks',
      description: 'Learn how multi-layer perceptrons work, forward and backward propagation.',
      difficulty: 'Intermediate',
      estimatedHours: 24,
      whyNext: 'This is the core architecture of deep learning models.',
      prerequisites: ['s2', 's3'],
      recommendedCourses: mockCourses.neural_networks,
    },
    {
      id: 's5',
      weekStart: 10,
      weekEnd: 12,
      title: 'Deep Learning Specialization',
      description: 'Dive into CNNs, RNNs, and advanced architectures.',
      difficulty: 'Advanced',
      estimatedHours: 40,
      whyNext: 'The final step to master modern deep learning techniques.',
      prerequisites: ['s4'],
      recommendedCourses: mockCourses.deep_learning,
    }
  ],
  graph: {
    nodes: [
      { id: 's1', label: 'Python Basics', difficulty: 'Beginner' },
      { id: 's2', label: 'Linear Algebra', difficulty: 'Intermediate' },
      { id: 's3', label: 'Probability', difficulty: 'Beginner' },
      { id: 's4', label: 'Neural Networks', difficulty: 'Intermediate' },
      { id: 's5', label: 'Deep Learning', difficulty: 'Advanced' }
    ],
    links: [
      { source: 's1', target: 's2' },
      { source: 's1', target: 's3' },
      { source: 's2', target: 's4' },
      { source: 's3', target: 's4' },
      { source: 's4', target: 's5' }
    ]
  }
};
