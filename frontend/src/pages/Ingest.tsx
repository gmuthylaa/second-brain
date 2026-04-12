import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, FileText, ImageIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useApp } from '@/contexts/appContextInternal'

const Ingest: React.FC = () => {
  const {
    files,
    enablePreview,
    setEnablePreview,
    showReview,
    setShowReview,
    reviewText,
    setReviewText,
    loading,
    handleFiles,
    handleUpload,
    handleSaveReviewedText
  } = useApp()

  return (
    <div className="max-w-3xl">
      <div className="mb-10">
        <h2 className="text-3xl font-semibold text-slate-900 mb-2">Ingest Files</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Upload Files</CardTitle>
          <CardDescription>Drag & drop or select files</CardDescription>
        </CardHeader>
        <CardContent className="p-16">
          <div
            className="border-2 border-dashed border-slate-300 hover:border-indigo-400 rounded-3xl p-20 text-center cursor-pointer bg-white"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files) }}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <Upload className="mx-auto h-16 w-16 text-slate-400 mb-6" />
            <p className="text-xl font-medium">Drag & drop files here</p>
            <p className="text-slate-500 mt-1">or click to browse</p>
            <input
              id="file-input"
              type="file"
              multiple
              accept=".md,.txt,.pdf,.jpg,.jpeg,.png"
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />
          </div>

          {files.length > 0 && (
            <div className="mt-8">
              <div className="flex items-center gap-2 mb-4">
                <input
                  type="checkbox"
                  id="preview-checkbox"
                  checked={enablePreview}
                  onChange={(e) => setEnablePreview(e.target.checked)}
                  className="w-4 h-4"
                />
                <label htmlFor="preview-checkbox" className="text-sm cursor-pointer select-none">
                  Preview & edit text before saving (for images)
                </label>
              </div>

              <p className="font-medium mb-3">Selected Files ({files.length})</p>
              <ul className="space-y-2">
                {files.map((f, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm bg-slate-50 p-3 rounded-xl">
                    {f.type.startsWith('image/') ? <ImageIcon className="h-5 w-5" /> : <FileText className="h-5 w-5" />}
                    {f.name}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {files.length > 0 && (
            <Button onClick={handleUpload} disabled={loading} className="mt-8 w-full" size="lg">
              {loading ? 'Processing...' : `Add ${files.length} File${files.length > 1 ? 's' : ''} to Brain`}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Review Modal */}
      {showReview && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="p-6 border-b flex justify-between items-center">
              <h3 className="text-xl font-semibold">Review Extracted Text</h3>
              <Button variant="ghost" onClick={() => setShowReview(false)}>
                Cancel
              </Button>
            </div>

            <div className="p-6 flex-1 overflow-auto">
              <Textarea
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                className="min-h-[400px] font-mono text-sm"
                placeholder="Extracted text will appear here..."
              />
            </div>

            <div className="p-6 border-t flex gap-3">
              <Button variant="outline" onClick={() => setShowReview(false)} className="flex-1">
                Cancel
              </Button>
              <Button onClick={handleSaveReviewedText} disabled={loading || !reviewText.trim()} className="flex-1">
                {loading ? 'Saving...' : 'Save to Brain'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Ingest
