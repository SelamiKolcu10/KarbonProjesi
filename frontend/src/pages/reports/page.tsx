import { motion } from "framer-motion";
import { FileText, Download, Eye, Filter, Search, Calendar, TrendingUp } from "lucide-react";
import { mockGeçmisRaporlar } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const formatNumber = (n: number) =>
  new Intl.NumberFormat("tr-TR").format(n);

const formatCurrency = (n: number) =>
  new Intl.NumberFormat("tr-TR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

export default function ReportsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  
  const totalEmission = mockGeçmisRaporlar.reduce((acc, r) => acc + r.emisyon, 0);
  const totalTax = mockGeçmisRaporlar.reduce((acc, r) => acc + r.cbamVergi, 0);
  const avgEmission = totalEmission / mockGeçmisRaporlar.length;
  const compliantCount = mockGeçmisRaporlar.filter(r => r.uyumluluk === "compliant").length;

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
          <h2 className="text-2xl font-bold text-foreground">Geçmiş Raporlar</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Denetim arşivi — {mockGeçmisRaporlar.length} kayıt
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2 text-xs">
            <FileText className="w-3 h-3" />
            Excel'e Aktar ( {mockGeçmisRaporlar.length} )
          </Button>
          <Button className="gap-2 text-xs">
            <Download className="w-3 h-3" />
            Tümünü İndir
          </Button>
        </div>
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
              <FileText className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Toplam Denetim</p>
                <p className="text-2xl font-bold text-foreground">{mockGeçmisRaporlar.length}</p>
                <p className="text-[10px] text-muted-foreground">kayıt</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center">
                <span className="text-green-400 text-xs">✓</span>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Uyumluluk Oranı</p>
                <p className="text-2xl font-bold text-yellow-400">%{Math.round((compliantCount / mockGeçmisRaporlar.length) * 100)}</p>
                <p className="text-[10px] text-muted-foreground">{compliantCount}/{mockGeçmisRaporlar.length} uyumlu</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-orange-400" />
              <div>
                <p className="text-xs text-muted-foreground">Ort. Emisyon</p>
                <p className="text-2xl font-bold text-orange-400">{formatNumber(Math.round(avgEmission))}</p>
                <p className="text-[10px] text-muted-foreground">tCO₂e / dönem</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <span className="text-lg text-green-400">€</span>
              <div>
                <p className="text-xs text-muted-foreground">Toplam CBAM Vergisi</p>
                <p className="text-2xl font-bold text-red-400">{formatCurrency(totalTax)}</p>
                <p className="text-[10px] text-muted-foreground">tüm dönemler</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
      >
        <Card className="glass-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">Filtreler</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Tesis adı ara..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full h-9 pl-9 pr-3 rounded-md bg-input border border-border text-sm text-foreground placeholder:text-muted-foreground"
                />
              </div>
              <select className="h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground">
                <option>Tüm Durumlar</option>
                <option>Uyumlu</option>
                <option>Dikkat</option>
                <option>Uyumsuz</option>
              </select>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="gg.aa.yyyy"
                  className="flex-1 h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground placeholder:text-muted-foreground"
                />
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="gg.aa.yyyy"
                  className="flex-1 h-9 px-3 rounded-md bg-input border border-border text-sm text-foreground placeholder:text-muted-foreground"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Reports Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="glass-card border-border">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="text-left text-muted-foreground font-medium p-4">Tarih</th>
                    <th className="text-left text-muted-foreground font-medium p-4">Tesis</th>
                    <th className="text-right text-muted-foreground font-medium p-4">Emisyon</th>
                    <th className="text-right text-muted-foreground font-medium p-4">CBAM Vergisi</th>
                    <th className="text-center text-muted-foreground font-medium p-4">İuk</th>
                    <th className="text-center text-muted-foreground font-medium p-4">Güven</th>
                    <th className="text-center text-muted-foreground font-medium p-4">İşlemciler</th>
                  </tr>
                </thead>
                <tbody>
                  {mockGeçmisRaporlar
                    .filter(r => r.tesis.toLowerCase().includes(searchTerm.toLowerCase()))
                    .map((r) => (
                    <tr key={r.id} className="border-b border-border/50 last:border-0 hover:bg-accent/30 transition-colors">
                      <td className="p-4 text-foreground">
                        <div className="flex items-center gap-2">
                          <span className="text-muted-foreground">›</span>
                          {new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium" }).format(new Date(r.tarih))}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          <span className="text-foreground">{r.tesis}</span>
                        </div>
                      </td>
                      <td className="p-4 text-right">
                        <span className="text-foreground tabular-nums">{formatNumber(r.emisyon)}</span>
                        <span className="text-muted-foreground ml-1">tCO₂e</span>
                      </td>
                      <td className="p-4 text-right text-foreground tabular-nums">{formatCurrency(r.cbamVergi)}</td>
                      <td className="p-4 text-center">
                        <Badge className={cn("text-[10px] px-2",
                          r.uyumluluk === "compliant" ? "bg-green-500/20 text-green-400 border-green-500/30" :
                          r.uyumluluk === "warning" ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" :
                          "bg-red-500/20 text-red-400 border-red-500/30"
                        )}>
                          {r.uyumluluk === "compliant" ? "Uyumlu" : r.uyumluluk === "warning" ? "Dikkat" : "Uyumsuz"}
                        </Badge>
                      </td>
                      <td className="p-4 text-center">
                        <Badge variant="outline" className={cn(
                          "text-[10px]",
                          r.guvenSkoru >= 90 ? "text-green-400" : r.guvenSkoru >= 80 ? "text-yellow-400" : "text-red-400"
                        )}>
                          % {r.guvenSkoru}
                        </Badge>
                      </td>
                      <td className="p-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <Button variant="ghost" size="icon-sm" className="w-7 h-7">
                            <Eye className="w-3.5 h-3.5" />
                          </Button>
                          <Button variant="ghost" size="icon-sm" className="w-7 h-7">
                            <Download className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
