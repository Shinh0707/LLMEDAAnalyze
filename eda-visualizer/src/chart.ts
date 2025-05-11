import {
  Chart,
  ScatterController,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend,
  type ChartConfiguration
} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';
import type { DataPoint } from './data';

// 必要なコンポーネントとプラグインを登録
Chart.register(
  ScatterController,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend,
  zoomPlugin
);

/** Create a scatter chart of keyword points */
export function createScatterChart(
  ctx: CanvasRenderingContext2D,
  dataPoints: DataPoint[],
  colors: string[]
): Chart {
  const config: ChartConfiguration = {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Keyword Embedding',
        data: dataPoints.map(p => ({ x: p.x, y: p.y })),
        pointRadius: 6,
        backgroundColor: colors
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { type: 'linear', min: -1, max: 1 },
        y: { type: 'linear', min: -1, max: 1, reverse: true }
      },
      plugins: {
        legend: { display: false },
        zoom: {
          pan: { enabled: true, mode: 'xy' },
          zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'xy' }
        }
      }
    }
  };
  return new Chart(ctx, config);
}

/**
 * Update chart point colors (fade non-neighbors)
 */
export function updatePointColors(
  chart: Chart,
  totalCount: number,
  clickedIndex: number,
  neighborIndices: number[]
): void {
  const defaultColor = 'rgba(0, 122, 204, 0.8)';
  const fadedColor = 'rgba(200, 200, 200, 0.3)';
  const neighborSet = new Set(neighborIndices);
  neighborSet.add(clickedIndex);
  const colors = Array.from({ length: totalCount }, (_, i) =>
    neighborSet.has(i) ? defaultColor : fadedColor
  );
  chart.data.datasets![0].backgroundColor = colors;
  chart.update();
}