import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useApp } from '@/contexts/appContextInternal'
import ReactFlow, { MarkerType } from "reactflow"
import "reactflow/dist/style.css"

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

const allNodes = [
  { id: "retrieve", position: { x: 100, y: 200 }, data: { label: "📥 Retrieve" }, sourcePosition: "right", style: { ...baseNodeStyle } },
  { id: "draft", position: { x: 300, y: 200 }, data: { label: "📝 Draft" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },
  { id: "critique", position: { x: 500, y: 200 }, data: { label: "🔍 Critique" }, targetPosition: "left", sourcePosition: "right", style: { ...baseNodeStyle } },
  { id: "final", position: { x: 700, y: 200 }, data: { label: "✅ Final" }, targetPosition: "left", style: { ...baseNodeStyle }  }
];


const edgeProps = {
        type: "smoothstep",
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: "#007bff", strokeWidth: 2 }
}


const allEdges = [
  { id: "e1", source: "retrieve", target: "draft", ...edgeProps },
  { id: "e2", source: "draft", target: "critique", ...edgeProps },
  { id: "e3", source: "critique", target: "final", ...edgeProps }
];


const Daily: React.FC = () => {
  //const [visibleSteps] = useState<string[]>(["retrieve", "draft", "critique", "final"]);
  const [nodes] = useState(allNodes);
  const [edges] = useState(allEdges);

  const { dailyReport, loading, handleGenerateDaily } = useApp();

  return (
    <div className="max-w-5xl space-y-8">
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Daily Proactive Summary</CardTitle>
          <CardDescription className="text-base mt-1">
            Patterns, risks, and actionable steps from your recent notes
          </CardDescription>
        </CardHeader>

        <CardContent className="p-8">
          <div className="flex justify-center mb-12">
            <Button
              onClick={handleGenerateDaily}
              disabled={loading}
              size="lg"
              className="px-12 py-7 text-lg font-medium bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-xl rounded-2xl"
            >
              {loading ? "Analyzing..." : "✨ Generate Daily Report"}
            </Button>
          </div>

          {!dailyReport && (
            <div style={{ height: 350 }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
              />
            </div>
          )}

          {dailyReport && (
            <ReactMarkdown>{dailyReport}</ReactMarkdown>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Daily;