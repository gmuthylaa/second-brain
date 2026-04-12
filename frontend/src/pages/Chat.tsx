import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useApp } from '@/contexts/appContextInternal'

const Chat: React.FC = () => {
  const {
    messages,
    inputMessage,
    setInputMessage,
    handleSendMessage,
    isThinking
  } = useApp()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-10">
        <h2 className="text-3xl font-semibold text-slate-900 mb-2">Chat with Second Brain</h2>
      </div>
      <Card className="h-[calc(100vh-180px)] flex flex-col shadow-sm">
        <CardHeader>
          <CardTitle>Chat with Second Brain</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
          {messages.length === 0 && (
            <div className="text-center text-slate-500 py-12">
              Ask me anything about your notes or life
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-5 rounded-3xl ${
                msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 shadow-sm'
              }`}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          {isThinking && (
            <div className="flex justify-start">
              <div className="bg-white border p-4 rounded-3xl text-slate-500">Thinking...</div>
            </div>
          )}
        </CardContent>
        <div className="p-4 border-t bg-white">
          <div className="flex gap-3">
            <Textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask anything about your notes..."
              className="flex-1 min-h-[60px]"
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
            />
            <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isThinking}>
              Send
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default Chat
