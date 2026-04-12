import React from 'react'

import { Brain, Upload, Edit3, MessageCircle } from 'lucide-react'
import { Toaster } from '@/components/ui/sonner'
import { AppProvider } from '@/contexts/AppContext'
import { useApp } from '@/contexts/appContextInternal'
import Ingest from '@/pages/Ingest'
import QuickNote from '@/pages/QuickNote'
import Chat from '@/pages/Chat'
import Daily from '@/pages/Daily'
import Weekly from '@/pages/Weekly'
import Monthly from '@/pages/Monthly'

const  InnerApp =() => {
  const { currentPage, setCurrentPage, docCount } = useApp()

  return (
    <div className="min-h-screen bg-zinc-50 flex">
      <Toaster position="top-center" richColors closeButton />

      {/* Sidebar */}
      <div className="w-72 bg-white border-r border-slate-200 h-screen p-6 flex flex-col fixed">
        <div className="flex items-center gap-3 mb-12">
          <div className="bg-indigo-100 p-3 rounded-2xl">
            <Brain className="h-8 w-8 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Second Brain</h1>
            <p className="text-xs text-slate-500">Personal AI Companion</p>
          </div>
        </div>

        <nav className="space-y-1 flex-1">
          <button
            onClick={() => setCurrentPage('ingest')}
            className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-left font-medium transition-all ${currentPage === 'ingest' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-slate-100 text-slate-700'}`}
          >
            <Upload className="h-5 w-5" /> Ingest Files
          </button>

          <button
            onClick={() => setCurrentPage('quicknote')}
            className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-left font-medium transition-all ${currentPage === 'quicknote' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-slate-100 text-slate-700'}`}
          >
            <Edit3 className="h-5 w-5" /> Quick Note
          </button>

          <button
            onClick={() => setCurrentPage('chat')}
            className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-left font-medium transition-all ${currentPage === 'chat' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-slate-100 text-slate-700'}`}
          >
            <MessageCircle className="h-5 w-5" /> Chat with Brain
          </button>

          <button
            onClick={() => setCurrentPage('daily')}
            className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-left font-medium transition-all ${currentPage === 'daily' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-slate-100 text-slate-700'}`}
          >
             📊  Daily Summary
          </button>

          <button
            onClick={() => setCurrentPage('weekly')}
            className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-left font-medium transition-all ${currentPage === 'weekly' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-slate-100 text-slate-700'}`}
          >
             📅  Weekly Summary
          </button>
           <button
            onClick={() => setCurrentPage('monthly')}
            className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-left font-medium transition-all ${currentPage === 'monthly' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-slate-100 text-slate-700'}`}
          >
             📅  Monthly Summary
          </button>
        </nav>

        <div className="pt-8 border-t mt-auto">
          <div className="text-xs text-slate-500 mb-1">NOTES IN BRAIN</div>
          <div className="text-4xl font-semibold text-slate-900">{docCount}</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 ml-72 p-8">

  {currentPage === 'ingest' && <Ingest />}
  {currentPage === 'quicknote' && <QuickNote />}
  {currentPage === 'chat' && <Chat />}
  {currentPage === 'daily' && <Daily />}
  {currentPage === 'weekly' && <Weekly />}
  {currentPage === 'monthly' && <Monthly />}
      </div>
    </div>
  )
}

const App = () => {
  return (
    <AppProvider>
      <InnerApp />
    </AppProvider>
  )
}
export default App