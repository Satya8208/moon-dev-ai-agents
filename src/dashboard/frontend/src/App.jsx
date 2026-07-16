import { useState, useRef, useCallback } from 'react'

// Dynamic API Base
const getApiBase = (overrideMode = null) => {
    const mode = overrideMode || import.meta.env.VITE_APP_MODE || 'all'
    // Poker API is on 8001, Nuts is on 8000
    if (mode === 'poker') return 'http://localhost:8001'
    return 'http://localhost:8000'
}

// Mode config
const MODES = {
  savage: { label: 'Savage', icon: '🔥' },
  funny: { label: 'Funny', icon: '😂' },
  philosophical: { label: 'Philosophical', icon: '🧘' },
  controversial: { label: 'Controversial', icon: '⚡' },
  nuclear: { label: 'Nuclear', icon: '☢️' }
}

// Copy hook
function useCopy() {
  const [copied, setCopied] = useState(null)
  const copy = async (text, id) => {
    await navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }
  return { copied, copy }
}

// Savagery Slider
function SavagerySlider({ value, onChange }) {
  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-[var(--text-secondary)]">Savagery Level</span>
        <span className="text-lg font-bold text-[var(--accent)]">{value}</span>
      </div>
      <input
        type="range"
        min="1"
        max="10"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
      />
      <div className="flex justify-between text-xs text-[var(--text-muted)] mt-1">
        <span>Gentle</span>
        <span>Spicy</span>
        <span>Nuclear</span>
      </div>
    </div>
  )
}

// Reply Card
function ReplyCard({ mode, reply }) {
  const { copied, copy } = useCopy()
  const config = MODES[mode] || MODES.savage
  const id = `reply-${mode}`

  return (
    <div className={`card reply-${mode} p-4 fade-in`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span>{config.icon}</span>
          <span className={`badge badge-${mode}`}>{config.label}</span>
        </div>
        <span className="text-xs text-[var(--text-muted)]">{reply.length} chars</span>
      </div>
      <p className="text-[var(--text-primary)] mb-3 leading-relaxed">{reply}</p>
      <div className="flex justify-between items-center">
        <span className="text-xs text-[var(--text-muted)]">
          {reply.length <= 280 ? '✓ Twitter ready' : '⚠ Over limit'}
        </span>
        <button
          onClick={() => copy(reply, id)}
          className={`copy-btn ${copied === id ? 'copied' : ''}`}
        >
          {copied === id ? '✓ Copied' : 'Copy'}
        </button>
      </div>
    </div>
  )
}

// Tweet Card
function TweetCard({ tweet, index }) {
  const { copied, copy } = useCopy()
  const id = `tweet-${index}`

  return (
    <div className="card p-4 fade-in">
      <p className="text-[var(--text-primary)] mb-3 leading-relaxed">{tweet.text}</p>
      <div className="flex justify-between items-center">
        <span className="text-xs text-[var(--text-muted)]">
          {tweet.char_count} chars {tweet.char_count <= 280 && '✓'}
        </span>
        <button
          onClick={() => copy(tweet.text, id)}
          className={`copy-btn ${copied === id ? 'copied' : ''}`}
        >
          {copied === id ? '✓ Copied' : 'Copy'}
        </button>
      </div>
    </div>
  )
}

// Thread Card
function ThreadCard({ tweet, index, total }) {
  const { copied, copy } = useCopy()
  const id = `thread-${index}`

  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className="w-8 h-8 rounded-full bg-[var(--accent)] text-white flex items-center justify-center text-sm font-bold">
          {index + 1}
        </div>
        {index < total - 1 && <div className="w-0.5 flex-1 bg-[var(--border)] my-1" />}
      </div>
      <div className="card p-4 flex-1 mb-3 fade-in">
        <p className="text-[var(--text-primary)] mb-3 leading-relaxed">{tweet.text}</p>
        <div className="flex justify-between items-center">
          <span className="text-xs text-[var(--text-muted)]">{tweet.char_count} chars</span>
          <button
            onClick={() => copy(tweet.text, id)}
            className={`copy-btn ${copied === id ? 'copied' : ''}`}
          >
            {copied === id ? '✓ Copied' : 'Copy'}
          </button>
        </div>
      </div>
    </div>
  )
}

