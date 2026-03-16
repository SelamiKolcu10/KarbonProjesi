import * as React from "react";
import { cn } from "@/lib/utils";

interface SliderProps {
  min?: number;
  max?: number;
  step?: number;
  value?: number[];
  defaultValue?: number[];
  onValueChange?: (value: number[]) => void;
  className?: string;
}

const Slider = React.forwardRef<HTMLDivElement, SliderProps>(
  ({ min = 0, max = 100, step = 1, value, defaultValue, onValueChange, className }, ref) => {
    const currentValue = value?.[0] ?? defaultValue?.[0] ?? min;
    const percentage = ((currentValue - min) / (max - min)) * 100;
    const trackRef = React.useRef<HTMLDivElement>(null);
    const isDragging = React.useRef(false);

    const updateValue = React.useCallback(
      (clientX: number) => {
        const track = trackRef.current;
        if (!track) return;
        const rect = track.getBoundingClientRect();
        let ratio = (clientX - rect.left) / rect.width;
        ratio = Math.max(0, Math.min(1, ratio));
        let newValue = min + ratio * (max - min);
        newValue = Math.round(newValue / step) * step;
        newValue = Math.max(min, Math.min(max, newValue));
        onValueChange?.([newValue]);
      },
      [min, max, step, onValueChange]
    );

    React.useEffect(() => {
      const handleMove = (e: MouseEvent) => {
        if (isDragging.current) updateValue(e.clientX);
      };
      const handleUp = () => {
        isDragging.current = false;
      };
      document.addEventListener("mousemove", handleMove);
      document.addEventListener("mouseup", handleUp);
      return () => {
        document.removeEventListener("mousemove", handleMove);
        document.removeEventListener("mouseup", handleUp);
      };
    }, [updateValue]);

    return (
      <div
        ref={ref}
        className={cn("relative flex w-full touch-none select-none items-center h-5", className)}
      >
        <div
          ref={trackRef}
          className="relative w-full h-[6px] rounded-full bg-white/10 cursor-pointer"
          onMouseDown={(e) => {
            isDragging.current = true;
            updateValue(e.clientX);
          }}
        >
          {/* Filled track */}
          <div
            className="absolute h-full rounded-full bg-primary"
            style={{ width: `${percentage}%` }}
          />
          {/* Thumb */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-white border-2 border-primary shadow-md cursor-grab active:cursor-grabbing transition-transform hover:scale-110"
            style={{ left: `${percentage}%` }}
            onMouseDown={(e) => {
              e.stopPropagation();
              isDragging.current = true;
            }}
          />
        </div>
      </div>
    );
  }
);
Slider.displayName = "Slider";

export { Slider };
