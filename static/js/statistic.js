import { requestAPI, triggerAlert } from "./exportFunc.js";

function renderTable(table, rows, batchSize = 50) {
  let index = 0;

  function work(deadline) {
    const fragment = document.createDocumentFragment();

    while (deadline.timeRemaining() > 0 && index < rows.length) {
      for (let i = 0; i < batchSize && index < rows.length; i++, index++) {
        const r = rows[index];
        const tr = document.createElement("tr");

        function ifNullConvertTrace(variable, fun) {
          if (variable == null) return (variable = " - ");
          return fun();
        }

        const read = ifNullConvertTrace(r.countRead, () => {
          return `${Math.round((r.countRead / r.countAttempt) * 100)}% (${r.countRead})`;
        });
        const mean = ifNullConvertTrace(r.countMean, () => {
          return `${Math.round((r.countMean / r.countAttempt) * 100)}% (${r.countMean})`;
        });
        const attempt = ifNullConvertTrace(r.countAttempt, () => {
          return r.countAttempt;
        });

        const avg = ifNullConvertTrace(r.countAttempt, () => {
          if (r.countRead == null)
            return `${Math.round((r.countMean / r.countAttempt) * 100)}%`;
          return `${Math.round(((r.countMean + r.countRead) / (r.countAttempt * 2)) * 100)}%`;
        });

        tr.innerHTML = `
          <td class="text-center">${r.id}</td>
          <td class="text-center">${r.word}</td>
          <td class="text-center">${r.category}</td>
          <td class="text-center">${read}</td>
          <td class="text-center">${mean}</td>
          <td class="text-center">${avg}</td>
          <td class="text-center">${attempt}</td>
        `;

        fragment.appendChild(tr);
      }
    }

    table.appendChild(fragment);

    if (index < rows.length) {
      requestIdleCallback(work);
    }
  }

  requestIdleCallback(work);
}

async function toggle(table) {
  if (table.children.length <= 0) {
    const rows = await requestAPI("/api/card/statistic", "GET", null, 10000);

    renderTable(table, rows);
  }
}

