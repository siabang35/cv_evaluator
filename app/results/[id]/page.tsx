import { ResultsView } from "@/components/results-view"

export default function ResultsPage({ params }: { params: { id: string } }) {
  return (
    <main className="min-h-screen bg-background">
      <ResultsView jobId={params.id} />
    </main>
  )
}