// Analysis Box
function AnalysisBox({ analysis }) {
  if (!analysis) return null

  return (
    <div className="card p-4 mb-6 fade-in">
      <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-3">Analysis</h3>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-[var(--text-muted)]">Tone:</span>
          <p className="text-[var(--text-primary)]">{analysis.tone}</p>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Best Mode:</span>
          <p><span className={`badge badge-${analysis.recommended_mode}`}>{analysis.recommended_mode}</span></p>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Angle:</span>
          <p className="text-[var(--text-primary)]">{analysis.angle}</p>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Engagement:</span>
          <p className="text-[var(--text-primary)] capitalize">{analysis.engagement_potential}</p>
        </div>
      </div>
    </div>
  )
}

// Image Analysis Box
function ImageAnalysisBox({ imageAnalysis }) {
  if (!imageAnalysis) return null

  return (
    <div className="card p-4 mb-4 fade-in border-[var(--accent)]/30">
      <h3 className="text-sm font-semibold text-[var(--accent)] mb-3 flex items-center gap-2">
        <span>Image Analysis</span>
        <span className="text-xs px-2 py-0.5 rounded bg-[var(--accent)]/20 capitalize">{imageAnalysis.image_type}</span>
      </h3>
      <div className="space-y-3 text-sm">
        {imageAnalysis.visible_text && (
          <div className="bg-[var(--bg-secondary)] p-3 rounded-lg border-l-2 border-[var(--accent)]">
            <span className="text-[var(--text-muted)] text-xs uppercase tracking-wide">Tweet Text</span>
            <p className="text-[var(--text-primary)] mt-1">{imageAnalysis.visible_text}</p>
          </div>
        )}
        <div>
          <span className="text-[var(--text-muted)]">What it's about:</span>
          <p className="text-[var(--text-primary)] mt-1">{imageAnalysis.actual_message}</p>
        </div>
        <div className="flex gap-4">
          <div>
            <span className="text-[var(--text-muted)]">Tone:</span>
            <span className="ml-2 text-[var(--text-primary)] capitalize">{imageAnalysis.tone}</span>
          </div>
        </div>
        <div>
          <span className="text-[var(--text-muted)]">Hook:</span>
          <p className="text-[var(--accent)] mt-1">{imageAnalysis.hook}</p>
        </div>
      </div>
    </div>
  )
}

// Loading
function Loading() {
  return (
    <div className="flex items-center gap-2 py-8 justify-center">
      <span className="loading-dot" style={{ animationDelay: '0ms' }} />
      <span className="loading-dot" style={{ animationDelay: '150ms' }} />
      <span className="loading-dot" style={{ animationDelay: '300ms' }} />
    </div>
  )
}

