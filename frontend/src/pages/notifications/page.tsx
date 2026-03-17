import { motion } from "framer-motion";
import { Bell, AlertCircle, AlertTriangle, Info, Check } from "lucide-react";
import { mockNotifications } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";

const notificationIcons = {
  critical: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const notificationColors = {
  critical: {
    icon: "text-destructive",
    badge: "bg-red-500 text-white",
    bg: "border-destructive/20 bg-destructive/5",
  },
  warning: {
    icon: "text-yellow-400",
    badge: "bg-yellow-500 text-black",
    bg: "border-yellow-500/20 bg-yellow-500/5",
  },
  info: {
    icon: "text-blue-400",
    badge: "bg-blue-500 text-white",
    bg: "border-blue-500/20 bg-blue-500/5",
  },
};

type FilterType = "all" | "critical" | "warning" | "info";

const filterOptions: { value: FilterType; label: string }[] = [
  { value: "all", label: "Tümü" },
  { value: "critical", label: "Kritik" },
  { value: "warning", label: "Uyarı" },
  { value: "info", label: "Bilgi" },
];

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState(mockNotifications);
  const [filterType, setFilterType] = useState<FilterType>("all");

  const markAsRead = (id: number) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, okundu: true } : n)
    );
  };

  const filteredNotifications = filterType === "all"
    ? notifications
    : notifications.filter(n => n.tip === filterType);

  const unreadCount = notifications.filter(n => !n.okundu).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold text-foreground">Bildirimler</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Sistem uyarıları ve bilgi mesajları
        </p>
      </motion.div>

      {/* Category Filter */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.05 }}
        className="flex items-center gap-2"
      >
        {filterOptions.map((opt) => {
          const isActive = filterType === opt.value;
          const count = opt.value === "all"
            ? notifications.length
            : notifications.filter(n => n.tip === opt.value).length;

          return (
            <button
              key={opt.value}
              onClick={() => setFilterType(opt.value)}
              className={cn(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
                isActive
                  ? "bg-primary text-primary-foreground border-primary shadow-sm"
                  : "bg-transparent text-muted-foreground border-border hover:bg-accent hover:text-foreground"
              )}
            >
              {opt.label}
              <span className={cn(
                "text-[10px] tabular-nums px-1.5 py-0.5 rounded-full",
                isActive ? "bg-primary-foreground/20" : "bg-muted"
              )}>
                {count}
              </span>
            </button>
          );
        })}
      </motion.div>

      {/* Notifications List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="max-w-2xl"
      >
        <div className="space-y-3">
          {filteredNotifications.map((n, i) => {
            const colors = notificationColors[n.tip as keyof typeof notificationColors];
            const Icon = notificationIcons[n.tip as keyof typeof notificationIcons];
            
            return (
              <motion.div
                key={n.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
              >
                <Card className={cn("glass-card border transition-all", colors.bg, n.okundu && "opacity-60")}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className={cn("flex-shrink-0 mt-0.5", colors.icon)}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={cn("text-[10px] uppercase", colors.badge)}>
                            {n.tip === "critical" ? "KRİTİK" : n.tip === "warning" ? "UYARI" : "BİLGİ"}
                          </Badge>
                          {!n.okundu && (
                            <span className="w-2 h-2 rounded-full bg-primary" />
                          )}
                        </div>
                        <p className="text-sm font-medium text-foreground">{n.mesaj}</p>
                        <p className="text-xs text-muted-foreground mt-1">{n.zaman}</p>
                      </div>
                      {!n.okundu && (
                        <button
                          onClick={() => markAsRead(n.id)}
                          className="flex-shrink-0 p-1 rounded hover:bg-accent transition-colors"
                        >
                          <Check className="w-4 h-4 text-muted-foreground" />
                        </button>
                      )}
                      {n.okundu && (
                        <Check className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {filteredNotifications.length === 0 && (
          <Card className="glass-card border-border">
            <CardContent className="p-12 text-center">
              <Bell className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
              <p className="text-sm text-muted-foreground">Bu kategoride bildirim bulunmuyor</p>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </div>
  );
}
