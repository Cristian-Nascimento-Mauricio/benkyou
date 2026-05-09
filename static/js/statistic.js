import {
  convertRomajiToJapanCaracter,
  requestAPI,
  triggerAlert,
} from "./exportFunc.js";

function renderTable(table, rows, batchSize = 50) {
  let index = 0;
  table.replaceChildren();
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

async function setMeasure(value, element) {
  const valueFormat = (value * 100).toFixed(1);
  element.classList.remove("text-green-600", "text-yellow-600", "text-red-600");

  if (value == null) {
    element.classList.add("text-gray-600");
    element.textContent = `-`;
    return;
  }

  if (valueFormat >= 75) {
    element.classList.add("text-green-600");
  } else if (valueFormat < 75 || valueFormat >= 50) {
    element.classList.add("text-yellow-600");
  } else if (valueFormat < 50) {
    element.classList.add("text-red-600");
  }

  element.textContent = `${valueFormat}%`;
}

async function setGraphic(graphic,data) {

  const d = new Date();

  const attempts = data.map((item) => item.attempt);
  const dates =  data.map((item) => new Date(item.day).toLocaleDateString("pt-br", { day: "2-digit", month: "2-digit" }).toString());
  const attemptsErros = data.map((item) => (item.mean + item.read) / 2);

  console.log(attempts);
  console.log(attemptsErros);
  console.log(dates);

  let chart = new Chart(graphic, {
    data: {
      labels: dates,
      datasets: [
        {
          type: "bar",
          label: "Erros",
          data: attemptsErros,
          backgroundColor: "rgba(76, 175, 80, 0.7)",
          stack: "resultado",
        },
        {
          type: "bar",
          label: "Tentativas",
          data: attempts,
          backgroundColor: "rgba(255, 152, 0, 0.7)",
          stack: "resultado",
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true },
      },
    },
  });

  return chart;
}

async function updateGraphic(chart, date) {
    const dataStatic = await requestAPI(`/api/card/statistic/activity?day=${date}`, 'GET', null, 10000);
    console.log(dataStatic);
    chart.data.labels = dataStatic.map((item) => new Date(item.day).toLocaleDateString("pt-br", { day: "2-digit", month: "2-digit" }).toString());
    chart.data.datasets[0].data = dataStatic.map((item) => item.attempt);
    chart.data.datasets[1].data = dataStatic.map((item) => (item.mean + item.read) / 2);
    chart.update();
}

export async function init(content) {

  console.log(content);
  const graphic = document.getElementById("graphic");

  const tableBodyCardsStatistic = document.getElementById("cards-statistic-table-body");

  const optionsCategory = document.getElementById("options-category");
  const optionsKeyboard = document.getElementById("options-keyboard");
  const optionsCategoryStatistic = document.getElementById("options-category-statistic");

  const btn7days = document.getElementById("btn-7-days");
  const btn15days = document.getElementById("btn-15-days");
  const btn30days = document.getElementById("btn-30-days");



  const inFilter = document.getElementById("in-filter");
  const btnFilter = document.getElementById("btn-filter");

  const outAverage = document.getElementById("out-average");
  const outMedian = document.getElementById("out-median");
  const outMode = document.getElementById("out-mode");

  const outQuantityAttempts = document.getElementById("out-quantity-attempts");

  let data = [];

  let chart= await setGraphic(graphic,content.statistics);

  btn7days.addEventListener("click", async () => {
    updateGraphic(chart, 7);
  })

  btn15days.addEventListener("click", async () => {
    updateGraphic(chart, 15);
  })

  btn30days.addEventListener("click", async () => {
    updateGraphic(chart, 30);
  } )


  btnFilter.addEventListener("click", () => {
    triggerAlert("okay", "INFOR", 1000);
    renderTable(
      tableBodyCardsStatistic,
      data.filter((item) =>
        item.word.toLowerCase().includes(inFilter.value.trim().toLowerCase()),
      ),
    );
  });

  inFilter.addEventListener("input", (event) => {
    event.target.value = convertRomajiToJapanCaracter(
      optionsKeyboard.value,
      event.target.value,
    );
  });

  outQuantityAttempts.textContent = content.measures.count.toLocaleString("pt-br");
  setMeasure(content.measures.average, outAverage);
  setMeasure(content.measures.med, outMedian);
  setMeasure(content.measures.mode, outMode);

  optionsCategoryStatistic.addEventListener("change", async (event) => {
    const dataStatic = await requestAPI(
      `/api/statistic/attempt?category=${event.target.value}`,
      "GET",
      null,
      10000,
    );
    const averageFormat = (dataStatic.average * 100).toFixed(1);
    const medFormat = (dataStatic.med * 100).toFixed(1);
    const modeFormat = (dataStatic.mode * 100).toFixed(1);
    const quantityFormat = dataStatic.count.toLocaleString("pt-br");

    outQuantityAttempts.textContent = quantityFormat;

    setMeasure(dataStatic.average, outAverage);
    setMeasure(dataStatic.med, outMedian);
    setMeasure(dataStatic.mode, outMode);
  });

  optionsCategory.addEventListener("change", async (event) => {
    data = await requestAPI(
      `/api/statistic/card?category=${event.target.value}`,
      "GET",
      null,
      10000,
    );
    renderTable(tableBodyCardsStatistic, data);
  });

  return {
    destroy: async function () {},
  };
}
