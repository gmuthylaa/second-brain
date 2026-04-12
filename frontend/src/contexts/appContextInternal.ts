import { createContext, useContext } from 'react'

export type Page = 'ingest' | 'quicknote' | 'chat' | 'daily' | 'weekly' | 'monthly'

export type Message = { role: 'user' | 'assistant'; content: string }

export type AppContextType = {
  currentPage: Page
  setCurrentPage: (p: Page) => void
  docCount: number
  files: File[]
  setFiles: (f: File[]) => void
  enablePreview: boolean
  setEnablePreview: (v: boolean) => void
  showReview: boolean
  setShowReview: (v: boolean) => void
  reviewText: string
  setReviewText: (s: string) => void
  reviewFilename: string
  setReviewFilename: (s: string) => void
  loading: boolean
  quickNote: string
  setQuickNote: (s: string) => void
  addingNote: boolean
  messages: Message[]
  inputMessage: string
  setInputMessage: (s: string) => void
  isThinking: boolean
  dailyReport: string
  weeklyReport: string
  monthlyReport: string
  fetchHealth: () => Promise<void>
  handleFiles: (files: FileList | null) => void
  handleReviewImage: (file: File) => Promise<void>
  handleSaveReviewedText: () => Promise<void>
  handleUpload: () => Promise<void>
  handleAddQuickNote: () => Promise<void>
  handleSendMessage: () => Promise<void>
  handleGenerateDaily: () => Promise<void>
  handleGenerateWeekly: () => Promise<void>
  handleGenerateMonthly: () => Promise<void>
}

export const AppContext = createContext<AppContextType | undefined>(undefined)

export const useApp = (): AppContextType => {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}

export default AppContext
