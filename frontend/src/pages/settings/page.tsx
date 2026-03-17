import { motion } from "framer-motion";
import { Bot, Key, Building2, Save, CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { toast } from "sonner";

const STORAGE_KEY = "cbam-settings";

interface Settings {
  modelProvider: string;
  model: string;
  openaiKey: string;
  anthropicKey: string;
  tesisAdi: string;
  cbamNo: string;
  konum: string;
}

const defaultSettings: Settings = {
  modelProvider: "openai",
  model: "gpt-4o",
  openaiKey: "",
  anthropicKey: "",
  tesisAdi: "İzmir Çelik Fabrikası A.Ş.",
  cbamNo: "TR-CBAM-2024-XXXXX",
  konum: "Türkiye / İzmir",
};

function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...defaultSettings, ...JSON.parse(raw) };
  } catch { /* ignore */ }
  return defaultSettings;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>(loadSettings);

  const update = <K extends keyof Settings>(key: K, value: Settings[K]) =>
    setSettings((prev) => ({ ...prev, [key]: value }));

  const handleSave = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    toast.success("Ayarlar başarıyla kaydedildi", {
      icon: <CheckCircle className="w-4 h-4 text-emerald-400" />,
    });
  };

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold text-foreground">Sistem Ayarları</h2>
        <p className="text-sm text-muted-foreground mt-1">
          LLM sağlayıcıları ve API ayarları
        </p>
      </motion.div>

      {/* LLM Provider */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Bot className="w-4 h-4 text-primary" />
              LLM Sağlayıcısı
            </CardTitle>
            <p className="text-xs text-muted-foreground">Ajan sistemi için yapay zeka uzmanı seçin</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">Model Sağlayıcısı</label>
              <select
                value={settings.modelProvider}
                onChange={(e) => update("modelProvider", e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground"
              >
                <option value="openai">OpenAI (GPT-4)</option>
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="azure">Azure OpenAI</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">Model</label>
              <select
                value={settings.model}
                onChange={(e) => update("model", e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground"
              >
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4-turbo">gpt-4-turbo</option>
                <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
              </select>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* API Keys */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Key className="w-4 h-4 text-primary" />
              API Anahtarları
            </CardTitle>
            <p className="text-xs text-muted-foreground">Güvenli şekilde saklanan API kimlik bilgileri</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">OpenAI API Anahtarı</label>
              <input
                type="password"
                value={settings.openaiKey}
                onChange={(e) => update("openaiKey", e.target.value)}
                placeholder="sk-..."
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground font-mono"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">Antropik API Anahtarı</label>
              <input
                type="password"
                value={settings.anthropicKey}
                onChange={(e) => update("anthropicKey", e.target.value)}
                placeholder="sk-ant-..."
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground font-mono"
              />
            </div>
            <Button className="gap-2" onClick={handleSave}>
              <Save className="w-4 h-4" />
              Kaydet
            </Button>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tesis Bilgileri */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Building2 className="w-4 h-4 text-primary" />
              Tesis Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">Tesis Adı</label>
              <input
                type="text"
                value={settings.tesisAdi}
                onChange={(e) => update("tesisAdi", e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">CBAM Kayıt No</label>
              <input
                type="text"
                value={settings.cbamNo}
                onChange={(e) => update("cbamNo", e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-foreground block mb-2">Ülke / Şehir</label>
              <input
                type="text"
                value={settings.konum}
                onChange={(e) => update("konum", e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground"
              />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleSave}>
              <Save className="w-4 h-4" />
              Kaydet
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
