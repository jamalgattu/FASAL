import React from "react";
import { Route } from "../types";

// Renders a schematic (NOT geographically accurate) visualization of a
// route's stop sequence using each stop's lat/lng, scaled to fit a
// fixed viewBox. This is for illustrating stop order only — real route
// geometry will come from a mapping/routing service later.
export function RouteMapSVG({ route, accent = "#166534" }: { route: Route; accent?: string }) {
  const lats = route.stops.map((s) => s.location.lat);
  const lngs = route.stops.map((s) => s.location.lng);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);

  const pad = 40;
  const width = 320;
  const height = 220;

  const scaleX = (lng: number) =>
    maxLng === minLng ? width / 2 : pad + ((lng - minLng) / (maxLng - minLng)) * (width - 2 * pad);
  // Invert Y since higher latitude should render higher up.
  const scaleY = (lat: number) =>
    maxLat === minLat ? height / 2 : height - pad - ((lat - minLat) / (maxLat - minLat)) * (height - 2 * pad);

  const points = route.stops
    .slice()
    .sort((a, b) => a.sequence - b.sequence)
    .map((s) => ({ ...s, x: scaleX(s.location.lng), y: scaleY(s.location.lat) }));

  const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto" role="img" aria-label={`${route.isOptimized ? "Optimized" : "Baseline"} route diagram`}>
      <path d={pathD} fill="none" stroke={accent} strokeWidth={2} strokeDasharray={route.isOptimized ? "0" : "5,4"} />
      {points.map((p, i) => (
        <g key={p.id}>
          <circle cx={p.x} cy={p.y} r={9} fill={p.type === "pickup" ? "#166534" : "#1d4ed8"} />
          <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize={9} fill="white" fontWeight={700}>
            {i + 1}
          </text>
          <text x={p.x} y={p.y + 22} textAnchor="middle" fontSize={9} fill="#57534e">
            {p.type === "pickup" ? "Pickup" : "Delivery"}
          </text>
        </g>
      ))}
    </svg>
  );
}
