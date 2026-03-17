import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Home } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary mb-4">404</h1>
        <p className="text-xl text-muted-foreground mb-8">{t("notFound.message")}</p>
        <Link to="/">
          <Button className="gap-2">
            <Home className="w-4 h-4" />
            {t("notFound.goHome")}
          </Button>
        </Link>
      </div>
    </div>
  );
}
