import './style.css';
import {
  generateRandomPapers,
  generateRandomDataPoints,
  type DataPoint,
  type Paper
} from './data';
import { createScatterChart } from './chart';
import { buildLayout, setupClickHandler } from './ui';

/** Initialize application */
export function init(): void {
  const { canvas, sideMenu } = buildLayout();
  const papers: Paper[] = generateRandomPapers(20);
  const dataPoints: DataPoint[] = generateRandomDataPoints(papers, 3);
  const initialColors = dataPoints.map(() => 'rgba(0, 122, 204, 0.8)');
  const chart = createScatterChart(canvas.getContext('2d')!, dataPoints, initialColors);
  setupClickHandler(canvas, chart, dataPoints, papers, sideMenu);
}

document.addEventListener('DOMContentLoaded', init);
