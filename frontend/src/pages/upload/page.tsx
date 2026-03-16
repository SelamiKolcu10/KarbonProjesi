import { motion } from "framer-motion";
import { Upload, FileText, Table, File, Shield, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { cn } from "@/lib/utils";

export default function UploadPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [jsonPreview, setJsonPreview] = useState<object | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [fileDeleted, setFileDeleted] = useState(false);
  const [extractionInfo, setExtractionInfo] = useState<{
    confidence?: number;
    columnLanguage?: string;
    extractionMode?: string;
  }>({});

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setUploadedFile(file);
    setIsProcessing(true);
    setUploadStatus("uploading");
    setErrorMessage("");
    setJsonPreview(null);
    setFileDeleted(false);
    setExtractionInfo({});

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: "Bilinmeyen hata" }));
        throw new Error(err.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setUploadStatus("success");
      setFileDeleted(data.file_deleted || false);

      // Çıkarılan veriyi JSON önizleme olarak göster
      if (data.structured_data) {
        setJsonPreview(data.structured_data);
      } else if (data.extraction) {
        setJsonPreview(data.extraction);
      } else {
        setJsonPreview(data);
      }

      // Ek bilgiler
      setExtractionInfo({
        confidence: data.extraction?.confidence,
        columnLanguage: data.extraction?.column_language,
        extractionMode: data.extraction_mode,
      });
    } catch (err: any) {
      setUploadStatus("error");
      setErrorMessage(err.message || "Dosya yükleme hatası");
      setJsonPreview(null);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold text-foreground">Belgeleme Paneli</h2>
        <p className="text-sm text-muted-foreground mt-1">
          PDF veya Excel fabrika belgesini yükleyin — Ajan 1 otomatik olarak veri çıkarımını başlatır
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="lg:col-span-2"
        >
          <Card className="glass-card border-border">
            <CardContent className="p-6">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={cn(
                  "border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 cursor-pointer",
                  isDragging
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-accent/30"
                )}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf,.xlsx,.xls,.csv"
                  onChange={handleFileInput}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent flex items-center justify-center">
                    <Upload className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    Dosyayı sürükleyip bırakın
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    veya <span className="text-primary underline">bilgisayardan seçin</span>
                  </p>
                  <div className="flex items-center justify-center gap-2">
                    <Badge variant="outline" className="text-xs">.PDF</Badge>
                    <Badge variant="outline" className="text-xs">.XLSX</Badge>
                    <Badge variant="outline" className="text-xs">.XLS</Badge>
                    <Badge variant="outline" className="text-xs">.CSV</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-4">Maks. dosya boyutu: 50 MB</p>
                </label>
              </div>

              {uploadedFile && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "mt-4 p-4 rounded-lg border",
                    uploadStatus === "success" && "bg-green-500/5 border-green-500/20",
                    uploadStatus === "uploading" && "bg-primary/5 border-primary/20",
                    uploadStatus === "error" && "bg-red-500/5 border-red-500/20",
                    uploadStatus === "idle" && "bg-primary/5 border-primary/20"
                  )}
                >
                  <div className="flex items-center gap-3">
                    {isProcessing ? (
                      <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    ) : uploadStatus === "success" ? (
                      <CheckCircle className="w-8 h-8 text-green-500" />
                    ) : uploadStatus === "error" ? (
                      <AlertCircle className="w-8 h-8 text-red-500" />
                    ) : (
                      <FileText className="w-8 h-8 text-primary" />
                    )}
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{uploadedFile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                        {isProcessing && " — İşleniyor..."}
                        {uploadStatus === "success" && " — ✅ Başarıyla işlendi"}
                        {uploadStatus === "error" && ` — ❌ ${errorMessage}`}
                      </p>
                    </div>
                    {fileDeleted && (
                      <Badge variant="outline" className="text-xs text-green-500 border-green-500/30">
                        <Shield className="w-3 h-3 mr-1" /> Dosya silindi
                      </Badge>
                    )}
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* JSON Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Table className="w-4 h-4" />
                JSON Önizleme
              </CardTitle>
            </CardHeader>
            <CardContent>
              {jsonPreview ? (
                <pre className="text-xs text-foreground/80 bg-background/50 p-3 rounded-lg overflow-auto max-h-64">
                  {JSON.stringify(jsonPreview, null, 2)}
                </pre>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <File className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Belge yüklendikten sonra</p>
                  <p className="text-sm">etiketlendi veri burada görünüyor</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Info Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div className="flex items-start gap-3 p-4 rounded-lg bg-card border border-border">
          <FileText className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">
              PDF belgelerinde metin güvenilirliği çıkarımını arttırır
            </p>
            {extractionInfo.confidence !== undefined && (
              <p className="text-xs text-primary mt-1 font-medium">
                Güvenilirlik: %{Math.round(extractionInfo.confidence * 100)}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-start gap-3 p-4 rounded-lg bg-card border border-border">
          <Table className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">
              Excel dosyalarının sütun başlıkları Türkçe veya İngilizce olabilir
            </p>
            {extractionInfo.columnLanguage && extractionInfo.columnLanguage !== "unknown" && (
              <p className="text-xs text-green-500 mt-1 font-medium">
                Tespit edilen dil: {extractionInfo.columnLanguage}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-start gap-3 p-4 rounded-lg bg-card border border-border">
          <Shield className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">
              Belgeler işlendikten sonra güvenli bir şekilde silinir, saklanmaz
            </p>
            {fileDeleted && (
              <p className="text-xs text-orange-500 mt-1 font-medium">
                ✅ Dosya güvenli şekilde silindi
              </p>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
