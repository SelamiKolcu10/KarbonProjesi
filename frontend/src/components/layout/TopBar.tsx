import { Bell, Building2, ChevronDown, LogOut } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { mockNotifications } from "@/lib/mock-data";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/": { title: "Kontrol Paneli", subtitle: "Genel bakış ve KPI özeti" },
  "/belge-yukle": { title: "Belge Yükle", subtitle: "PDF ve Excel işlemlerinin işlenmesi" },
  "/emisyon-analizi": { title: "Emisyon Analizi", subtitle: "Ajan 2 ortaya çıktı — programlama ve anormallik tespiti" },
  "/emisyon-projeksiyonu": { title: "Emisyon Projeksiyonu", subtitle: "2026-2034 CBAM takvimi boyunca emisyon ve vergi yükümlülüğü hesaplaması" },
  "/strateji-raporu": { title: "Strateji Raporu", subtitle: "Ajan 3 çıktısı — görünüm önerileri" },
  "/raporlar": { title: "Geçmiş Raporlar", subtitle: "Denetim arşivi ve PDF dışa aktarma" },
  "/ayarlar": { title: "Ayarlar", subtitle: "Sistem ayarları" },
  "/bildirimler": { title: "Bildirimler", subtitle: "Uyarılar ve sistem mesajları" },
};

export default function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const pageInfo = pageTitles[location.pathname] ?? { title: "CBAM Yönetimi", subtitle: "" };
  const unreadCount = mockNotifications.filter((n) => !n.okundu).length;
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-10">
      <div>
        <h1 className="text-base font-semibold text-foreground">{pageInfo.title}</h1>
        <p className="text-xs text-muted-foreground">{pageInfo.subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Notification Bell */}
        <Button
          variant="ghost"
          size="icon"
          className="relative w-9 h-9"
          onClick={() => navigate("/bildirimler")}
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-destructive rounded-full text-[9px] text-white flex items-center justify-center font-bold">
              {unreadCount}
            </span>
          )}
        </Button>

        {/* User */}
        <div className="relative" ref={menuRef}>
          <button
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg hover:bg-accent transition-colors"
            onClick={() => setUserMenuOpen((prev) => !prev)}
          >
            <div className="w-7 h-7 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
              <Building2 className="w-3.5 h-3.5 text-primary" />
            </div>
            <div className="text-left">
              <p className="text-xs font-medium text-foreground">İzmir Çelik A.Ş.</p>
              <p className="text-[10px] text-muted-foreground">Fabrika Yöneticisi</p>
            </div>
            <ChevronDown className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${userMenuOpen ? "rotate-180" : ""}`} />
          </button>

          {userMenuOpen && (
            <div className="absolute right-0 mt-1 w-44 rounded-lg border border-border bg-card shadow-lg py-1 z-50">
              <button
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-destructive hover:bg-accent transition-colors"
                onClick={() => {
                  setUserMenuOpen(false);
                  navigate("/");
                }}
              >
                <LogOut className="w-4 h-4" />
                Çıkış Yap
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
