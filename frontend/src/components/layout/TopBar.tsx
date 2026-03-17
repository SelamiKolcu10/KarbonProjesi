import { Bell, Building2, ChevronDown, LogOut, Menu, Globe } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { mockNotifications } from "@/lib/mock-data";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";

const pageKeys: Record<string, string> = {
  "/": "dashboard",
  "/belge-yukle": "upload",
  "/emisyon-analizi": "emission",
  "/emisyon-projeksiyonu": "projection",
  "/strateji-raporu": "strategy",
  "/raporlar": "reports",
  "/ayarlar": "settings",
  "/bildirimler": "notifications",
};

interface TopBarProps {
  onMenuClick?: () => void;
}

export default function TopBar({ onMenuClick }: TopBarProps) {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const key = pageKeys[location.pathname] ?? "default";
  const pageTitle = t(`topbar.${key}Title`);
  const pageSubtitle = t(`topbar.${key}Subtitle`, { defaultValue: "" });
  const unreadCount = mockNotifications.filter((n) => !n.okundu).length;
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const langRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
      if (langRef.current && !langRef.current.contains(e.target as Node)) {
        setLangMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const switchLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setLangMenuOpen(false);
  };

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-4 md:px-6 sticky top-0 z-10">
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <Button
          variant="ghost"
          size="icon"
          className="w-9 h-9 md:hidden"
          onClick={onMenuClick}
        >
          <Menu className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-base font-semibold text-foreground">{pageTitle}</h1>
          <p className="text-xs text-muted-foreground hidden sm:block">{pageSubtitle}</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Language Switcher */}
        <div className="relative" ref={langRef}>
          <Button
            variant="ghost"
            size="icon"
            className="w-9 h-9"
            onClick={() => setLangMenuOpen((prev) => !prev)}
          >
            <Globe className="w-4 h-4" />
          </Button>
          {langMenuOpen && (
            <div className="absolute right-0 mt-1 w-36 rounded-lg border border-border bg-card shadow-lg py-1 z-50">
              <button
                className={`flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-accent transition-colors ${i18n.language === "en" ? "text-primary font-medium" : "text-foreground"}`}
                onClick={() => switchLanguage("en")}
              >
                {t("language.en")}
              </button>
              <button
                className={`flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-accent transition-colors ${i18n.language === "tr" ? "text-primary font-medium" : "text-foreground"}`}
                onClick={() => switchLanguage("tr")}
              >
                {t("language.tr")}
              </button>
            </div>
          )}
        </div>

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
              <p className="text-xs font-medium text-foreground">{t("topbar.companyName")}</p>
              <p className="text-[10px] text-muted-foreground">{t("topbar.role")}</p>
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
                {t("topbar.logout")}
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
