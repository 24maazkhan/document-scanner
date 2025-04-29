"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

export default function DocumentScanner() {
  const [file, setFile] = useState<File | null>(null); //Uploaded File Store
  const [loading, setLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState<string>(""); // Downloadable URL
  const [downloadName, setDownloadName] = useState<string>(""); // Download File Name
  const [resultType, setResultType] = useState<"scan" | "text" | "">(""); // Result Type
  const [resultText, setResultText] = useState<string>(""); // Recognized OCR Text

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]; // Select First File

    if (f) {
      // Save File
      setFile(f);
      
      // Clear previous result
      setResultUrl("");
      setDownloadName("");
      setResultType("");
      setResultText("");
    }
  };

  const uploadAndScan = async (type: "scan" | "text") => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file, file.name);

    const endpoint = type === "scan" ? "/api/scan" : "/api/ocr";

    const res = await fetch(endpoint, { method: "POST", body: formData }); //Send Request to nextjs API

    if (!res.ok) { //Failure 
      console.error("Upload failed", res.status, await res.text());
      setLoading(false);
      return;
    }

    // Success
    let url: string;
    if (type === "text") { // Text Response
      const text = await res.text();
      setResultText(text);
      const blob = new Blob([text], { type: "text/plain" });
      url = URL.createObjectURL(blob);
    } else { //Scan Result
      const blob = await res.blob();
      url = URL.createObjectURL(blob);
    }

    // Download File Name Build
    const base = file.name.replace(/\.[^.]+$/, "");
    const ext = type === "scan" ? "_scanned.jpg" : "_recognized.txt";

    setResultUrl(url);
    setDownloadName(`${base}${ext}`);
    setResultType(type);
    setLoading(false);
  };

  // UI
  // Card Title
  // Upload Document Button w/ Input for Image
  // Scan or Extract Text Buttons
  // Progress Loading Bar
  // Scanned Document or Text View
  // Download Button

  return (
    <div className="w-full min-h-screen p-4 bg-gray-50 flex justify-center items-start">
      <Card className="w-full max-w-4xl space-y-4">
        <CardHeader>
          <CardTitle>Document Scanner</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="fileUpload">Upload Document (PNG/JPG Only)</Label>
            <Input
              id="fileUpload"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => uploadAndScan("scan")}
              disabled={!file || loading}
              className="bg-blue-500 hover:bg-blue-800"
            >
              {loading ? "Scanning..." : "Scan Document"}
            </Button>
            <Button
              onClick={() => uploadAndScan("text")}
              disabled={!file || loading}
              className="bg-green-500 hover:bg-green-800"
            >
              {loading ? "Extracting..." : "Extract Text"}
            </Button>
          </div>

          {loading && <Progress />}

          {resultType && (
            <div className="mt-4 border rounded p-4 bg-white w-full overflow-auto max-h-[400px]">
              {resultType === "scan" ? (
                <img
                  src={resultUrl}
                  alt="Scanned document"
                  className="w-full object-contain"
                />
              ) : (
                <pre className="whitespace-pre-wrap">{resultText}</pre>
              )}
            </div>
          )}

          {resultUrl && (
            <Button asChild>
              <a href={resultUrl} download={downloadName}>
                Download Result
              </a>
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
