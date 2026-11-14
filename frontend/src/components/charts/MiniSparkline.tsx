import React from 'react';

interface MiniSparklineProps {
  data: number[];
  width?: number;
  height?: number;
  positive?: boolean;
}

export const MiniSparkline: React.FC<MiniSparklineProps> = ({
  data,
  width = 64,
  height = 24,
  positive = true,
}) => {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * (width - 4) + 2;
      const y = height - 3 - ((val - min) / range) * (height - 6);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  const strokeColor = positive ? 'rgb(var(--success))' : 'rgb(var(--danger))';
  const fillColor = positive ? 'rgba(var(--success), 0.15)' : 'rgba(var(--danger), 0.15)';

  const firstX = 2;
  const lastX = width - 2;
  const closedPath = `M ${points.split(' ')[0]} L ${points} L ${lastX},${height} L ${firstX},${height} Z`;

  return (
    <svg
      width={width}
      height={height}
      className="overflow-visible shrink-0 select-none"
      aria-hidden="true"
    >
      <path d={closedPath} fill={fillColor} />
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
};
