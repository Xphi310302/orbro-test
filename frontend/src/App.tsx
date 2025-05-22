import { useState, useEffect } from 'react'
import axios from 'axios'
import { config } from './config'

interface JobStatus {
  job_id: string
  status: 'processing' | 'done' | 'error'
  count: number
}

function App() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [jobs, setJobs] = useState<JobStatus[]>([])
  const [visibleResults, setVisibleResults] = useState<Set<string>>(new Set())

  useEffect(() => {
    const ws = new WebSocket(`${config.WS_HOST}/ws`)

    ws.onmessage = (event) => {
      const status: JobStatus = JSON.parse(event.data)
      setJobs(prev => {
        const existing = prev.findIndex(job => job.job_id === status.job_id)
        if (existing >= 0) {
          const newJobs = [...prev]
          newJobs[existing] = status
          return newJobs
        }
        return [...prev, status]
      })
    }

    return () => {
      ws.close()
    }
  }, [])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedImage(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedImage) return

    const formData = new FormData()
    formData.append('file', selectedImage)  // Changed from 'image' to 'file'

    try {
      const { data } = await axios.post(`${config.API_HOST}/images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      console.log('Upload successful:', data)
      setSelectedImage(null)
    } catch (error) {
      console.error('Error uploading image:', error)
    }
}

  const toggleResult = (jobId: string) => {
    setVisibleResults(prev => {
      const newSet = new Set(prev)
      if (newSet.has(jobId)) {
        newSet.delete(jobId)
      } else {
        newSet.add(jobId)
      }
      return newSet
    })
  }

  const getStatusColor = (status: JobStatus['status']) => {
    switch (status) {
      case 'processing': return 'bg-status-processing'
      case 'done': return 'bg-status-done'
      case 'error': return 'bg-status-error'
      default: return 'bg-gray-200'
    }
  }

  return (
    <div className="fixed inset-0 flex flex-col bg-white overflow-hidden">
      <header className="flex-none text-center py-8 px-4">

        <h1 className="text-4xl font-bold text-gray-900 mb-8 tracking-tight">Object Detection App</h1>
        <div className="flex items-center justify-center gap-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="btn btn-primary cursor-pointer"
          >
            Select Image
          </label>
          <button 
            onClick={handleUpload}
            disabled={!selectedImage}
            className="btn btn-primary"
          >
            Upload
          </button>
        </div>
        {selectedImage && (
          <div className="mt-4 text-sm text-gray-600">
            Selected: {selectedImage.name}
          </div>
        )}
      </header>

      <div className="flex-1 flex overflow-hidden">
        <main className="flex-1 overflow-auto p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {Array.from(visibleResults).map(jobId => (
              <div 
                key={`result-${jobId}`}
                className="rounded-xl overflow-hidden shadow-xl bg-white transition-all hover:shadow-2xl hover:-translate-y-1"
              >
                <img 
                  src={`${config.API_HOST}/images/${jobId}/result.jpg`}
                  alt={`Result for job ${jobId}`}
                  className="w-full h-auto"
                />
              </div>
            ))}
          </div>
        </main>

        <aside className="w-80 flex-none overflow-y-auto border-l border-gray-200 bg-gray-50 p-4">
          <div className="space-y-2">
            {jobs.map(job => (
              <button
                key={job.job_id}
                onClick={() => toggleResult(job.job_id)}
                className={`
                  w-full px-4 py-2 rounded text-sm font-medium transition-all flex justify-between items-center
                  ${getStatusColor(job.status)}
                  ${visibleResults.has(job.job_id) ? 'ring-2 ring-indigo-600' : ''}
                  hover:-translate-y-0.5 hover:shadow-md
                `}
              >
                <span>Job: {job.job_id}</span>
                <span className="flex items-center gap-2">
                  <span>{job.status}</span>
                  <span className="bg-white bg-opacity-30 px-2 py-0.5 rounded">{job.count}</span>
                </span>
              </button>
            ))}
          </div>
        </aside>
      </div>
    </div>
  )
}

export default App
