import { motion } from "framer-motion";
import { AlertTriangle, AlertCircle, BarChart3, ChevronRight, Info } from "lucide-react";
import { mockEmissionBreakdown, mockMonthlyTrend, mockEmissionDetails, mockMaliEtki, mockCbamTimeline, mockAuditTrail } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, LineChart, Line, ReferenceLine } from "recharts";

const formatNumber = (n: number) =>
  new Intl.NumberFormat("tr-TR").format(n);

export default function EmissionPage() {
  const totalEmission = mockEmissionBreakdown.sources.reduce((acc, s) => acc + s.value, 0);

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
          <h2 className="text-2xl font-bold text-foreground">Emisyon Analizi</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Ajan 2 çıkışı — 2025 1. Çeyrek · İzmir Çelik Fabrikası A.Ş.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2 text-xs border-yellow-500/30 text-yellow-400">
            <AlertCircle className="w-3 h-3" />
            2 Anomali Tespit Edildi
          </Button>
          <Button variant="outline" className="gap-2 text-xs">
            <BarChart3 className="w-3 h-3" />
            124.850 tCO₂e Toplam
          </Button>
        </div>
      </motion.div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scope Breakdown Pie Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="glass-card border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-foreground">Emisyon Kapsamı Dağılımı</CardTitle>
              <p className="text-xs text-muted-foreground">Kapsam 1 / Kapsam 2 / Proses — tCO₂e</p>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-8">
                <div className="w-48 h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: "Kapsam 1 (Doğrudan)", value: mockEmissionBreakdown.scope1, color: "#F59E0B" },
                          { name: "Scope 2 (Elektrik)", value: mockEmissionBreakdown.scope2, color: "#3B82F6" },
                          { name: "Proses Emisyonları", value: mockEmissionBreakdown.process, color: "#8B5CF6" },
                        ]}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        dataKey="value"
                        stroke="none"
                      >
                        <Cell fill="#F59E0B" />
                        <Cell fill="#3B82F6" />
                        <Cell fill="#8B5CF6" />
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3 flex-1">
                  {[
                    { name: "Kapsam 1 (Doğrudan)", value: mockEmissionBreakdown.scope1, color: "#F59E0B" },
                    { name: "Scope 2 (Elektrik)", value: mockEmissionBreakdown.scope2, color: "#3B82F6" },
                    { name: "Proses Emisyonları", value: mockEmissionBreakdown.process, color: "#8B5CF6" },
                  ].map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-xs text-muted-foreground">{item.name}</span>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-foreground">{formatNumber(item.value)}</p>
                        <p className="text-[10px] text-muted-foreground">
                          % {((item.value / totalEmission) * 100).toFixed(1)}
                        </p>
                      </div>
                    </div>
                  ))}
                  <div className="pt-2 border-t border-border">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-foreground">Toplam</span>
                      <span className="text-sm font-bold text-foreground">{formatNumber(totalEmission)} tCO₂e</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Source Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <Card className="glass-card border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-foreground">Emisyonlar</CardTitle>
              <p className="text-xs text-muted-foreground">Kaynak bazlı kırılım — tCO₂e</p>
            </CardHeader>
            <CardContent>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mockEmissionBreakdown.sources} layout="horizontal">
                    <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v/1000}k`} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                      labelStyle={{ color: '#f1f5f9' }}
                      formatter={(value: number) => [formatNumber(value) + ' tCO₂e', '']}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {mockEmissionBreakdown.sources.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Monthly Trend */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-foreground">Aylık Emisyon Trendi</CardTitle>
                <p className="text-xs text-muted-foreground">2025 yılı — hedef ile karşılaştırma</p>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-0.5 bg-green-400" />
                  <span className="text-muted-foreground">Gerçek</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-0.5 bg-red-400 opacity-50" style={{ borderTop: '2px dashed' }} />
                  <span className="text-muted-foreground">Hedef</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockMonthlyTrend}>
                  <XAxis dataKey="ay" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v/1000}k`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#f1f5f9' }}
                    formatter={(value: number) => [formatNumber(value) + ' tCO₂e', '']}
                  />
                  <ReferenceLine y={16000} stroke="#ef4444" strokeDasharray="5 5" strokeOpacity={0.5} />
                  <Line type="monotone" dataKey="emisyon" stroke="#22c55e" strokeWidth={2} dot={{ fill: '#22c55e', strokeWidth: 0, r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Detailed Emission Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.25 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3 flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">Detaylı Emisyon Kırılımı</CardTitle>
              <p className="text-xs text-muted-foreground">Kaynak, miktar, birim ve tCO₂e değerleri</p>
            </div>
            <Button variant="outline" size="sm" className="gap-1 text-xs text-yellow-400 border-yellow-500/30">
              <AlertTriangle className="w-3 h-3" />
              Anormallikler
            </Button>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left text-muted-foreground font-medium pb-2">Emisyon kaynağı</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">Miktar</th>
                    <th className="text-left text-muted-foreground font-medium pb-2 pl-2">Birim</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">kg CO₂</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">tCO₂e</th>
                    <th className="text-center text-muted-foreground font-medium pb-2">Durum</th>
                  </tr>
                </thead>
                <tbody>
                  {mockEmissionDetails.map((row) => (
                    <tr key={row.id} className={cn(
                      "border-b border-border/50 last:border-0",
                      row.anomali && "bg-yellow-500/5"
                    )}>
                      <td className="py-3 text-foreground">
                        <div className="flex items-center gap-2">
                          {row.anomali && <AlertTriangle className="w-3 h-3 text-yellow-400" />}
                          {row.kaynak}
                        </div>
                      </td>
                      <td className="py-3 text-right text-foreground tabular-nums">{formatNumber(row.miktar)}</td>
                      <td className="py-3 text-left text-muted-foreground pl-2">{row.birim}</td>
                      <td className="py-3 text-right text-muted-foreground tabular-nums">{formatNumber(row.kgCO2)}</td>
                      <td className="py-3 text-right text-foreground font-medium tabular-nums">{formatNumber(row.tCO2e)}</td>
                      <td className="py-3 text-center">
                        <Badge className={cn(
                          "text-[10px] px-1.5",
                          row.anomali 
                            ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" 
                            : "bg-green-500/20 text-green-400 border-green-500/30"
                        )}>
                          {row.anomali ? "Anormallikler" : "Normal"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t border-border">
                    <td colSpan={4} className="py-3 text-foreground font-semibold">Toplam</td>
                    <td className="py-3 text-right text-foreground font-bold tabular-nums">{formatNumber(totalEmission)}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Mali Etki & Audit Trail */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mali Etki */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Card className="glass-card border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <span className="text-lg">€</span>
                Mali Etki — CBAM Yükümlülüğü
              </CardTitle>
              <p className="text-xs text-muted-foreground">2025 Q1 dönemi · Faz: % 2.5</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-background/50 border border-border">
                  <p className="text-xs text-muted-foreground">CBAM Faz Faktörü</p>
                  <p className="text-xl font-bold text-yellow-400">%{mockMaliEtki.cbamFazFaktoru}</p>
                  <p className="text-[10px] text-muted-foreground">2026 başlangıç oranı</p>
                </div>
                <div className="p-3 rounded-lg bg-background/50 border border-border">
                  <p className="text-xs text-muted-foreground">Brüt Vergi Yükümlülüğü</p>
                  <p className="text-xl font-bold text-red-400">{formatNumber(mockMaliEtki.brutVergi)} €</p>
                  <p className="text-[10px] text-muted-foreground">Hesaplanan toplam</p>
                </div>
                <div className="p-3 rounded-lg bg-background/50 border border-border">
                  <p className="text-xs text-muted-foreground">Etkin Vergi</p>
                  <p className="text-xl font-bold text-orange-400">{formatNumber(mockMaliEtki.efektifVergi)} €</p>
                  <p className="text-[10px] text-muted-foreground">Krediler düşüldükten sonra</p>
                </div>
                <div className="p-3 rounded-lg bg-background/50 border border-border">
                  <p className="text-xs text-muted-foreground">Çelik Başına Maliyet</p>
                  <p className="text-xl font-bold text-foreground">{mockMaliEtki.celikBasinaMaliyet} €/ton</p>
                  <p className="text-[10px] text-muted-foreground">{formatNumber(mockMaliEtki.uretimMiktari)} ton üretim</p>
                </div>
              </div>

              {/* CBAM Timeline */}
              <div className="mt-6">
                <p className="text-xs font-medium text-foreground mb-3">CBAM Aşamalı Takvimi (2026-2034)</p>
                <div className="flex items-center gap-1">
                  {mockCbamTimeline.map((item, i) => (
                    <div key={item.yil} className="flex-1">
                      <div 
                        className={cn(
                          "h-2 rounded-full",
                          item.aktif ? "bg-green-500" : item.faz <= 47.5 ? "bg-border" : "bg-red-500/50"
                        )}
                      />
                      <p className="text-[9px] text-muted-foreground mt-1 text-center">% {item.faz}</p>
                      <p className="text-[9px] text-muted-foreground text-center">{item.yil}</p>
                    </div>
                  ))}
                </div>
                {mockCbamTimeline[0].aktif && (
                  <Badge className="mt-2 bg-green-500/20 text-green-400 border-green-500/30 text-[10px]">
                    Şu an
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Audit Trail */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.35 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-3 flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Info className="w-4 h-4" />
                Denetim İzleme Kaydı
              </CardTitle>
              <Badge variant="outline" className="text-[10px]">{mockAuditTrail.length} kayıt</Badge>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockAuditTrail.map((item, i) => (
                  <div key={i} className="flex gap-3 pb-3 border-b border-border/50 last:border-0 last:pb-0">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-xs font-medium text-foreground">{item.islem}</p>
                        <p className="text-[10px] text-muted-foreground flex-shrink-0">
                          {new Date(item.timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{item.detay}</p>
                      <p className="text-[10px] text-muted-foreground/70">{item.kullanici}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
