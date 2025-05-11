/**
 * Paper metadata and keyword point model
 */
export interface Paper {
  id: number;
  title: string;
  url: string;
}
export interface DataPoint {
  x: number;
  y: number;
  keyword: string;
  paperId: number;
}

const keywordPool = [
  'EDA', 'Emotion', 'User Flow', 'Narrative', 'Feedback',
  'Immersion', 'Engagement', 'Reward', 'Challenge', 'Aesthetics'
];

/** Generate a random paper title */
function randomPaperTitle(): string {
  return `Paper_${Math.random().toString(36).substring(2, 7)}`;
}

/** Pick random keywords */
function pickRandomKeywords(count: number): string[] {
  return keywordPool
    .sort(() => 0.5 - Math.random())
    .slice(0, count);
}

/** Generate random papers */
export function generateRandomPapers(count: number): Paper[] {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    title: randomPaperTitle(),
    url: `https://example.com/paper/${i}`
  }));
}

/** Generate DataPoints for each paper and its keywords */
export function generateRandomDataPoints(
  papers: Paper[],
  keywordsPerPaper: number
): DataPoint[] {
  const pts: DataPoint[] = [];
  for (const paper of papers) {
    const kws = pickRandomKeywords(keywordsPerPaper);
    for (const kw of kws) {
      pts.push({
        paperId: paper.id,
        keyword: kw,
        x: Math.random() * 2 - 1,
        y: Math.random() * 2 - 1
      });
    }
  }
  return pts;
}

/** Compute k nearest neighbors excluding the same keyword point */
export function getKNearest(
  points: DataPoint[],
  target: DataPoint,
  k: number
): Array<{ point: DataPoint; dist: number; idx: number }> {
  return points
    .map((p, i) => ({ point: p, dist: Math.hypot(p.x - target.x, p.y - target.y), idx: i }))
    .filter(item => item.dist > 0)
    .sort((a, b) => a.dist - b.dist)
    .slice(0, k);
}