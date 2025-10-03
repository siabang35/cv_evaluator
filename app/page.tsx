import { UploadForm } from "@/components/upload-form"
import { ThemeToggle } from "@/components/theme-toggle"
import { FileText, Sparkles, Zap, Brain, BarChart3 } from "lucide-react"

export default function Home() {
  return (
    <main className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-bg opacity-50" />

      <div className="fixed top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-glow" />
      <div
        className="fixed bottom-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-glow"
        style={{ animationDelay: "2s" }}
      />

      <div className="relative z-10">
        <header className="border-b border-border/50 glass sticky top-0 z-50">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Sparkles className="h-7 w-7 text-primary animate-pulse" />
                  <div className="absolute inset-0 bg-primary/20 blur-xl" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    CV Evaluator
                  </h1>
                  <p className="text-xs text-muted-foreground">AI-Powered Screening</p>
                </div>
              </div>
              <ThemeToggle />
            </div>
          </div>
        </header>

        <section className="container mx-auto px-4 py-20 md:py-28">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-primary/20 mb-4">
              <Zap className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">Powered by Groq AI</span>
            </div>

            <h2 className="text-5xl md:text-7xl font-bold text-balance leading-tight">
              Automate Your{" "}
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
                Candidate Screening
              </span>
            </h2>

            <p className="text-lg md:text-xl text-muted-foreground text-pretty max-w-2xl mx-auto leading-relaxed">
              Upload candidate CVs and project reports to receive AI-powered evaluations with detailed scoring and
              actionable feedback in seconds.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-6 pt-4">
              <div className="flex items-center gap-2 text-sm">
                <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                <span className="text-muted-foreground">Fast Processing</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                <span className="text-muted-foreground">AI-Powered</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="h-2 w-2 rounded-full bg-accent animate-pulse" />
                <span className="text-muted-foreground">Detailed Reports</span>
              </div>
            </div>
          </div>
        </section>

        <section className="container mx-auto px-4 pb-20">
          <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-6 mb-16">
            <div className="group glass rounded-2xl p-8 space-y-4 hover:border-primary/50 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-primary/20">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FileText className="h-7 w-7 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Document Analysis</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Advanced PDF parsing extracts structured data from CVs and project reports with high accuracy.
              </p>
            </div>

            <div className="group glass rounded-2xl p-8 space-y-4 hover:border-accent/50 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-accent/20">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Brain className="h-7 w-7 text-accent" />
              </div>
              <h3 className="text-xl font-semibold">AI Evaluation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                LLM-powered evaluation with RAG context retrieval for accurate, contextual scoring.
              </p>
            </div>

            <div className="group glass rounded-2xl p-8 space-y-4 hover:border-success/50 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-success/20">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-success/20 to-success/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                <BarChart3 className="h-7 w-7 text-success" />
              </div>
              <h3 className="text-xl font-semibold">Detailed Feedback</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Comprehensive evaluation reports with scores, insights, and actionable recommendations.
              </p>
            </div>
          </div>

          <div className="max-w-2xl mx-auto">
            <UploadForm />
          </div>
        </section>

        <footer className="border-t border-border/50 glass mt-20">
          <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-sm text-muted-foreground">Built with Next.js, FastAPI, and Groq AI</p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>© 2025 CV Evaluator</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </main>
  )
}