async function renderGrafic(canvas, ctx, tooltip) {
  let currentRange = 30;

  let chartState = {
    pointsA: [],
    pointsB: [],
    labels: [],
    displayedA: [],
    displayedB: [],
  };

  const colorA = "#1e293b"; // dark (Tentativas)
  const colorB = "#93c5fd"; // light (Acertos)

  /* =======================
     HIGH DPI
  ======================= */
  function resizeCanvas() {
    const DPR = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.round(rect.width * DPR);
    canvas.height = Math.round(rect.height * DPR);
    canvas.style.width = rect.width + "px";
    canvas.style.height = rect.height + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    redraw();
  }
  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  function clear() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

  function redraw() {
    if (!chartState.displayedA || !chartState.displayedB) return;
    draw(chartState.displayedA, chartState.displayedB);
  }

  /* =======================
     DRAW (STACKED BARS)
  ======================= */
  function draw(valuesA, valuesB) {
    clear();

    const padding = { top: 24, right: 20, bottom: 40, left: 48 };
    const w = canvas.clientWidth - padding.left - padding.right;
    const h = canvas.clientHeight - padding.top - padding.bottom;

    // number of groups
    const n = Math.max(valuesA.length, valuesB.length);
    if (n === 0) return;

    // totals per group for stacked scale
    const totals = new Array(n).fill(0).map((_, i) => {
      const a = valuesA[i] != null ? valuesA[i] : 0;
      const b = valuesB[i] != null ? valuesB[i] : 0;
      return a + b;
    });
    const nonNullTotals = totals.filter(v => v != null);
    const maxTotal = nonNullTotals.length ? Math.max(...nonNullTotals) : 1;
    const minVal = 0;
    const range = maxTotal === minVal ? 1 : maxTotal - minVal;

    /* ===== GRID + Y LABELS ===== */
    ctx.font = "12px system-ui";
    ctx.fillStyle = "#64748b";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.strokeStyle = "rgba(15,23,42,0.06)";
    ctx.lineWidth = 1;

    const yTicks = 4;
    for (let i = 0; i <= yTicks; i++) {
      const y = padding.top + (h / yTicks) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + w, y);
      ctx.stroke();

      const val = Math.round(maxTotal - (i / yTicks) * (maxTotal - minVal));
      ctx.fillText(val, padding.left - 10, y);
    }

    /* ===== BAR SIZING WITH DENSITY CONTROL ===== */
    const MIN_BAR_WIDTH = 18; // minimum readable bar width
    const MIN_GAP = 6; // minimum left/right gap per group

    let groupWidth = w / n;
    // prefer barWidth to be a fraction of groupWidth
    let barWidth = groupWidth * 0.7;

    if (barWidth < MIN_BAR_WIDTH) {
      barWidth = MIN_BAR_WIDTH;
      groupWidth = barWidth + MIN_GAP * 2;
    }

    const totalChartWidth = groupWidth * n;
    const offsetX = totalChartWidth < w ? (w - totalChartWidth) / 2 : 0;
    const barGap = (groupWidth - barWidth) / 2; // computed gap to center bar in group

    function valueToY(v) {
      return padding.top + h - ((v - minVal) / range) * h;
    }

    const pointsA = [];
    const pointsB = [];
    const labels = [];

    /* ===== DRAW STACKED BARS ===== */
    for (let i = 0; i < n; i++) {
      const baseX = padding.left + offsetX + i * groupWidth;
      const centerX = baseX + groupWidth / 2;

      const vA = valuesA[i] != null ? valuesA[i] : null; // Tentativas (top)
      const vB = valuesB[i] != null ? valuesB[i] : null; // Acertos (bottom)

      if (vA == null && vB == null) {
        pointsA[i] = null;
        pointsB[i] = null;
        labels.push(`${n - i}d`);
        continue;
      }

      // draw from baseline upward
      let currentY = padding.top + h;

      // bottom segment -> Acertos (colorB)
      if (vB != null && vB !== 0) {
        const yB = valueToY(vB);
        const hB = padding.top + h - yB;

        ctx.fillStyle = colorB;
        ctx.fillRect(baseX + barGap, currentY - hB, barWidth, hB);

        // move currentY to top of this segment
        currentY -= hB;
        pointsB[i] = { x: centerX, y: currentY, v: vB, idx: i };
      } else {
        pointsB[i] = null;
      }

      // top segment -> Tentativas (colorA)
      if (vA != null && vA !== 0) {
        const yA = valueToY(vA);
        const hA = padding.top + h - yA;

        ctx.fillStyle = colorA;
        ctx.fillRect(baseX + barGap, currentY - hA, barWidth, hA);

        currentY -= hA;
        pointsA[i] = { x: centerX, y: currentY, v: vA, idx: i };
      } else {
        pointsA[i] = null;
      }

      labels.push(`${n - i}d`);
    }

    chartState.pointsA = pointsA;
    chartState.pointsB = pointsB;
    chartState.labels = labels;

    /* ===== X LABELS ===== */
    ctx.fillStyle = "#64748b";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    const stepLabel = n <= 7 ? 1 : n <= 15 ? 2 : 4;
    for (let i = 0; i < n; i += stepLabel) {
      const x = padding.left + offsetX + i * groupWidth + groupWidth / 2;
      ctx.fillText(labels[i], x, padding.top + h + 10);
    }
  }

  /* =======================
     NORMALIZE
  ======================= */
  function normalizeArrays(a, b) {
    const len = Math.min(a.length, b.length);
    const target = len <= 7 ? 7 : len <= 15 ? 15 : 30;
    currentRange = target;

    function adjust(arr) {
      if (arr.length > target) return arr.slice(arr.length - target);
      if (arr.length < target) return arr.concat(Array(target - arr.length).fill(null));
      return arr;
    }

    return [adjust(a.slice(0, len)), adjust(b.slice(0, len))];
  }

  /* =======================
     TOOLTIP
  ======================= */
  canvas.addEventListener("mousemove", ev => {
    const rect = canvas.getBoundingClientRect();
    const x = ev.clientX - rect.left;

    // find nearest index by proximity to center x positions
    let nearestIdx = -1;
    let minDist = Infinity;
    const pts = chartState.pointsA.length ? chartState.pointsA : chartState.pointsB;
    for (let i = 0; i < (chartState.pointsA.length || chartState.pointsB.length); i++) {
      const p = chartState.pointsA[i] || chartState.pointsB[i];
      if (!p) continue;
      const d = Math.abs(p.x - x);
      if (d < minDist) {
        minDist = d;
        nearestIdx = i;
      }
    }
    if (nearestIdx === -1) return tooltip.classList.add("hidden");

    const pA = chartState.pointsA[nearestIdx];
    const pB = chartState.pointsB[nearestIdx];
    if (!pA && !pB) return tooltip.classList.add("hidden");

    tooltip.innerHTML = `
      <div class="text-xs opacity-70">${chartState.labels[nearestIdx]}</div>
      <div style="color:${colorA}">Developer: <b>${pA ? pA.v : "-"}</b></div>
      <div style="color:#0b66c3">Designer: <b>${pB ? pB.v : "-"}</b></div>
    `;

    const refY = (pA || pB).y;
    tooltip.style.left = Math.min(Math.max(x, 40), canvas.clientWidth - 40) + "px";
    tooltip.style.top = (refY - 44) + "px";
    tooltip.classList.remove("hidden");
  });

  canvas.addEventListener("mouseleave", () => tooltip.classList.add("hidden"));

  /* =======================
     PUBLIC API
  ======================= */
  window.createDualLineChart = function (canvasId, dataA, dataB) {
    const c = document.getElementById(canvasId);
    if (!c) return;

    const [A, B] = normalizeArrays(dataA, dataB);
    chartState.displayedA = A;
    chartState.displayedB = B;
    redraw();
  };
}

