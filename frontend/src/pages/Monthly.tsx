import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useApp } from '@/contexts/appContextInternal'

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

          {monthlyReport && (
            <div className="prose prose-slate max-w-none bg-white rounded-2xl p-12 border border-slate-200 shadow-sm leading-relaxed">
              <ReactMarkdown>{monthlyReport}</ReactMarkdown>
            </div>
          )}

          {!monthlyReport && !loading && (
            <div className="text-center py-20 text-slate-500">
              Click the button to generate your Monthly deep analysis
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Monthly
