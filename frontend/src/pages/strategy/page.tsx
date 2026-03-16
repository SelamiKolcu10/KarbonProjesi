import { motion } from "framer-motion";
import { Sparkles, CheckCircle, Clock, AlertTriangle, TrendingDown, Euro, Zap, Info } from "lucide-react";
import { mockScenarios, mockAiOzet, mockKpiData, mockCbamTimeline } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const formatNumber = (n: number) =>
  new Intl.NumberFormat("tr-TR").format(n);

const formatCurrency = (n: number) =>
  new Intl.NumberFormat("tr-TR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

const zorlukColors = {
  düşük: "bg-green-500/20 text-green-400 border-green-500/30",
  orta: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  yüksek: "bg-red-500/20 text-red-400 border-red-500/30",
};

const oncelikColors = {
  düşük: "bg-muted text-muted-foreground",
  orta: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  yüksek: "bg-primary/20 text-primary border-primary/30",
};

export default function StrategyPage() {
  const [selectedScenarios, setSelectedScenarios] = useState<number[]>([]);

  const toggleScenario = (id: number) => {
    setSelectedScenarios(prev => 
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const selectedTotal = mockScenarios
    .filter(s => selectedScenarios.includes(s.id))
    .reduce((acc, s) => ({
      emisyon: acc.emisyon + s.tasarrufEmisyon,
      mali: acc.mali + s.maliKazanc,
    }), { emisyon: 0, mali: 0 });

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-start justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-foreground">Strateji Raporu</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Ajan 3 çıktısı — planlama stratejileri ve etkileşimli simülasyon
          </p>
        </div>
        <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
          Risk Skoru: {mockKpiData.riskScore} /100
        </Badge>
      </motion.div>

      {/* Risk Gauge & AI Summary Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Gauge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-foreground text-center">CBAM UYUMLULUK RİSKİ</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center">
                {/* Semi-circle gauge */}
                <div className="relative w-48 h-28">
                  <svg viewBox="0 0 200 110" className="w-full h-full">
                    {/* Background arc segments */}
                    <path d="M 20 100 A 80 80 0 0 1 100 20" fill="none" stroke="#22c55e" strokeWidth="16" strokeLinecap="round" opacity="0.3" />
                    <path d="M 100 20 A 80 80 0 0 1 140 35" fill="none" stroke="#eab308" strokeWidth="16" strokeLinecap="round" opacity="0.3" />
                    <path d="M 140 35 A 80 80 0 0 1 180 100" fill="none" stroke="#ef4444" strokeWidth="16" strokeLinecap="round" opacity="0.3" />
                    
                    {/* Active indicator */}
                    <circle 
                      cx={100 + 70 * Math.cos(Math.PI - (mockKpiData.riskScore / 100) * Math.PI)} 
                      cy={100 - 70 * Math.sin(Math.PI - (mockKpiData.riskScore / 100) * Math.PI)} 
                      r="8" 
                      fill="white" 
                      stroke="#ef4444" 
                      strokeWidth="3"
                    />
                    
                    {/* Center text */}
                    <text x="100" y="85" textAnchor="middle" fill="#f1f5f9" fontSize="32" fontWeight="bold">
                      {mockKpiData.riskScore}
                    </text>
                  </svg>
                  <div className="absolute -bottom-2 left-0 right-0 flex justify-between px-2 text-[10px] text-muted-foreground">
                    <span>Düşük</span>
                    <span>Yüksek</span>
                  </div>
                </div>
                
                <Badge className="mt-4 bg-red-500/20 text-red-400 border-red-500/30">YÜKSEK RİSK</Badge>
                
                <div className="mt-4 text-center">
                  <p className="text-2xl font-bold text-foreground">{mockKpiData.riskScore}</p>
                  <p className="text-xs text-muted-foreground">CBAM Uyumluluk Risk Skoru</p>
                </div>

                <div className="flex items-center justify-between w-full mt-4 pt-4 border-t border-border text-xs">
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-muted-foreground">Güvenli</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-yellow-500" />
                    <span className="text-muted-foreground">Dikkat</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    <span className="text-muted-foreground">Kritik</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* AI Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                AI Danışman Özeti
              </CardTitle>
              <p className="text-xs text-muted-foreground">Ajan 3 — yönetici özeti</p>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm prose-invert max-w-none">
                {mockAiOzet.split('\n\n').map((paragraph, i) => {
                  const isTitle = paragraph.startsWith('**');
                  if (isTitle) {
                    const title = paragraph.replace(/\*\*/g, '');
                    return (
                      <div key={i} className="mb-3">
                        <p className={cn(
                          "text-xs font-semibold",
                          title.includes('Kritik') ? "text-red-400" :
                          title.includes('Risk') ? "text-yellow-400" :
                          title.includes('Öneri') ? "text-green-400" :
                          "text-blue-400"
                        )}>{title}</p>
                      </div>
                    );
                  }
                  return <p key={i} className="text-xs text-muted-foreground mb-3 leading-relaxed">{paragraph}</p>;
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Optimization Scenarios */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Optimizasyon Senaryoları
                </CardTitle>
                <p className="text-xs text-muted-foreground">Senaryoları — otomatik animasyon hesaplamaları</p>
              </div>
              {selectedScenarios.length > 0 && (
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">Seçili senaryolar:</p>
                  <p className="text-sm font-semibold text-primary">
                    -{formatNumber(selectedTotal.emisyon)} tCO₂e · +{formatCurrency(selectedTotal.mali)}
                  </p>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    <th className="w-8"></th>
                    <th className="text-left text-muted-foreground font-medium pb-2">Senaryo</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Tasarruf (tCO₂e)</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Mali Kazanç</th>
                    <th className="text-center text-muted-foreground font-medium pb-2">Elbette</th>
                    <th className="text-center text-muted-foreground font-medium pb-2">Zorluk</th>
                    <th className="text-center text-muted-foreground font-medium pb-2">Öncelik</th>
                  </tr>
                </thead>
                <tbody>
                  {mockScenarios.map((scenario) => (
                    <tr 
                      key={scenario.id} 
                      className={cn(
                        "border-b border-border/50 last:border-0 cursor-pointer transition-colors",
                        selectedScenarios.includes(scenario.id) ? "bg-primary/5" : "hover:bg-accent/30"
                      )}
                      onClick={() => toggleScenario(scenario.id)}
                    >
                      <td className="py-3">
                        <div className={cn(
                          "w-4 h-4 rounded border-2 flex items-center justify-center",
                          selectedScenarios.includes(scenario.id) 
                            ? "bg-primary border-primary" 
                            : "border-border"
                        )}>
                          {selectedScenarios.includes(scenario.id) && (
                            <CheckCircle className="w-3 h-3 text-primary-foreground" />
                          )}
                        </div>
                      </td>
                      <td className="py-3">
                        <p className="font-medium text-foreground">{scenario.baslik}</p>
                        <p className="text-[10px] text-muted-foreground">{scenario.aciklama}</p>
                      </td>
                      <td className="py-3 text-right text-green-400 font-medium">- {formatNumber(scenario.tasarrufEmisyon)}</td>
                      <td className="py-3 text-right text-primary font-medium">{formatCurrency(scenario.maliKazanc)}</td>
                      <td className="py-3 text-center">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          {scenario.sure}
                        </div>
                      </td>
                      <td className="py-3 text-center">
                        <Badge className={cn("text-[10px]", zorlukColors[scenario.zorluk])}>
                          {scenario.zorluk.charAt(0).toUpperCase() + scenario.zorluk.slice(1)}
                        </Badge>
                      </td>
                      <td className="py-3 text-center">
                        <Badge className={cn("text-[10px]", oncelikColors[scenario.oncelik])}>
                          {scenario.oncelik.charAt(0).toUpperCase() + scenario.oncelik.slice(1)}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* CBAM Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.25 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <TrendingDown className="w-4 h-4" />
                  CBAM Aşamalı Uygulama Takvimi
                </CardTitle>
                <p className="text-xs text-muted-foreground">2026-2034 · %2,5'ten %100'e doğru uygulama</p>
              </div>
              <Badge className="bg-primary/20 text-primary border-primary/30">Şu an: 2026 · %2,5</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {/* Timeline visualization */}
            <div className="relative pt-8 pb-4">
              {/* Line */}
              <div className="absolute top-12 left-0 right-0 h-0.5 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500" />
              
              {/* Points */}
              <div className="flex justify-between relative">
                {mockCbamTimeline.map((item, i) => (
                  <div key={item.yil} className="flex flex-col items-center">
                    <div className={cn(
                      "w-4 h-4 rounded-full border-2 z-10",
                      item.aktif 
                        ? "bg-green-500 border-green-400" 
                        : item.faz <= 47.5 
                          ? "bg-background border-border" 
                          : "bg-red-500/50 border-red-400/50"
                    )} />
                    <p className="text-xs font-medium text-foreground mt-2">% {item.faz}</p>
                    <p className="text-[10px] text-muted-foreground">{item.yil}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Phase cards */}
            <div className="flex gap-2 mt-4 overflow-x-auto pb-2">
              {mockCbamTimeline.map((item) => (
                <div 
                  key={item.yil}
                  className={cn(
                    "flex-shrink-0 px-4 py-2 rounded-lg border text-center min-w-[80px]",
                    item.aktif 
                      ? "bg-green-500/20 border-green-500/30" 
                      : item.faz <= 47.5 
                        ? "bg-card border-border" 
                        : "bg-red-500/10 border-red-500/20"
                  )}
                >
                  <p className={cn(
                    "text-sm font-bold",
                    item.aktif ? "text-green-400" : item.faz <= 47.5 ? "text-foreground" : "text-red-400"
                  )}>% {item.faz}</p>
                  <p className="text-[10px] text-muted-foreground">{item.yil}</p>
                </div>
              ))}
            </div>

            {/* Warning */}
            <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-yellow-400">Aciliyet: CBAM 2026 başlıyor</p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    Şu anda %2,5 oranında uygulanmaktadır. 2034'e kadar her yıl artacak olan bu oran, harekete geçmemeniz durumunda toplam borcunuzu yaklaşık <span className="text-red-400 font-medium">40 kat</span> arttırabilir.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
