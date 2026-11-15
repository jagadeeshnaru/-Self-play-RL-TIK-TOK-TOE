import React, { useState } from 'react';

export interface SeriesConfig {
  key: string;
  label: string;
  color: string;
  yAxis?: 'left' | 'right';
  formatValue?: (val: number) => string;
}

interface LineChartProps {
  title: string;
  subtitle?: string;
  data: Array<Record<string, number>>;
  xKey: string;
  series: SeriesConfig[];
  height?: number;
  yDomainLeft?: [number, number];
  yDomainRight?: [number, number];
  xFormat?: (val: number) => string;
}

export const LineChart: React.FC<LineChartProps> = ({
  title,
  subtitle,
  data,
  xKey,
  series,
  height = 200,
  yDomainLeft = [0, 100],
  yDomainRight,
  xFormat = (v) => (v >= 1000 ? `${Math.round(v / 1000)}k` : `${v}`)
}) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return (
      <div className="chart-card">
        <div className="chart-header">
          <div className="chart-title">{title}</div>
          {subtitle && <div className="chart-subtitle">{subtitle}</div>}
        </div>
        <div className="chart-empty" style={{ height }}>
          No data available yet. Train agent to view learning curves.
        </div>
      </div>
    );
  }

  const padding = { top: 20, right: yDomainRight ? 45 : 20, bottom: 25, left: 40 };
  const width = 500; // SVG viewBox coordinate width
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  // Calculate coordinates
  const minX = data[0][xKey];
  const maxX = data[data.length - 1][xKey] || minX + 1;

  const getX = (val: number) => {
    if (maxX === minX) return padding.left + plotWidth / 2;
    return padding.left + ((val - minX) / (maxX - minX)) * plotWidth;
  };

  const getLeftY = (val: number) => {
    const [minY, maxY] = yDomainLeft;
    const clamped = Math.max(minY, Math.min(maxY, val));
    return padding.top + plotHeight - ((clamped - minY) / (maxY - minY)) * plotHeight;
  };

  const getRightY = (val: number) => {
    if (!yDomainRight) return getLeftY(val);
    const [minY, maxY] = yDomainRight;
    const clamped = Math.max(minY, Math.min(maxY, val));
    return padding.top + plotHeight - ((clamped - minY) / (maxY - minY)) * plotHeight;
  };

  // Generate SVG path for a series
  const generatePath = (s: SeriesConfig) => {
    return data
      .map((d, i) => {
        const x = getX(d[xKey]);
        const y = s.yAxis === 'right' ? getRightY(d[s.key] ?? 0) : getLeftY(d[s.key] ?? 0);
        return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(' ');
  };

  const hoveredData = hoverIndex !== null && hoverIndex >= 0 && hoverIndex < data.length ? data[hoverIndex] : null;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div className="chart-title">{title}</div>
        {subtitle && <div className="chart-subtitle">{subtitle}</div>}
        <div className="chart-legend">
          {series.map((s) => (
            <div key={s.key} className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: s.color }} />
              <span className="legend-label">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="chart-container">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="chart-svg"
          onMouseLeave={() => setHoverIndex(null)}
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const relX = ((e.clientX - rect.left) / rect.width) * width;
            if (relX < padding.left || relX > width - padding.right) {
              setHoverIndex(null);
              return;
            }
            // Find closest data point
            let closestDist = Infinity;
            let closestIdx = 0;
            data.forEach((d, i) => {
              const ptX = getX(d[xKey]);
              const dist = Math.abs(ptX - relX);
              if (dist < closestDist) {
                closestDist = dist;
                closestIdx = i;
              }
            });
            setHoverIndex(closestIdx);
          }}
        >
          {/* Grid lines (horizontal) */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((frac, idx) => {
            const y = padding.top + plotHeight * (1 - frac);
            const valLeft = yDomainLeft[0] + frac * (yDomainLeft[1] - yDomainLeft[0]);
            return (
              <g key={idx}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#1E293B"
                  strokeDasharray={frac === 0 ? undefined : '2,2'}
                  strokeWidth="1"
                />
                <text x={padding.left - 6} y={y + 3} textAnchor="end" className="chart-axis-text">
                  {valLeft >= 1000 ? `${Math.round(valLeft / 1000)}k` : `${Math.round(valLeft)}${yDomainLeft[1] <= 100 && yDomainLeft[0] === 0 ? '%' : ''}`}
                </text>
                {yDomainRight && (
                  <text x={width - padding.right + 6} y={y + 3} textAnchor="start" className="chart-axis-text">
                    {Math.round(yDomainRight[0] + frac * (yDomainRight[1] - yDomainRight[0]))}
                  </text>
                )}
              </g>
            );
          })}

          {/* X axis ticks */}
          {data.length > 1 &&
            [0, Math.floor(data.length * 0.25), Math.floor(data.length * 0.5), Math.floor(data.length * 0.75), data.length - 1].map((idx) => {
              const d = data[idx];
              if (!d) return null;
              const x = getX(d[xKey]);
              return (
                <text key={idx} x={x} y={height - 6} textAnchor="middle" className="chart-axis-text">
                  {xFormat(d[xKey])}
                </text>
              );
            })}

          {/* Lines */}
          {series.map((s) => (
            <path
              key={s.key}
              d={generatePath(s)}
              fill="none"
              stroke={s.color}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ))}

          {/* Hover indicator line & dots */}
          {hoveredData && (
            <g>
              <line
                x1={getX(hoveredData[xKey])}
                y1={padding.top}
                x2={getX(hoveredData[xKey])}
                y2={padding.top + plotHeight}
                stroke="#64748B"
                strokeWidth="1"
                strokeDasharray="3,3"
              />
              {series.map((s) => {
                const cx = getX(hoveredData[xKey]);
                const cy = s.yAxis === 'right' ? getRightY(hoveredData[s.key] ?? 0) : getLeftY(hoveredData[s.key] ?? 0);
                return (
                  <circle
                    key={s.key}
                    cx={cx}
                    cy={cy}
                    r="4"
                    fill={s.color}
                    stroke="#0B0F19"
                    strokeWidth="2"
                  />
                );
              })}
            </g>
          )}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredData && (
          <div className="chart-tooltip">
            <div className="tooltip-title">Episode {hoveredData[xKey].toLocaleString()}</div>
            {series.map((s) => (
              <div key={s.key} className="tooltip-row">
                <span className="tooltip-dot" style={{ backgroundColor: s.color }} />
                <span className="tooltip-label">{s.label}:</span>
                <span className="tooltip-val" style={{ color: s.color }}>
                  {s.formatValue ? s.formatValue(hoveredData[s.key] ?? 0) : `${hoveredData[s.key]}%`}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
