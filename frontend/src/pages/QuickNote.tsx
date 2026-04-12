import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useApp } from '@/contexts/appContextInternal'

const QuickNote: React.FC = () => {
  const {
    quickNote,
    setQuickNote,
    handleAddQuickNote,
    addingNote
  } = useApp()

  return (
    <div className="max-w-3xl">
      <div className="mb-10">
        <h2 className="text-3xl font-semibold text-slate-900 mb-2">Quick Note</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Quick Note</CardTitle>
          <CardDescription>Write your thoughts directly</CardDescription>
        </CardHeader>
        <CardContent className="p-8">
          <Textarea
            value={quickNote}
            onChange={(e) => setQuickNote(e.target.value)}
            placeholder="Write your thoughts here..."
            className="min-h-[200px]"
          />
          <Button onClick={handleAddQuickNote} disabled={addingNote || !quickNote.trim()} className="mt-6 w-full" size="lg">
            {addingNote ? 'Adding...' : 'Add Note to Brain'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default QuickNote