// Reply Generator with Image Support
function ReplyGenerator() {
  const [tweet, setTweet] = useState('')
  const [savagery, setSavagery] = useState(7)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Image state
  const [imageData, setImageData] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)

  // Handle paste event for images
  const handlePaste = useCallback((e) => {
    const items = e.clipboardData?.items
    if (!items) return

    for (const item of items) {
      if (item.type.startsWith('image/')) {
        e.preventDefault()
        const file = item.getAsFile()
        if (file) {
          processImageFile(file)
        }
        return
      }
    }
  }, [])

  // Process image file to base64
  const processImageFile = (file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const dataUrl = e.target.result
      setImageData(dataUrl)
      setImagePreview(dataUrl)
    }
    reader.readAsDataURL(file)
  }

  // Handle file input change
  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      processImageFile(file)
    }
  }

  // Clear image
  const clearImage = () => {
    setImageData(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const generate = async () => {
    // Need either text or image
    if (!tweet.trim() && !imageData) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      let res
      if (imageData) {
        // Use image endpoint
        res = await fetch(`${getApiBase('nuts')}/api/image-replies`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_data: imageData,
            caption: tweet.trim()
          })
        })
      } else {
        // Use text endpoint
        res = await fetch(`${getApiBase('nuts')}/api/replies`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tweet: tweet.trim() })
        })
      }

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to generate replies')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const canGenerate = tweet.trim() || imageData

  return (
    <div>
      <div className="card p-6 mb-6">
        <h2 className="text-lg font-semibold mb-1">Reply Generator</h2>
        <p className="text-sm text-[var(--text-muted)] mb-4">
          Paste a tweet or screenshot (Ctrl+V) to generate savage replies
        </p>

        {/* Image Preview */}
        {imagePreview && (
          <div className="mb-4 relative">
            <div className="relative inline-block">
              <img
                src={imagePreview}
                alt="Tweet screenshot"
                className="max-h-48 rounded-lg border border-[var(--border)] object-contain"
              />
              <button
                onClick={clearImage}
                className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full text-sm hover:bg-red-600 flex items-center justify-center"
                title="Remove image"
              >
                x
              </button>
            </div>
            <p className="text-xs text-[var(--text-muted)] mt-2">
              Screenshot attached - add caption below (optional)
            </p>
          </div>
        )}

        {/* Text Input Area */}
        <div className="relative mb-4">
          <textarea
            ref={textareaRef}
            value={tweet}
            onChange={(e) => setTweet(e.target.value)}
            onPaste={handlePaste}
            placeholder={imageData ? "Add caption (optional)..." : "Paste tweet text or screenshot (Ctrl+V)..."}
            className="input pr-12"
            rows={4}
          />

          {/* Upload button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="absolute right-3 bottom-3 p-2 text-[var(--text-muted)] hover:text-[var(--accent)] transition-colors"
            title="Upload image"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>

        <SavagerySlider value={savagery} onChange={setSavagery} />

        <button
          onClick={generate}
          disabled={!canGenerate || loading}
          className="btn w-full"
        >
          {loading ? 'Generating...' : imageData ? 'Generate Image Replies' : 'Generate Replies'}
        </button>
      </div>

      {error && (
        <div className="card p-4 mb-6 border-red-500/50 bg-red-500/10 text-red-400">
          {error}
        </div>
      )}

      {loading && <Loading />}

      {result && !loading && (
        <>
          {result.image_analysis && <ImageAnalysisBox imageAnalysis={result.image_analysis} />}
          <AnalysisBox analysis={result.analysis} />
          <div className="space-y-3">
            {result.replies?.map((r, i) => (
              <ReplyCard key={i} mode={r.mode} reply={r.reply} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// Tweet Generator
function TweetGenerator() {
  const [topic, setTopic] = useState('')
  const [count, setCount] = useState(5)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const generate = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${getApiBase('nuts')}/api/tweets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim() || null, count })
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to generate tweets')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card p-6 mb-6">
        <h2 className="text-lg font-semibold mb-1">Tweet Generator</h2>
        <p className="text-sm text-[var(--text-muted)] mb-4">Generate original tweets on any topic</p>

        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Topic (optional)"
          className="input mb-4"
        />

        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-[var(--text-secondary)]">Number of tweets</span>
            <span className="text-lg font-bold text-[var(--accent)]">{count}</span>
          </div>
          <input
            type="range"
            min="1"
            max="10"
            value={count}
            onChange={(e) => setCount(parseInt(e.target.value))}
          />
        </div>

        <button onClick={generate} disabled={loading} className="btn w-full">
          {loading ? 'Generating...' : 'Generate Tweets'}
        </button>
      </div>

      {error && (
        <div className="card p-4 mb-6 border-red-500/50 bg-red-500/10 text-red-400">
          {error}
        </div>
      )}

      {loading && <Loading />}

      {result && !loading && (
        <div className="space-y-3">
          {result.tweets?.map((t, i) => (
            <TweetCard key={i} tweet={t} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}

// Thread Builder
function ThreadBuilder() {
  const [topic, setTopic] = useState('')
  const [thesis, setThesis] = useState('')
  const [length, setLength] = useState(5)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const { copied, copy } = useCopy()

  const generate = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${getApiBase('nuts')}/api/thread`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim(), thesis: thesis.trim() || null, length })
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to generate thread')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const copyAll = () => {
    if (!result?.tweets) return
    const text = result.tweets.map((t, i) => `${i + 1}/ ${t.text}`).join('\n\n')
    copy(text, 'all')
  }

  return (
    <div>
      <div className="card p-6 mb-6">
        <h2 className="text-lg font-semibold mb-1">Thread Builder</h2>
        <p className="text-sm text-[var(--text-muted)] mb-4">Build engaging Twitter threads</p>

        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Thread topic"
          className="input mb-3"
        />

        <input
          type="text"
          value={thesis}
          onChange={(e) => setThesis(e.target.value)}
          placeholder="Core thesis (optional)"
          className="input mb-4"
        />

        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-[var(--text-secondary)]">Thread length</span>
            <span className="text-lg font-bold text-[var(--accent)]">{length}</span>
          </div>
          <input
            type="range"
            min="3"
            max="12"
            value={length}
            onChange={(e) => setLength(parseInt(e.target.value))}
          />
        </div>

        <button onClick={generate} disabled={!topic.trim() || loading} className="btn w-full">
          {loading ? 'Generating...' : 'Generate Thread'}
        </button>
      </div>

      {error && (
        <div className="card p-4 mb-6 border-red-500/50 bg-red-500/10 text-red-400">
          {error}
        </div>
      )}

      {loading && <Loading />}

      {result && !loading && (
        <>
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm text-[var(--text-muted)]">Topic: {result.topic}</span>
            <button
              onClick={copyAll}
              className={`copy-btn ${copied === 'all' ? 'copied' : ''}`}
            >
              {copied === 'all' ? '✓ Copied All' : 'Copy All'}
            </button>
          </div>
          <div>
            {result.tweets?.map((t, i) => (
              <ThreadCard key={i} tweet={t} index={i} total={result.tweets.length} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// Dashboard imports
import PokerGod from './components/PokerGod'
import ScalpingDashboard from './components/ScalpingDashboard'
import BlackjackDashboard from './components/BlackjackDashboard'

// Main App
export default function App() {
  const mode = import.meta.env.VITE_APP_MODE || 'all' // 'poker', 'nuts', 'scalping', 'blackjack', 'all'
  const [tab, setTab] = useState(
    mode === 'poker' ? 'poker' :
    mode === 'scalping' ? 'scalping' :
    mode === 'blackjack' ? 'blackjack' :
    'replies'
  )

  const showPoker = mode === 'all' || mode === 'poker'
  const showNuts = mode === 'all' || mode === 'nuts'
  const showScalping = mode === 'all' || mode === 'scalping'
  const showBlackjack = mode === 'all' || mode === 'blackjack'

  // Dynamic Title
  const getTitle = () => {
    if (mode === 'poker') return 'Poker God'
    if (mode === 'nuts') return 'Nirvana Nuts'
    if (mode === 'scalping') return 'Scalping Agent'
    if (mode === 'blackjack') return 'Blackjack'
    return 'Moon Dev Agents'
  }

  const getSubtitle = () => {
    if (mode === 'poker') return 'AI Poker Advisor'
    if (mode === 'nuts') return 'Twitter Growth Engine'
    if (mode === 'scalping') return 'AI Strategy Generation'
    if (mode === 'blackjack') return 'Twitter Gambling Wisdom'
    return 'AI Trading & Social Suite'
  }

  const getIcon = () => {
    if (mode === 'poker') return '🎰'
    if (mode === 'nuts') return '🥜'
    if (mode === 'scalping') return '🎯'
    if (mode === 'blackjack') return '🃏'
    return '🌙'
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getIcon()}</span>
            <div>
              <h1 className="font-bold text-lg">{getTitle()}</h1>
              <p className="text-xs text-[var(--text-muted)]">{getSubtitle()}</p>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <nav className="border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        <div className="max-w-3xl mx-auto px-4">
          <div className="flex gap-1 py-2 overflow-x-auto">
            {showPoker && (
                <button
                onClick={() => setTab('poker')}
                className={`tab-btn ${tab === 'poker' ? 'active' : ''}`}
                >
                🎰 Poker God
                </button>
            )}
            
            {showNuts && (
                <>
                <button
                onClick={() => setTab('replies')}
                className={`tab-btn ${tab === 'replies' ? 'active' : ''}`}
                >
                🔥 Replies
                </button>
                <button
                onClick={() => setTab('tweets')}
                className={`tab-btn ${tab === 'tweets' ? 'active' : ''}`}
                >
                ✨ Tweets
                </button>
                <button
                onClick={() => setTab('threads')}
                className={`tab-btn ${tab === 'threads' ? 'active' : ''}`}
                >
                🧵 Threads
                </button>
                </>
            )}
            {showScalping && (
                <button
                onClick={() => setTab('scalping')}
                className={`tab-btn ${tab === 'scalping' ? 'active' : ''}`}
                >
                🎯 Scalping
                </button>
            )}
            {showBlackjack && (
                <button
                onClick={() => setTab('blackjack')}
                className={`tab-btn ${tab === 'blackjack' ? 'active' : ''}`}
                >
                🃏 Blackjack
                </button>
            )}
          </div>
        </div>
      </nav>

      {/* Content */}
      {tab === 'scalping' && showScalping ? (
        <ScalpingDashboard />
      ) : tab === 'blackjack' && showBlackjack ? (
        <BlackjackDashboard />
      ) : (
        <main className="max-w-3xl mx-auto px-4 py-6">
          {tab === 'poker' && showPoker && <PokerGod />}
          {tab === 'replies' && showNuts && <ReplyGenerator />}
          {tab === 'tweets' && showNuts && <TweetGenerator />}
          {tab === 'threads' && showNuts && <ThreadBuilder />}
        </main>
      )}
    </div>
  )
}
