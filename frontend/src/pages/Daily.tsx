import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useApp } from '@/contexts/appContextInternal'

const Daily: React.FC = () => {
  const {
    dailyReport,
    loading,
    handleGenerateDaily
  } = useApp()

  return (
    <div className="max-w-4xl">
      <div className="mb-10">
        <h2 className="text-3xl font-semibold text-slate-900 mb-2">Daily Proactive Summary</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Daily Proactive Summary</CardTitle>
          <CardDescription>Patterns, risks, and actionable steps from your recent notes</CardDescription>
        </CardHeader>
        <CardContent className="p-12 flex flex-col items-center">
          <Button
            onClick={handleGenerateDaily}
            disabled={loading}
            size="lg"
            className="px-10 py-7 text-lg font-medium bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg rounded-2xl mb-16"
          >
            {loading ? 'Analyzing your notes...' : '✨ Generate Daily Report'}
          </Button>

          {dailyReport && (
            <div className="prose prose-slate max-w-none bg-white rounded-2xl p-12 pb-24 border border-slate-200 shadow-sm leading-relaxed w-full">
              <ReactMarkdown>{dailyReport}</ReactMarkdown>
            </div>
          )}

          {!dailyReport && !loading && (
            <div className="text-center py-20 text-slate-500">
              Click the button above to generate your daily insights
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Daily
