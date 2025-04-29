import { NextResponse } from "next/server";

export const POST = async (req: Request) => {
  const formData = await req.formData();
  if (!formData.has("file")) { // Get Data Check
    return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
  }

  // Send Request
  const flaskRes = await fetch(
    `${process.env.FLASK_API_URL}/ocr`,
    {
      method: "POST",
      body: formData,
    }
  );

  // Failure
  if (!flaskRes.ok) {
    const text = await flaskRes.text();
    return NextResponse.json(
      { error: "Flask OCR failed", details: text },
      { status: flaskRes.status }
    );
  }

  // Success
  const blob = await flaskRes.blob();
  const headers = new Headers();
  headers.set("Content-Type", flaskRes.headers.get("Content-Type")!);
  if (flaskRes.headers.has("Content-Disposition")) {
    headers.set("Content-Disposition", flaskRes.headers.get("Content-Disposition")!);
  }

  // Return blob
  return new Response(blob, { status: 200, headers });
};
