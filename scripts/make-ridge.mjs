// Generates the footer skyline: the Wasatch Front seen from the Salt Lake Valley
// looking east (north on the left, south on the right).
//
//   node scripts/make-ridge.mjs           print the path and the data URI
//   node scripts/make-ridge.mjs --write   replace the $wfrc-ridge-mask line in
//                                         wfrc-overrides.scss between its markers
//
// Tune PEAKS / SEED / ROUGH and re-run. Output is deterministic.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const W = 1200;           // viewBox width
const H = 84;             // viewBox height; the footer ::before height must match (px)
const LAT_N = 41.45, LAT_S = 40.15;
const FT_MIN = 6000, FT_MAX = 11800;
const FLOOR = 8, SPAN = 72;   // 6,000 ft sits 8 units up; 11,800 ft sits 80 units up
const LEVELS = 4;             // midpoint displacement passes
const SEED = 20260;
const ROUGH = 0.2;            // displacement as a fraction of segment length

// lat / ft checked against Wikipedia and SummitPost (see CHANGELOG 0.5.0).
// shape: pyramid = steep narrow flanks, smooth; rugged = extra crag; massif = long summit ridge.
const PEAKS = [
  { name: "Willard Peak / Ben Lomond", lat: 41.383, ft: 9763 },
  { name: "Mt Ogden",        lat: 41.200, ft: 9579 },
  { name: "Francis Peak",    lat: 41.033, ft: 9540 },
  { name: "Farmington Peak", lat: 40.990, ft: 9255 },   // coordinates estimated, not verified
  { name: "Bountiful Peak",  lat: 40.964, ft: 9259 },
  { name: "Grandeur Peak",   lat: 40.707, ft: 8299 },
  { name: "Mt Olympus",      lat: 40.657, ft: 9030, shape: "pyramid" },
  { name: "Twin Peaks",      lat: 40.594, ft: 11330, shape: "rugged" },
  { name: "Lone Peak",       lat: 40.527, ft: 11253, shape: "rugged" },
  { name: "Box Elder Peak",  lat: 40.490, ft: 11101 },
  { name: "Mt Timpanogos",   lat: 40.391, ft: 11752, shape: "massif" },
  { name: "Provo Peak",      lat: 40.244, ft: 11068 },
];
const START_FT = 7200, END_FT = 8800;

const xOf = (lat) => ((LAT_N - lat) / (LAT_N - LAT_S)) * W;
const hOf = (ft) => FLOOR + ((ft - FT_MIN) / (FT_MAX - FT_MIN)) * SPAN;

function mulberry32(a) {
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(SEED);

const SHAPES = {
  default: { w: 18, drop: 900,  rough: 1 },
  pyramid: { w: 9,  drop: 1700, rough: 0.35 },
  rugged:  { w: 14, drop: 800,  rough: 1.7 },
  massif:  { w: 22, drop: 700,  rough: 0.9 },
};

// Key points: [x, h, rough]. Each peak gets shoulders; each gap gets a saddle.
const key = [[0, hOf(START_FT), 1]];
const peaks = PEAKS.map((p) => ({ ...p, x: xOf(p.lat), s: SHAPES[p.shape ?? "default"] }));
const lows = [{ x: 0, ft: START_FT }, ...peaks, { x: W, ft: END_FT }];
for (let i = 0; i < peaks.length; i++) {
  const p = peaks[i], prev = lows[i], next = lows[i + 2];
  const wl = Math.min(p.s.w, (p.x - prev.x) * 0.3), wr = Math.min(p.s.w, (next.x - p.x) * 0.3);
  // saddle between the previous peak and this one
  if (i > 0) {
    const a = peaks[i - 1];
    const gl = Math.min(a.s.w, (p.x - a.x) * 0.3), x0 = a.x + gl, x1 = p.x - wl;
    const ft = Math.max(6600, Math.min(a.ft, p.ft) - 1700 - rand() * 600);
    key.push([x0 + (x1 - x0) * (0.4 + rand() * 0.2), hOf(ft), a.s.rough]);
  }
  const sh = p.ft - p.s.drop;
  key.push([p.x - wl, hOf(sh), p.s.rough]);
  if (p.shape === "massif") {
    key.push([p.x - wl * 0.45, hOf(p.ft - 120), p.s.rough]);
    key.push([p.x, hOf(p.ft), p.s.rough]);
    key.push([p.x + wr * 0.45, hOf(p.ft - 90), p.s.rough]);
  } else {
    key.push([p.x, hOf(p.ft), p.s.rough]);
  }
  key.push([p.x + wr, hOf(sh), p.s.rough]);
}
key.push([W, hOf(END_FT), 1]);

// Midpoint displacement, tapered near key points so apexes stay put.
function subdivide(a, b, level) {
  if (level === 0) return [];
  const len = b[0] - a[0], rough = (a[2] + b[2]) / 2;
  const amp = ROUGH * len * rough;
  const taper = Math.min(1, Math.min(len / 2, 12) / 12);
  const m = [(a[0] + b[0]) / 2 + (rand() - 0.5) * len * 0.25,
             (a[1] + b[1]) / 2 + (rand() - 0.5) * 2 * amp * taper, rough];
  m[1] = Math.min(H - 3, Math.max(4, m[1]));
  return [...subdivide(a, m, level - 1), m, ...subdivide(m, b, level - 1)];
}
const pts = [key[0]];
for (let i = 1; i < key.length; i++) pts.push(...subdivide(key[i - 1], key[i], LEVELS), key[i]);

const f = (n) => String(Math.round(n * 10) / 10);
const d = `M0 ${H}V${f(H - pts[0][1])}` +
  pts.slice(1).map(([x, h]) => `L${f(x)} ${f(H - h)}`).join("") + `V${H}z`;
const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${W} ${H}' preserveAspectRatio='none'><path d='${d}'/></svg>`;
const uri = "data:image/svg+xml," + svg.replace(/</g, "%3C").replace(/>/g, "%3E");
const line = `$wfrc-ridge-mask: url("${uri}");`;

if (process.argv.includes("--write")) {
  const file = fileURLToPath(new URL("../_extensions/wfrc-brand/assets/theme/wfrc-overrides.scss", import.meta.url));
  const src = readFileSync(file, "utf8");
  const re = /(\/\/ ridge:begin[^\n]*\n)[^\n]*\n(\/\/ ridge:end)/;
  if (!re.test(src)) throw new Error("ridge markers not found in wfrc-overrides.scss");
  writeFileSync(file, src.replace(re, (_, a, b) => `${a}${line}\n${b}`));
  console.log(`wrote ${pts.length} points, ${d.length} path chars`);
} else {
  console.log(d, "\n\n" + line);
}
