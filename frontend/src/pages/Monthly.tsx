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

  { id: "writer", position: { x: 300, y: 200 }, data: { label: "✍️ Writer" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },

  // parallel critics
  { id: "structure", position: { x: 550, y: 100 }, data: { label: "🏗 Structure" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },
  { id: "clarity", position: { x: 550, y: 200 }, data: { label: "🔍 Clarity" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },
  { id: "depth", position: { x: 550, y: 300 }, data: { label: "🧠 Depth" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },

  // merge
  { id: "selector", position: { x: 800, y: 200 }, data: { label: "🎯 Selector" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },

  // outputs
  { id: "rewrite", position: { x: 1050, y: 120 }, data: { label: "🔄 Rewrite" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },
  { id: "finalize", position: { x: 1050, y: 280 }, data: { label: "✅ Finalize" }, targetPosition: "left", style: { ...baseNodeStyle } }
];

const edgeProps = {
        type: "smoothstep",
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: "#007bff", strokeWidth: 2 }
}

const edges = [
  { id: "e1", source: "retrieve", target: "writer", ...edgeProps },

  // parallel split
  { id: "e2", source: "writer", target: "structure", ...edgeProps },
  { id: "e3", source: "writer", target: "clarity", ...edgeProps },
  { id: "e4", source: "writer", target: "depth", ...edgeProps },

  // merge
  { id: "e5", source: "structure", target: "selector", ...edgeProps },
  { id: "e6", source: "clarity", target: "selector", ...edgeProps },
  { id: "e7", source: "depth", target: "selector", ...edgeProps },

  // conditional
  { id: "e8", source: "selector", target: "rewrite", label: "needs rewrite", ...edgeProps },
  { id: "e9", source: "selector", target: "finalize", label: "good", ...edgeProps },

  // loop back
  {
    id: "e10",
    source: "rewrite",
    target: "writer",
    ...edgeProps,
    style: { stroke: "#f97316" }, // orange loop
    markerEnd: { type: MarkerType.ArrowClosed }
  }
];
const Monthly: React.FC = () => {
  const {
    monthlyReport,
    loading,
    handleGenerateMonthly
  } = useApp()

  return (
    <div className="max-w-4xl">
      <div className="mb-10">
        <h2 className="text-3xl font-semibold text-slate-900 mb-2">Monthly Deep Analysis</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Monthly Deep Analysis</CardTitle>
          <CardDescription>Long-term patterns and recommendations</CardDescription>
        </CardHeader>
        <CardContent className="p-12">
          <Button   
            onClick={handleGenerateMonthly}
            disabled={loading}
            size="lg"
            className="w-full mb-12 bg-purple-600 hover:bg-purple-700 text-white"
          >
            {loading ? 'Analyzing Month...' : 'Generate Monthly Report'}
          </Button>

          {!monthlyReport && (<div style={{ height: 500 }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
              />
            </div>
            )}

          {monthlyReport && (
            <div className="prose prose-slate max-w-none bg-white rounded-2xl p-12 border border-slate-200 shadow-sm leading-relaxed">
              <ReactMarkdown>{monthlyReport}</ReactMarkdown>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Monthly
