"use client";

import { useRef, useEffect } from "react";

interface PaperNode {
  id: string;
  title: string;
  status: string;
  prerequisite_ids: string[];
  order: number;
  arxiv_id: string;
  difficulty_tier: string;
}

interface SkillTreeProps {
  papers: PaperNode[];
  onPaperClick: (paperId: string) => void;
}

const STATUS_COLORS: Record<string, { fill: string; stroke: string; text: string }> = {
  locked: { fill: "#1f2937", stroke: "#4b5563", text: "#6b7280" },
  unlocked: { fill: "#1e3a5f", stroke: "#3b82f6", text: "#93c5fd" },
  in_progress: { fill: "#1e3a5f", stroke: "#f59e0b", text: "#fcd34d" },
  completed: { fill: "#064e3b", stroke: "#10b981", text: "#6ee7b7" },
};

export default function SkillTree({ papers, onPaperClick }: SkillTreeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Layout: arrange nodes in rows by order
  const nodePositions = new Map<string, { x: number; y: number }>();
  const nodeWidth = 220;
  const nodeHeight = 60;
  const gapX = 40;
  const gapY = 80;
  const padding = 40;

  // Arrange in rows of 3
  const cols = 3;
  papers.forEach((paper, i) => {
    const row = Math.floor(i / cols);
    const col = i % cols;
    nodePositions.set(paper.id, {
      x: padding + col * (nodeWidth + gapX),
      y: padding + row * (nodeHeight + gapY),
    });
  });

  const totalWidth = padding * 2 + cols * nodeWidth + (cols - 1) * gapX;
  const totalRows = Math.ceil(papers.length / cols);
  const totalHeight = padding * 2 + totalRows * nodeHeight + (totalRows - 1) * gapY;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = totalWidth * dpr;
    canvas.height = totalHeight * dpr;
    canvas.style.width = `${totalWidth}px`;
    canvas.style.height = `${totalHeight}px`;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, totalWidth, totalHeight);

    // Draw edges
    papers.forEach((paper) => {
      const to = nodePositions.get(paper.id);
      if (!to) return;
      paper.prerequisite_ids.forEach((prereqId) => {
        const from = nodePositions.get(prereqId);
        if (!from) return;
        ctx.beginPath();
        ctx.moveTo(from.x + nodeWidth / 2, from.y + nodeHeight);
        ctx.lineTo(to.x + nodeWidth / 2, to.y);
        ctx.strokeStyle = "#374151";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Arrow head
        const angle = Math.atan2(to.y - (from.y + nodeHeight), to.x + nodeWidth / 2 - (from.x + nodeWidth / 2));
        const arrowSize = 8;
        ctx.beginPath();
        ctx.moveTo(to.x + nodeWidth / 2, to.y);
        ctx.lineTo(
          to.x + nodeWidth / 2 - arrowSize * Math.cos(angle - Math.PI / 6),
          to.y - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(to.x + nodeWidth / 2, to.y);
        ctx.lineTo(
          to.x + nodeWidth / 2 - arrowSize * Math.cos(angle + Math.PI / 6),
          to.y - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        ctx.strokeStyle = "#374151";
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    });

    // Draw nodes
    papers.forEach((paper) => {
      const pos = nodePositions.get(paper.id);
      if (!pos) return;
      const colors = STATUS_COLORS[paper.status] || STATUS_COLORS.locked;

      // Node background
      ctx.fillStyle = colors.fill;
      ctx.strokeStyle = colors.stroke;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(pos.x, pos.y, nodeWidth, nodeHeight, 8);
      ctx.fill();
      ctx.stroke();

      // Title text (truncated)
      ctx.fillStyle = colors.text;
      ctx.font = "12px Inter, system-ui, sans-serif";
      const title = paper.title.length > 28 ? paper.title.slice(0, 28) + "..." : paper.title;
      ctx.fillText(title, pos.x + 10, pos.y + 24);

      // Status badge
      ctx.font = "10px Inter, system-ui, sans-serif";
      ctx.fillStyle = colors.stroke;
      const statusLabel = paper.status === "in_progress" ? "reading" : paper.status;
      ctx.fillText(statusLabel.toUpperCase(), pos.x + 10, pos.y + 44);

      // Lock icon for locked papers
      if (paper.status === "locked") {
        ctx.fillText("🔒", pos.x + nodeWidth - 30, pos.y + 24);
      }
    });
  }, [papers]);

  function handleCanvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    for (const paper of papers) {
      const pos = nodePositions.get(paper.id);
      if (!pos) continue;
      if (x >= pos.x && x <= pos.x + nodeWidth && y >= pos.y && y <= pos.y + nodeHeight) {
        if (paper.status !== "locked") {
          onPaperClick(paper.id);
        }
        break;
      }
    }
  }

  return (
    <div ref={containerRef} className="overflow-auto">
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        className="cursor-pointer"
      />
      <div className="mt-4 flex gap-6 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-gray-700 border border-gray-500" /> Locked
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-blue-900 border border-blue-500" /> Unlocked
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-blue-900 border border-yellow-500" /> Reading
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-emerald-900 border border-emerald-500" /> Completed
        </span>
      </div>
    </div>
  );
}
