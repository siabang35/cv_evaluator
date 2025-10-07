"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, FileText, Loader2, Sparkles } from "lucide-react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "ttps://legacy-journal-neon-membership.trycloudflare.com/api"

export function UploadForm() {
  const router = useRouter()
  const [jobTitle, setJobTitle] = useState("")
  const [cvFile, setCvFile] = useState<File | null>(null)
  const [projectFile, setProjectFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Helper untuk convert file ke Base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        // hasilnya: "data:application/pdf;base64,xxxxxx"
        const base64 = (reader.result as string).split(",")[1] // ambil bagian setelah koma
        resolve(base64)
      }
      reader.onerror = (err) => reject(err)
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!jobTitle || !cvFile || !projectFile) {
      setError("Please fill in all fields and upload both documents")
      return
    }

    setIsUploading(true)

    try {
      // Convert file ke base64
      const cvBase64 = await fileToBase64(cvFile)
      const projectBase64 = await fileToBase64(projectFile)

      // Kirim ke backend
      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cv_base64: cvBase64,
          project_base64: projectBase64,
        }),
      })

      if (!uploadResponse.ok) {
        throw new Error("Failed to upload documents")
      }

      const uploadData = await uploadResponse.json()
      const cvDocumentId = uploadData.cv_document.id
      const projectDocumentId = uploadData.project_document.id

      // Trigger evaluation
      const evaluateResponse = await fetch(`${API_BASE_URL}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: jobTitle,
          cv_document_id: cvDocumentId,
          project_document_id: projectDocumentId,
        }),
      })

      if (!evaluateResponse.ok) {
        throw new Error("Failed to start evaluation")
      }

      const evaluateData = await evaluateResponse.json()
      const jobId = evaluateData.id

      router.push(`/results/${jobId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
      setIsUploading(false)
    }
  }

  return (
    <Card className="glass border-border/50 shadow-2xl">
      <CardHeader className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <CardTitle className="text-2xl">Upload Documents</CardTitle>
        </div>
        <CardDescription className="text-base">
          Upload candidate CV and project report to start the AI evaluation process
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Job Title */}
          <div className="space-y-3">
            <Label htmlFor="jobTitle" className="text-sm font-medium">Job Title</Label>
            <Input
              id="jobTitle"
              placeholder="e.g., Product Engineer (Backend)"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              disabled={isUploading}
              className="h-12 bg-secondary/50 border-border/50 focus:border-primary transition-colors"
            />
          </div>

          {/* CV */}
          <div className="space-y-3">
            <Label htmlFor="cv" className="text-sm font-medium">Candidate CV (PDF)</Label>
            <div className="relative group">
              <Input
                id="cv"
                type="file"
                accept=".pdf"
                onChange={(e) => setCvFile(e.target.files?.[0] || null)}
                disabled={isUploading}
                className="h-12 cursor-pointer bg-secondary/50 border-border/50 hover:border-primary/50 transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
              />
              {cvFile && (
                <div className="mt-3 flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 border border-primary/20">
                  <FileText className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-primary">{cvFile.name}</span>
                </div>
              )}
            </div>
          </div>

          {/* Project Report */}
          <div className="space-y-3">
            <Label htmlFor="project" className="text-sm font-medium">Project Report (PDF)</Label>
            <div className="relative group">
              <Input
                id="project"
                type="file"
                accept=".pdf"
                onChange={(e) => setProjectFile(e.target.files?.[0] || null)}
                disabled={isUploading}
                className="h-12 cursor-pointer bg-secondary/50 border-border/50 hover:border-accent/50 transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-accent file:text-accent-foreground hover:file:bg-accent/90"
              />
              {projectFile && (
                <div className="mt-3 flex items-center gap-2 px-4 py-2 rounded-lg bg-accent/10 border border-accent/20">
                  <FileText className="h-4 w-4 text-accent" />
                  <span className="text-sm font-medium text-accent">{projectFile.name}</span>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="bg-destructive/10 border border-destructive/30 rounded-xl p-4 backdrop-blur-sm">
              <p className="text-sm font-medium text-destructive">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full h-12 text-base font-medium bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-all hover:scale-[1.02] shadow-lg shadow-primary/25"
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-5 w-5" />
                Start Evaluation
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
