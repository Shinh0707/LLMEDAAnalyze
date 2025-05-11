import type { Chart } from 'chart.js';
import type { DataPoint, Paper } from './data';
import { getKNearest } from './data';
import { updatePointColors } from './chart';

/** Build canvas and side menu layout */
export function buildLayout(): { canvas: HTMLCanvasElement; sideMenu: HTMLDivElement } {
  const app = document.getElementById('app')!;
  const canvasContainer = document.createElement('div');
  canvasContainer.id = 'canvas-container';
  const canvas = document.createElement('canvas');
  canvas.id = 'plot-canvas';
  canvasContainer.appendChild(canvas);

  const sideMenu = document.createElement('div');
  sideMenu.id = 'side-menu';
  Array.from({ length: 2 }, (_, i) => i + 1).forEach(i => {
    const p = document.createElement('p');
    p.textContent = `Info placeholder ${i}`;
    sideMenu.appendChild(p);
  });

  app.appendChild(canvasContainer);
  app.appendChild(sideMenu);
  return { canvas, sideMenu };
}

/** Update side menu with paper info and neighbors */
export function updateSideMenu(
  sideMenu: HTMLDivElement,
  clicked: DataPoint,
  paper: Paper,
  neighbors: Array<{ point: DataPoint; dist: number; idx: number; paper: Paper }>
): void {
  sideMenu.innerHTML = '';
  // Paper info
  const titleEl = document.createElement('h3');
  titleEl.textContent = paper.title;
  sideMenu.appendChild(titleEl);
  const linkEl = document.createElement('a');
  linkEl.href = paper.url;
  linkEl.target = '_blank';
  linkEl.textContent = paper.url;
  sideMenu.appendChild(linkEl);
  // Clicked keyword
  const kwEl = document.createElement('p');
  kwEl.textContent = `Keyword: ${clicked.keyword}`;
  sideMenu.appendChild(kwEl);

  // Neighbors
  const info = document.createElement('p');
  info.textContent = `5-Nearest Keywords:`;
  sideMenu.appendChild(info);

  neighbors.forEach((d, i) => {
    const pEl = document.createElement('p');
    pEl.textContent = `#${i + 1}: ${d.point.keyword} (Paper: ${d.paper.title}) dist ${d.dist.toFixed(2)}`;
    sideMenu.appendChild(pEl);
  });
}

/** Setup click handler to show paper and neighbor info */
export function setupClickHandler(
  canvas: HTMLCanvasElement,
  chart: Chart,
  dataPoints: DataPoint[],
  papers: Paper[],
  sideMenu: HTMLDivElement
): void {
  canvas.addEventListener('click', evt => {
    const active = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, false);
    if (!active.length) return;
    const idx = active[0].index;
    const clicked = dataPoints[idx];
    const paper = papers.find(p => p.id === clicked.paperId)!;
    const knn = getKNearest(dataPoints, clicked, 5);
    const neighbors = knn.map(k => ({ ...k, paper: papers.find(p => p.id === k.point.paperId)! }));

    updateSideMenu(sideMenu, clicked, paper, neighbors);
    updatePointColors(chart, dataPoints.length, idx, neighbors.map(n => n.idx));
  });
}