import { NavLink, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Upload,
  FlaskConical,
  BrainCircuit,
  FileText,
  Settings,
  Factory,
  Leaf,
  Bell,
  Target,
  X,
} from "lucide-react";
import { mockNotifications } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";

const navItems = [
  { to: "/", label: "Kontrol Paneli", icon: LayoutDashboard },
  { to: "/belge-yukle", label: "Belge Yükle", icon: Upload },
  { to: "/emisyon-analizi", label: "Emisyon Analizi", icon: FlaskConical },
  { to: "/emisyon-projeksiyonu", label: "Emisyon Projeksiyonu", icon: Target },
  { to: "/strateji-raporu", label: "Strateji Raporu", icon: BrainCircuit },
  { to: "/raporlar", label: "Geçmiş Raporlar", icon: FileText },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const location = useLocation();
  const unreadCount = mockNotifications.filter((n) => !n.okundu).length;

  return (
    <aside
      className={cn(
        "w-64 min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col",
        "fixed md:static z-50 md:z-auto transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}
    >
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary/20 border border-primary/30 flex items-center justify-center">
            <Factory className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="font-bold text-sm text-foreground tracking-wide">CBAM</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest">Karbon Yönetimi</p>
          </div>
        </div>
        {/* Mobile close button */}
        <button
          onClick={onClose}
          className="md:hidden p-1.5 rounded-lg hover:bg-accent transition-colors text-muted-foreground"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-3 pb-2 pt-1">Navigasyon</p>
        {navItems.map(({ to, label, icon: Icon }) => {
          const isActive = to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);
          return (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary/15 text-primary border border-primary/25"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </NavLink>
          );
        })}

        <div className="pt-4">
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-3 pb-2">Sistem</p>
          <NavLink
            to="/bildirimler"
            onClick={onClose}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
              location.pathname === "/bildirimler"
                ? "bg-primary/15 text-primary border border-primary/25"
                : "text-muted-foreground hover:text-foreground hover:bg-accent"
            )}
          >
            <Bell className="w-4 h-4 flex-shrink-0" />
            Bildirimler
            {unreadCount > 0 && (
              <Badge className="ml-auto bg-destructive text-white text-[10px] px-1.5 py-0 min-w-[18px] h-[18px] flex items-center justify-center">
                {unreadCount}
              </Badge>
            )}
          </NavLink>
          <NavLink
            to="/ayarlar"
            onClick={onClose}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
              location.pathname === "/ayarlar"
                ? "bg-primary/15 text-primary border border-primary/25"
                : "text-muted-foreground hover:text-foreground hover:bg-accent"
            )}
          >
            <Settings className="w-4 h-4 flex-shrink-0" />
            Ayarlar
          </NavLink>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary/10 border border-primary/20">
          <Leaf className="w-4 h-4 text-primary" />
          <div>
            <p className="text-[11px] font-semibold text-primary">CBAM 2026</p>
            <p className="text-[10px] text-muted-foreground">Faz: %2.5 aktif</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
