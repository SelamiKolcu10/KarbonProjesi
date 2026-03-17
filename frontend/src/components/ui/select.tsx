import * as React from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";
import { ChevronDown, Check } from "lucide-react";

interface SelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  children?: React.ReactNode;
}

interface SelectContextType {
  value?: string;
  onValueChange?: (value: string) => void;
  open: boolean;
  setOpen: (open: boolean) => void;
  registerItem: (value: string, text: string) => void;
  itemMap: React.MutableRefObject<Map<string, string>>;
  triggerRef: React.MutableRefObject<HTMLButtonElement | null>;
}

const SelectContext = React.createContext<SelectContextType>({
  open: false,
  setOpen: () => {},
  registerItem: () => {},
  itemMap: { current: new Map() },
  triggerRef: { current: null },
});

function Select({ value, onValueChange, children }: SelectProps) {
  const [open, setOpen] = React.useState(false);
  const itemMap = React.useRef(new Map<string, string>());
  const triggerRef = React.useRef<HTMLButtonElement | null>(null);

  const registerItem = React.useCallback((val: string, text: string) => {
    itemMap.current.set(val, text);
  }, []);

  const ctx = React.useMemo(
    () => ({ value, onValueChange, open, setOpen, registerItem, itemMap, triggerRef }),
    [value, onValueChange, open, registerItem]
  );

  return (
    <SelectContext.Provider value={ctx}>
      <div className="relative">
        {children}
      </div>
    </SelectContext.Provider>
  );
}

function SelectTrigger({
  className,
  children,
  ...props
}: React.ComponentProps<"button">) {
  const { open, setOpen, triggerRef } = React.useContext(SelectContext);
  return (
    <button
      ref={triggerRef}
      type="button"
      onClick={() => setOpen(!open)}
      className={cn(
        "flex h-10 w-full items-center justify-between rounded-lg border px-3 py-2 text-sm",
        "bg-[#1a2236] border-white/20 text-foreground",
        "hover:bg-[#1e2840] hover:border-white/30 focus:outline-none focus:ring-2 focus:ring-primary/60",
        open && "ring-2 ring-primary/60 border-primary/40",
        className
      )}
      {...props}
    >
      {children}
      <ChevronDown className={cn("h-4 w-4 opacity-80 shrink-0 ml-2 transition-transform", open && "rotate-180")} />
    </button>
  );
}

function SelectValue({ placeholder }: { placeholder?: string }) {
  const { value, itemMap } = React.useContext(SelectContext);
  const displayText = value ? itemMap.current.get(value) || value : "";
  return <span className="truncate font-medium">{displayText || placeholder}</span>;
}

function SelectContent({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const { open, setOpen, triggerRef } = React.useContext(SelectContext);
  const ref = React.useRef<HTMLDivElement>(null);
  const [style, setStyle] = React.useState<React.CSSProperties>({});

  React.useEffect(() => {
    if (!open || !triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    setStyle({
      position: "fixed",
      top: rect.bottom + 4,
      left: rect.left,
      width: rect.width,
      zIndex: 9999,
    });
  }, [open, triggerRef]);

  React.useEffect(() => {
    if (!open) return;
    const handleClick = (e: MouseEvent) => {
      if (
        ref.current && !ref.current.contains(e.target as Node) &&
        triggerRef.current && !triggerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open, setOpen, triggerRef]);

  if (!open) return null;

  return createPortal(
    <div
      ref={ref}
      style={style}
      className={cn(
        "min-w-[180px] rounded-xl border border-white/20 bg-[#111827] py-1 shadow-2xl shadow-black/40",
        className
      )}
    >
      {children}
    </div>,
    document.body
  );
}

function SelectItem({
  value: itemValue,
  children,
  className,
}: {
  value: string;
  children: React.ReactNode;
  className?: string;
}) {
  const { value, onValueChange, setOpen, registerItem } = React.useContext(SelectContext);
  const isSelected = value === itemValue;
  const textRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (textRef.current) {
      registerItem(itemValue, textRef.current.textContent || itemValue);
    }
  }, [itemValue, registerItem]);

  const handleClick = React.useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    // Use microtask to close dropdown after state update
    onValueChange?.(itemValue);
    requestAnimationFrame(() => {
      setOpen(false);
    });
  }, [itemValue, onValueChange, setOpen]);

  return (
    <div
      ref={textRef}
      onClick={handleClick}
      className={cn(
        "relative flex cursor-pointer select-none items-center justify-between rounded-lg mx-1 px-3 py-2.5 text-sm",
        "hover:bg-white/15 text-white/90 transition-colors duration-100",
        isSelected && "bg-white/10 text-white",
        className
      )}
    >
      <span className="pointer-events-none">{children}</span>
      {isSelected && <Check className="w-4 h-4 text-primary ml-2 shrink-0 pointer-events-none" />}
    </div>
  );
}

export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue };
