import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useApp } from '@/contexts/appContextInternal'
import ReactFlow, { MarkerType } from "reactflow";

const baseNodeStyle = {
  width: 160,
  height: 60,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  borderRadius: 10,
  fontWeight: 500,
  border: "2px solid #007bff",
  background: "#e6f0ff"
};

const nodes = [
  { id: "retrieve", position: { x: 100, y: 200 }, data: { label: "📥 Retrieve" }, sourcePosition: "right", style: { ...baseNodeStyle } },

  { id: "generate_draft", position: { x: 300, y: 200 }, data: { label: "📝 Draft" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },

  { id: "critique", position: { x: 500, y: 200 }, data: { label: "🔍 Critique" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },

  // branching
  { id: "rewrite", position: { x: 500, y: 350 }, data: { label: "🔄 Rewrite" }, targetPosition: "top", sourcePosition: "top", style: { ...baseNodeStyle } },

  { id: "finalize", position: { x: 750, y: 200 }, data: { label: "✅ Finalize" }, targetPosition: "left", style: { ...baseNodeStyle } }
];

const edgeProps = {
        type: "smoothstep",
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: "#007bff", strokeWidth: 2 }
}

const edges = [
  { id: "e1", source: "retrieve", target: "generate_draft", ...edgeProps },

  { id: "e2", source: "generate_draft", target: "critique", ...edgeProps },

  // decision
  {
    id: "e3",
    source: "critique",
    target: "rewrite",
    label: "needs improvement",
    ...edgeProps
  },
  {
    id: "e4",
    source: "critique",
    target: "finalize",
    label: "good",
    ...edgeProps
  },

  // loop back
  {
    id: "e5",
    source: "rewrite",
    target: "critique",
    ...edgeProps,
    style: { stroke: "#f97316" } // loop highlight
  }
];
const Weekly: React.FC = () => {
  const {
    weeklyReport,
    loading,
    handleGenerateWeekly
  } = useApp()

  return (
    <div className="max-w-4xl">
      <div className="mb-10">
        <h2 className="text-3xl font-semibold text-slate-900 mb-2">Weekly Deep Analysis</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Weekly Deep Analysis</CardTitle>
          <CardDescription>Long-term patterns and recommendations</CardDescription>
        </CardHeader>
        <CardContent className="p-12">
          <Button
            onClick={handleGenerateWeekly}
            disabled={loading}
            size="lg"
            className="w-full mb-12 bg-purple-600 hover:bg-purple-700 text-white"
          >
            {loading ? 'Analyzing week...' : 'Generate Weekly Report'}
          </Button>

          {
            !weeklyReport && (
              <div style={{ height: 450 }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
              />
            </div>
            )
          }

          {weeklyReport && (
            <div className="prose prose-slate max-w-none bg-white rounded-2xl p-12 border border-slate-200 shadow-sm leading-relaxed">
              <ReactMarkdown>{weeklyReport}</ReactMarkdown>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Weekly