export async function init(content) {
  const canvas = document.getElementById("dualChart");
  const ctx = canvas.getContext("2d");
  const tooltip = document.getElementById("tooltip");

  const b7 = document.getElementById("b7");
  const b15 = document.getElementById("b15");
  const b30 = document.getElementById("b30");

  renderGrafic(canvas, ctx, tooltip);
  const arr1 = content.statistics.map(item => item.attempt)
  const arr2 = content.statistics.map(item => Math.round( (item.read + item.mean)/2 ))

  createDualLineChart("dualChart", arr1, arr2);

  b7.addEventListener("click", async () => {
    const list = await requestAPI("/api/card/statistic/activity?day=7", "GET", null, 10000)
    const arry = list.map(item => item.attempt)
    const arr2 = list.map(item => Math.round( (item.read + item.mean)/2 ))
    
    createDualLineChart("dualChart", arry, arr2);
  });
  b15.addEventListener("click", async () => {
    const list = await requestAPI("/api/card/statistic/activity?day=15", "GET", null, 10000)
    const kk = list.map(item => item.attempt)
    const kkk = list.map(item => Math.round( (item.read + item.mean)/2 ))

    createDualLineChart("dualChart", kk, kkk);
  });
  b30.addEventListener("click", async  () => {
    const list = await requestAPI("/api/card/statistic/activity?day=30", "GET", null, 10000)

    const arry = list.map(item => item.attempt)
    const arr2 = list.map(item => Math.round( (item.read + item.mean)/2 ))

    createDualLineChart("dualChart", arry, arr2);
  });

  
  // NÂO APAGAR - TABELA DE ESTATÍSTICAS DAS CARTAS
  const tableBodyCardsStatistic = document.getElementById(
    "cards-statistic-table-body",
  );
  const accordionStatistcAllCards = document.getElementById(
    "accordion-statistc-all-cards",
  );

  accordionStatistcAllCards.addEventListener("toggle", (e) => {
    toggle(tableBodyCardsStatistic);
  });

  return {
    destroy: async function () {},
  };
}
