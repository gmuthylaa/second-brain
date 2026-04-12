import React, { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { apiFetch, apiPostJSON } from '@/lib/api'
import AppContext from './appContextInternal'
import type { AppContextType, Page, Message } from './appContextInternal'

export const AppProvider: React.FC<React.PropsWithChildren<object>> = ({ children }) => {
    const [currentPage, setCurrentPage] = useState<Page>('ingest')
    const [docCount, setDocCount] = useState(0)
    const [loading, setLoading] = useState(false)
    const [dailyReport, setDailyReport] = useState('')
    const [weeklyReport, setWeeklyReport] = useState('')
    const [monthlyReport, setMonthlyReport] = useState('')
    const [files, setFiles] = useState<File[]>([])
    const [quickNote, setQuickNote] = useState('')
    const [addingNote, setAddingNote] = useState(false)

    // Chat states
    const [messages, setMessages] = useState<Message[]>([])
    const [inputMessage, setInputMessage] = useState('')
    const [isThinking, setIsThinking] = useState(false)

    // Image Preview
    const [enablePreview, setEnablePreview] = useState(false)
    const [showReview, setShowReview] = useState(false)
    const [reviewText, setReviewText] = useState('')
    const [reviewFilename, setReviewFilename] = useState('')

    useEffect(() => {
        fetchHealth()
    }, [])

    const fetchHealth = async () => {
        try {
            const res = await apiFetch('/health')
            const data = await res.json()
            setDocCount(data.docs_count || 0)
        } catch (err) {
            console.error('Health check failed:', err)
        }
    }

    const handleFiles = (selectedFiles: FileList | null) => {
        if (!selectedFiles) return
        setFiles(Array.from(selectedFiles))
    }

    const handleReviewImage = async (file: File) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const res = await apiFetch('/ingest/review', { method: 'POST', body: formData })

            const data = await res.json()

            if (data.error) {
                toast.error(data.error)
            } else {
                setReviewText(data.extracted_text || '')
                setReviewFilename(data.filename)
                setShowReview(true)
            }
        } catch (err) {
            console.error('Review failed:', err)
            toast.error('Failed to process image')
        } finally {
            setLoading(false)
        }
    }

    const handleSaveReviewedText = async () => {
        if (!reviewText.trim()) {
            toast.error('Text cannot be empty')
            return
        }

        setLoading(true)
        try {
            const formData = new FormData()
            formData.append('file', new Blob([reviewText], { type: 'text/plain' }), `reviewed-${reviewFilename}`)

            await apiFetch('/ingest', { method: 'POST', body: formData })
            toast.success('Saved to Second Brain successfully!')
            setShowReview(false)
            setReviewText('')
            setFiles([])
            fetchHealth()
        } catch (err) {
            console.error('Save failed:', err)
            toast.error('Failed to save')
        } finally {
            setLoading(false)
        }
    }

    const handleUpload = async () => {
        if (files.length === 0) {
            toast.error('Please select at least one file')
            return
        }

        setLoading(true)

        for (const file of files) {
            if (file.type.startsWith('image/') && enablePreview) {
                await handleReviewImage(file)
                break
            } else {
                const formData = new FormData()
                formData.append('file', file)
                await apiFetch('/ingest', { method: 'POST', body: formData })
            }
        }

        setLoading(false)

        if (!files.some(f => f.type.startsWith('image/') && enablePreview)) {
            toast.success(`${files.length} file(s) added successfully!`)
            setFiles([])
            fetchHealth()
        }
    }

    const handleAddQuickNote = async () => {
        if (!quickNote.trim()) {
            toast.error('Please write something')
            return
        }

        setAddingNote(true)
        try {
            const formData = new FormData()
            formData.append('file', new Blob([quickNote], { type: 'text/plain' }), `quick-note-${Date.now()}.md`)
            await apiFetch('/ingest', { method: 'POST', body: formData })
            toast.success('Quick note added!')
            setQuickNote('')
            fetchHealth()
        } catch (err) {
            console.error('Failed to add quick note:', err)
            toast.error('Failed to add note')
        } finally {
            setAddingNote(false)
        }
    }

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || isThinking) return

        const userMsg = inputMessage.trim()
        setMessages(prev => [...prev, { role: 'user', content: userMsg }])
        setInputMessage('')
        setIsThinking(true)

        try {
            const res = await apiPostJSON('/chat', { question: userMsg })

            const data = await res.json()

            if (data.error) {
                toast.error(data.error)
            } else {
                setMessages(prev => [...prev, { role: 'assistant', content: data.answer || data.report || "Sorry, I couldn't generate a response." }])
            }
        } catch (err) {
            console.error('Chat error:', err)
            toast.error('Failed to get response')
        } finally {
            setIsThinking(false)
        }
    }

    const handleGenerateDaily = async () => {
        setLoading(true)
        setDailyReport('')

        try {
            const res = await apiFetch('/daily-summary', { method: 'POST' })
            const data = await res.json()

            if (data.error) {
                toast.error(data.error)
            } else if (data.report) {
                setDailyReport(data.report)
                toast.success('Daily report generated successfully!')
            }
        } catch (err) {
            console.error('Daily summary error:', err)
            toast.error('Failed to generate report')
        } finally {
            setLoading(false)
            fetchHealth()
        }
    }

    const handleGenerateMonthly = async () => {
        setLoading(true)
        setWeeklyReport('')

        try {
            const res = await apiFetch('/monthly-summary', { method: 'POST' })
            const data = await res.json()

            if (data.error) {
                toast.error(data.error)
            } else if (data.report) {
                setMonthlyReport(data.report)
                toast.success('Monthly report generated successfully!')
            }
        } catch (err) {
            console.error('Monthly summary error:', err)
            toast.error('Failed to generate Monthly report')
        } finally {
            setLoading(false)
            fetchHealth()
        }
    }

    const handleGenerateWeekly = async () => {
        setLoading(true)
        setWeeklyReport('')

        try {
            const res = await apiFetch('/weekly-summary', { method: 'POST' })
            const data = await res.json()

            if (data.error) {
                toast.error(data.error)
            } else if (data.report) {
                setWeeklyReport(data.report)
                toast.success('Weekly report generated successfully!')
            }
        } catch (err) {
            console.error('Weekly summary error:', err)
            toast.error('Failed to generate weekly report')
        } finally {
            setLoading(false)
            fetchHealth()
        }
    }

    const value: AppContextType = {
        currentPage,
        setCurrentPage,
        docCount,
        files,
        setFiles,
        enablePreview,
        setEnablePreview,
        showReview,
        setShowReview,
        reviewText,
        setReviewText,
        reviewFilename,
        setReviewFilename,
        loading,
        quickNote,
        setQuickNote,
        addingNote,
        messages,
        inputMessage,
        setInputMessage,
        isThinking,
        dailyReport,
        weeklyReport,
        monthlyReport,
        fetchHealth,
        handleFiles,
        handleReviewImage,
        handleSaveReviewedText,
        handleUpload,
        handleAddQuickNote,
        handleSendMessage,
        handleGenerateDaily,
        handleGenerateWeekly,
        handleGenerateMonthly,
    }

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export default AppContext
