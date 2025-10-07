import { NextResponse } from "next/server"

const BACKEND_EVALUATE_URL =
  process.env.NEXT_PUBLIC_API_URL + "/evaluate" ||
  "https://legacy-journal-neon-membership.trycloudflare.com/api/evaluate"

export async function POST(req: Request) {
  try {
    const body = await req.json() // { job_title, cv_document_id, project_document_id }

    const backendRes = await fetch(BACKEND_EVALUATE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    const data = await backendRes.json()
    return NextResponse.json(data, { status: backendRes.status })
  } catch (err) {
    return NextResponse.json(
      { error: "Failed to proxy evaluate", details: (err as Error).message },
      { status: 500 }
    )
  }
}
