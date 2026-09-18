'use client';

import { GraphData, GraphNode } from '@/types';
import { cn } from '@/lib/utils';
import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';

interface InteractiveGraphProps {
  data: GraphData;
}

interface Layout {
  positions: Record<string, { x: number; y: number }>;
  width: number;
  height: number;
}

const COL_GAP = 230;
const ROW_GAP = 92;
const PAD_X = 100;
const PAD_Y = 70;

/**
 * Layered DAG layout: a node's column is its longest distance from a root
 * (topological depth), rows are spaced within the column. No dependency on
 * a physics engine — deterministic and instant for prerequisite chains.
 */
function computeLayout(data: GraphData): Layout {
  const ids = data.nodes.map((n) => n.id);
  const known = new Set(ids);
  const depth: Record<string, number> = {};
  ids.forEach((id) => (depth[id] = 0));

  // longest-path relaxation (graph is a DAG, so V passes suffice)
  for (let pass = 0; pass < ids.length; pass += 1) {
    for (const link of data.links) {
      if (known.has(link.source) && known.has(link.target)) {
        depth[link.target] = Math.max(depth[link.target], depth[link.source] + 1);
      }
    }
  }

  const columns: Record<number, string[]> = {};
  ids.forEach((id) => {
    const d = depth[id];
    (columns[d] ??= []).push(id);
  });

  const positions: Record<string, { x: number; y: number }> = {};
  let maxDepth = 0;
  let maxRows = 1;
  Object.entries(columns).forEach(([depthKey, column]) => {
    const d = Number(depthKey);
    maxDepth = Math.max(maxDepth, d);
    maxRows = Math.max(maxRows, column.length);
    const x = PAD_X + d * COL_GAP;
    const columnHeight = (column.length - 1) * ROW_GAP;
    column.forEach((id, i) => {
      positions[id] = { x, y: PAD_Y + columnHeight / 2 + i * ROW_GAP };
    });
  });

  return {
    positions,
    width: Math.max(PAD_X * 2 + maxDepth * COL_GAP, 720),
    height: Math.max(PAD_Y * 2 + (maxRows - 1) * ROW_GAP, 260),
  };
}

export function InteractiveGraph({ data }: InteractiveGraphProps) {
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const { positions, width, height } = useMemo(() => computeLayout(data), [data]);

  const getNodeColor = (node: GraphNode) => {
    if (activeNode === node.id) return 'fill-electric stroke-white';
    if (node.completed) return 'fill-mint stroke-mint-light';

    switch (node.difficulty) {
      case 'Beginner': return 'fill-mint/20 stroke-mint';
      case 'Intermediate': return 'fill-electric/20 stroke-electric';
      case 'Advanced': return 'fill-violet/20 stroke-violet';
      default: return 'fill-navy-light stroke-gray-500';
    }
  };

  return (
    <div className="w-full overflow-x-auto glass-panel rounded-2xl p-4">
      <div style={{ width, height }} className="relative">
        <svg className="w-full h-full" viewBox={`0 0 ${width} ${height}`}>
          {/* Edges */}
          {data.links.map((link, i) => {
            const source = positions[link.source];
            const target = positions[link.target];
            if (!source || !target) return null;

            const isHighlighted = activeNode === link.source || activeNode === link.target;

            return (
              <motion.line
                key={`link-${link.source}-${link.target}-${i}`}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke={isHighlighted ? '#D4AF37' : 'rgba(212, 175, 55, 0.15)'}
                strokeWidth={isHighlighted ? 2 : 1.5}
                className="transition-colors duration-300"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, delay: i * 0.15, ease: 'easeOut' }}
              />
            );
          })}

          {/* Nodes */}
          {data.nodes.map((node, i) => {
            const pos = positions[node.id];
            if (!pos) return null;

            return (
              <motion.g
                key={node.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.4, delay: i * 0.1, type: 'spring', stiffness: 200 }}
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer group"
                onClick={() => setActiveNode(node.id === activeNode ? null : node.id)}
              >
                <circle
                  r={24}
                  className={cn('transition-all duration-300 stroke-2', getNodeColor(node))}
                />
                {/* Outer glow on hover/active */}
                <circle
                  r={32}
                  className={cn(
                    'fill-transparent transition-all duration-300 stroke-1',
                    activeNode === node.id ? 'stroke-electric opacity-100' : 'stroke-transparent group-hover:stroke-gray-400 group-hover:opacity-50',
                  )}
                  strokeDasharray="4 4"
                />
                <text
                  y={45}
                  textAnchor="middle"
                  className={cn(
                    'text-[11px] font-medium transition-colors',
                    activeNode === node.id ? 'fill-electric' : 'fill-gray-400 group-hover:fill-white',
                  )}
                >
                  {node.label}
                </text>
              </motion.g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex gap-4 items-center justify-center mt-4 text-xs text-gray-400">
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-mint/20 border border-mint"></div> Beginner</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-electric/20 border border-electric"></div> Intermediate</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-violet/20 border border-violet"></div> Advanced</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-mint border border-mint-light"></div> Completed</div>
      </div>
    </div>
  );
}
