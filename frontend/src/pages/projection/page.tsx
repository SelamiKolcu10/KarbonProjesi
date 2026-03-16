import { motion } from "framer-motion";
import { Sparkles, AlertTriangle, Clock, CheckCircle, Euro, Target, Sliders, Calendar, TrendingDown, Info } from "lucide-react";
import { mockProjectionData } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart, ReferenceLine } from "recharts";
import { useState } from "react";

const formatNumber = (n: number) =>
  new Intl.NumberFormat("tr-TR").format(n);

const formatCurrency = (n: number) =>
  new Intl.NumberFormat("tr-TR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

export default function ProjectionPage() {
  const [emissionReduction, setEmissionReduction] = useState(5);
  const [productionChange, setProductionChange] = useState(2);
  const [targetReduction, setTargetReduction] = useState(40);
  const [startYear, setStartYear] = useState(2027);

  const { yillikProjeksiyon, toplamlar } = mockProjectionData;

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
          <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Target className="w-6 h-6 text-primary" />
            Emisyon Projeksiyon Aracı
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            2026-2034 CBAM takvimi boyunca emisyon ve vergi yükümlülüğü hesaplaması
          </p>
        </div>
        <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
          <Calendar className="w-3 h-3 mr-1" />
          Baz Yıl: 2025 Q1 Verisi
        </Badge>
      </motion.div>

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-500/15 flex items-center justify-center">
                <Euro className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Toplam Baz Senaryo Vergisi</p>
                <p className="text-lg font-bold text-red-400">{formatCurrency(toplamlar.bazVergiToplam)}</p>
                <p className="text-[10px] text-muted-foreground">2026-2034 kümülatif</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/15 flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Optimize Senaryo Vergisi</p>
                <p className="text-lg font-bold text-purple-400">{formatCurrency(toplamlar.optimizeVergiToplam)}</p>
                <p className="text-[10px] text-muted-foreground">2026-2034 kümülatif</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/15 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Toplam Vergi Tasarrufu</p>
                <p className="text-lg font-bold text-green-400">{formatCurrency(toplamlar.toplamTasarruf)}</p>
                <p className="text-[10px] text-muted-foreground">Kümülatif %{toplamlar.emisyonAzaltmaYuzdesi} emisyon azaltmamı</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/15 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Yatırım Geri Dönüşü</p>
                <p className="text-lg font-bold text-foreground">{toplamlar.basabasYili}</p>
                <p className="text-[10px] text-muted-foreground">Tahmini başabaş yılı</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Parameters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Sliders className="w-4 h-4" />
                Projeksiyon Parametreleri
              </CardTitle>
              <p className="text-xs text-muted-foreground">Karbon Fiyatı: 85 € /tCO₂</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-medium text-foreground">Yıllık Emisyon Azaltma Oranı</label>
                  <span className="text-xs text-primary font-semibold">+ % {emissionReduction}</span>
                </div>
                <p className="text-[10px] text-muted-foreground mb-2">Önlemler uygulandıktan sonra yılda azalacak emisyon yüzdesi</p>
                <input
                  type="range"
                  min="0"
                  max="15"
                  value={emissionReduction}
                  onChange={(e) => setEmissionReduction(Number(e.target.value))}
                  className="w-full h-2 bg-border rounded-full appearance-none cursor-pointer accent-primary"
                />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-medium text-foreground">Üretim Hacmi Değişimi</label>
                  <span className="text-xs text-primary font-semibold">+ % {productionChange}</span>
                </div>
                <p className="text-[10px] text-muted-foreground mb-2">Yıllık üretim artışı veya azalış tahmini</p>
                <input
                  type="range"
                  min="-5"
                  max="10"
                  value={productionChange}
                  onChange={(e) => setProductionChange(Number(e.target.value))}
                  className="w-full h-2 bg-border rounded-full appearance-none cursor-pointer accent-primary"
                />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-medium text-foreground">Nihai Emisyon Hedefi</label>
                  <span className="text-xs text-primary font-semibold">+ % {targetReduction}</span>
                </div>
                <p className="text-[10px] text-muted-foreground mb-2">Baz senaryoya göre hedeflenen azaltma oranı</p>
                <input
                  type="range"
                  min="10"
                  max="60"
                  value={targetReduction}
                  onChange={(e) => setTargetReduction(Number(e.target.value))}
                  className="w-full h-2 bg-border rounded-full appearance-none cursor-pointer accent-primary"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <label className="text-xs font-medium text-foreground mb-2 block">Karbon Fiyat Senaryosu</label>
                <p className="text-[10px] text-muted-foreground mb-2">AB ETS referanslı tahmin karbon fiyatı (€/tCO₂)</p>
                <select className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground">
                  <option>Orta — €85/tCO₂ (baz)</option>
                  <option>Düşük — €65/tCO₂</option>
                  <option>Yüksek — €120/tCO₂</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-foreground mb-2 block">Önlem Başlangıç Yılı</label>
                <p className="text-[10px] text-muted-foreground mb-2">Azaltım önlemlerinin uygulamaya başladığı yıl</p>
                <select 
                  className="w-full h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground"
                  value={startYear}
                  onChange={(e) => setStartYear(Number(e.target.value))}
                >
                  <option value={2027}>2027</option>
                  <option value={2028}>2028</option>
                  <option value={2029}>2029</option>
                </select>
              </div>
            </div>

            {/* Methodology Info */}
            <div className="mt-6 p-3 rounded-lg bg-primary/5 border border-primary/20">
              <div className="flex items-start gap-2">
                <Info className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-primary">Hesaplama Metodolojisi</p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    Emisyon = Yoğunluk × Üretim × (1-azaltma) yılı
                  </p>
                  <p className="text-[10px] text-muted-foreground">
                    CBAM Vergisi = Emisyon × Karbon Fiyatı × Faz Faktörü / 100
                  </p>
                  <p className="text-[10px] text-red-400 mt-1">
                    * Projeksiyon tahminidir, resmi CBAM hesabı değildir.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Projection Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-foreground">Emisyon Projeksiyonu (tCO₂e)</CardTitle>
              </div>
              <Badge variant="outline" className="text-[10px]">CBAM Faz Faktörü ile</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={yillikProjeksiyon}>
                  <defs>
                    <linearGradient id="redGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="yil" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v/1000}k`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#f1f5f9' }}
                    formatter={(value: number, name: string) => [formatNumber(value) + ' tCO₂e', name === 'bazEmisyon' ? 'Baz Senaryo' : 'Optimize']}
                  />
                  <ReferenceLine x={startYear} stroke="#22c55e" strokeDasharray="5 5" label={{ value: 'Önlem Başlangıcı', fill: '#22c55e', fontSize: 10 }} />
                  <Area type="monotone" dataKey="bazEmisyon" stroke="#ef4444" fill="url(#redGradient)" strokeWidth={2} />
                  <Area type="monotone" dataKey="optimizeEmisyon" stroke="#22c55e" fill="url(#greenGradient)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center gap-6 mt-4 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-3 h-0.5 bg-red-400" />
                <span className="text-muted-foreground">Baz Senaryo</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-0.5 bg-green-400" />
                <span className="text-muted-foreground">Senaryoyu Optimize Et</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-0.5 bg-purple-400 opacity-50" style={{ borderTop: '2px dashed' }} />
                <span className="text-muted-foreground">Hedef Emisyon</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Yearly Projection Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.25 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Yıllık Projeksiyon Tablosu
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left text-muted-foreground font-medium pb-2">Yıl</th>
                    <th className="text-center text-muted-foreground font-medium pb-2">CBAM Faz</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Baz Emisyon</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Emisyonu Optimize Et</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Azaltım</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Baz Vergi</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Vergiyi Optimize Et</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Tasarruf</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Kümülatif Tasarruf</th>
                  </tr>
                </thead>
                <tbody>
                  {yillikProjeksiyon.map((row, i) => (
                    <tr key={row.yil} className={cn(
                      "border-b border-border/50 last:border-0",
                      row.yil === toplamlar.basabasYili && "bg-blue-500/5"
                    )}>
                      <td className="py-3 text-foreground font-medium">
                        <div className="flex items-center gap-2">
                          {row.yil}
                          {row.yil === 2027 && <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 text-[9px]">Başlangıç</Badge>}
                          {row.yil === toplamlar.basabasYili && <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-[9px]">Başabaş</Badge>}
                        </div>
                      </td>
                      <td className="py-3 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <div className={cn(
                            "w-12 h-1.5 rounded-full",
                            row.cbamFaz <= 10 ? "bg-green-500" : row.cbamFaz <= 47.5 ? "bg-yellow-500" : "bg-red-500"
                          )} style={{ width: `${row.cbamFaz}%`, maxWidth: '100%', minWidth: '8px' }} />
                          <span className="text-muted-foreground">% {row.cbamFaz}</span>
                        </div>
                      </td>
                      <td className="py-3 text-right text-red-400 tabular-nums">{formatNumber(row.bazEmisyon)}</td>
                      <td className="py-3 text-right text-green-400 tabular-nums">{formatNumber(row.optimizeEmisyon)}</td>
                      <td className="py-3 text-right text-muted-foreground">- % {row.azaltim.toFixed(1)}</td>
                      <td className="py-3 text-right text-red-400 tabular-nums">{formatCurrency(row.bazVergi)}</td>
                      <td className="py-3 text-right text-green-400 tabular-nums">{formatCurrency(row.optimizeVergi)}</td>
                      <td className="py-3 text-right text-primary tabular-nums">+ {formatCurrency(row.tasarruf)}</td>
                      <td className="py-3 text-right text-foreground font-medium tabular-nums">{formatCurrency(row.kumulatifTasarruf)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-border bg-accent/30">
                    <td colSpan={5} className="py-3 text-foreground font-bold">TOPLAM (2026-2034)</td>
                    <td className="py-3 text-right text-red-400 font-bold tabular-nums">{formatCurrency(toplamlar.bazVergiToplam)}</td>
                    <td className="py-3 text-right text-green-400 font-bold tabular-nums">{formatCurrency(toplamlar.optimizeVergiToplam)}</td>
                    <td colSpan={2} className="py-3 text-right text-primary font-bold tabular-nums">€ {formatNumber(toplamlar.toplamTasarruf)}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
