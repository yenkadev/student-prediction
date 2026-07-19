import type { RiskLevel } from "../types";
import "./RiskBadge.css";

const LABELS: Record<RiskLevel, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

const SHORT_LABELS: Record<RiskLevel, string> = {
  low: "Low",
  medium: "Med",
  high: "High",
};

interface RiskBadgeProps {
  level: RiskLevel;
  riskProb?: number;
  short?: boolean;
}

export function RiskBadge({ level, riskProb, short }: RiskBadgeProps) {
  const label = short ? SHORT_LABELS[level] : LABELS[level];
  const percent = riskProb !== undefined ? `${Math.round(riskProb * 100)}%` : undefined;
  return (
    <span className={`risk-badge risk-badge--${level}`}>
      {label}
      {percent ? ` · ${percent}` : ""}
    </span>
  );
}

export function RiskDot({ level }: { level: RiskLevel }) {
  return <span className={`risk-dot risk-dot--${level}`} />;
}
