"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle2, XCircle, ArrowLeft, FileText, Award, Sparkles, TrendingUp } from "lucide-react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface EvaluationResult {
  cv_match_rate: number
  cv_feedback: string
  project_score: number
  project_feedback: string
  overall_summary: string
}

interface EvaluationJob {
  id: string
  status: "queued" | "processing" | "completed" | "failed"
  result?: EvaluationResult
  error_message?: string
  created_at: string
  completed_at?: string
}

export function ResultsView({ jobId }: { jobId: string }) {
  const router = useRouter()
  const [job, setJob] = useState<EvaluationJob | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/result/${jobId}`)

        if (!response.ok) {
          throw new Error("Failed to fetch results")
        }

        const data = await response.json()
        setJob(data)
        setIsLoading(false)

        if (data.status === "queued" || data.status === "processing") {
          setProgress(data.status === "queued" ? 30 : 70)
          setTimeout(fetchResults, 3000)
        } else if (data.status === "completed") {
          setProgress(100)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred")
        setIsLoading(false)
      }
    }

    fetchResults()
  }, [jobId])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "queued":
        return (
          <Badge variant="secondary" className="glass">
            Queued
          </Badge>
        )
      case "processing":
        return (
          <Badge variant="secondary" className="bg-info/20 text-info border-info/30 backdrop-blur-sm">
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
            Processing
          </Badge>
        )
      case "completed":
        return (
          <Badge variant="secondary" className="bg-success/20 text-success border-success/30 backdrop-blur-sm">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Completed
          </Badge>
        )
      case "failed":
        return (
          <Badge variant="destructive" className="backdrop-blur-sm">
            Failed
          </Badge>
        )
      default:
        return (
          <Badge variant="secondary" className="glass">
            {status}
          </Badge>
        )
    }
  }

  const getMatchRateColor = (rate: number) => {
    if (rate >= 0.8) return "text-success"
    if (rate >= 0.6) return "text-warning"
    return "text-destructive"
  }

  const getProjectScoreColor = (score: number) => {
    if (score >= 4.0) return "text-success"
    if (score >= 3.0) return "text-warning"
    return "text-destructive"
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto flex flex-col items-center justify-center space-y-6">
          <div className="relative">
            <Loader2 className="h-16 w-16 animate-spin text-primary" />
            <div className="absolute inset-0 bg-primary/20 blur-2xl animate-pulse" />
          </div>
          <div className="text-center space-y-2">
            <p className="text-lg font-medium">Loading evaluation results</p>
            <p className="text-sm text-muted-foreground">Please wait while we fetch your data...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <Card className="glass border-destructive/30">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-destructive/20 flex items-center justify-center">
                  <XCircle className="h-5 w-5 text-destructive" />
                </div>
                <CardTitle>Error Loading Results</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">{error || "Job not found"}</p>
              <Button onClick={() => router.push("/")} variant="outline" className="glass">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-bg opacity-30" />
      <div className="fixed top-20 right-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-glow" />

      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <Button
              onClick={() => router.push("/")}
              variant="ghost"
              size="sm"
              className="glass hover:scale-105 transition-transform"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            {getStatusBadge(job.status)}
          </div>

          {(job.status === "queued" || job.status === "processing") && (
            <Card className="glass border-primary/30 shadow-2xl shadow-primary/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="relative">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    <div className="absolute inset-0 bg-primary/20 blur-xl" />
                  </div>
                  Evaluation in Progress
                </CardTitle>
                <CardDescription className="text-base">
                  Your documents are being analyzed by our AI. This may take a few minutes.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Progress value={progress} className="h-3" />
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {job.status === "queued" ? "Waiting in queue..." : "Running AI evaluation pipeline..."}
                  </span>
                  <span className="font-medium text-primary">{progress}%</span>
                </div>
              </CardContent>
            </Card>
          )}

          {job.status === "failed" && (
            <Card className="glass border-destructive/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-destructive">
                  <XCircle className="h-6 w-6" />
                  Evaluation Failed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{job.error_message || "An error occurred during evaluation"}</p>
              </CardContent>
            </Card>
          )}

          {job.status === "completed" && job.result && (
            <>
              {/* Overall Summary */}
              <Card className="glass border-primary/30 shadow-2xl shadow-primary/10 overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl" />
                <CardHeader className="relative">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-success/20 to-success/5 flex items-center justify-center">
                      <CheckCircle2 className="h-6 w-6 text-success" />
                    </div>
                    <div>
                      <CardTitle className="text-2xl">Overall Assessment</CardTitle>
                      <CardDescription>AI-generated evaluation summary</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="relative">
                  <p className="text-foreground leading-relaxed text-lg">{job.result.overall_summary}</p>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-2 gap-6">
                {/* CV Evaluation */}
                <Card className="glass border-border/50 hover:border-primary/50 transition-all hover:shadow-xl hover:shadow-primary/10 group">
                  <CardHeader>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                          <FileText className="h-5 w-5 text-primary" />
                        </div>
                        <CardTitle>CV Evaluation</CardTitle>
                      </div>
                    </div>
                    <div className="flex items-end justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Match Rate</p>
                        <p className={`text-4xl font-bold ${getMatchRateColor(job.result.cv_match_rate)}`}>
                          {(job.result.cv_match_rate * 100).toFixed(0)}%
                        </p>
                      </div>
                      <TrendingUp className={`h-8 w-8 ${getMatchRateColor(job.result.cv_match_rate)}`} />
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Progress value={job.result.cv_match_rate * 100} className="h-2" />
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-primary" />
                        Feedback
                      </h4>
                      <p className="text-muted-foreground leading-relaxed">{job.result.cv_feedback}</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Project Evaluation */}
                <Card className="glass border-border/50 hover:border-accent/50 transition-all hover:shadow-xl hover:shadow-accent/10 group">
                  <CardHeader>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                          <Award className="h-5 w-5 text-accent" />
                        </div>
                        <CardTitle>Project Report</CardTitle>
                      </div>
                    </div>
                    <div className="flex items-end justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Score</p>
                        <p className={`text-4xl font-bold ${getProjectScoreColor(job.result.project_score)}`}>
                          {job.result.project_score.toFixed(2)}
                          <span className="text-2xl text-muted-foreground">/5.00</span>
                        </p>
                      </div>
                      <Award className={`h-8 w-8 ${getProjectScoreColor(job.result.project_score)}`} />
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Progress value={(job.result.project_score / 5) * 100} className="h-2" />
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-accent" />
                        Feedback
                      </h4>
                      <p className="text-muted-foreground leading-relaxed">{job.result.project_feedback}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="glass border-border/50">
                <CardContent className="pt-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Job ID</p>
                      <p className="font-mono text-xs bg-secondary/50 px-3 py-2 rounded-lg">{job.id}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Created At</p>
                      <p className="font-medium">{new Date(job.created_at).toLocaleString()}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Completed At</p>
                      <p className="font-medium">
                        {job.completed_at ? new Date(job.completed_at).toLocaleString() : "N/A"}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
