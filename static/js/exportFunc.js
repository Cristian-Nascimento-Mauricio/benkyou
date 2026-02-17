export async function triggerAlert(message, category = "INFO", time = -1) {
  const containerAlerts = document.getElementById("container-alerts");
  const alertsAlreadyExisting =
    containerAlerts.querySelectorAll(":scope > div");

  if (!containerAlerts) {
    console.error("Container de alerts não encontrado!");
    return;
  }

  if (!time) return;

  if (alertsAlreadyExisting.length >= 5) {
    alertsAlreadyExisting[0].remove();
  }

  const alert = document.createElement("div");
  alert.classList.add(
    "flex",
    "sm:items-center",
    "p-2",
    "mb-4",
    "text-sm",
    "text-fg-brand-strong",
    "rounded-md",
    "transform",
    "transition",
    "duration-500",
    "ease-in-out",
    "hover:scale-105",
  );
  const colorClass = {
    INFO: "bg-blue-300",
    DANGER: "bg-red-300",
    SUCCESS: "bg-green-300",
    WARNING: "bg-yellow-300",
  }[category];

  if (colorClass) {
    alert.classList.add(colorClass);
  }

  const myId = `alert_${Date.now()}_${Math.random()
    .toString(36)
    .substring(2, 9)}`;
  alert.id = myId;

  const svgAlert = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "svg",
  );
  svgAlert.setAttribute("class", "w-4 h-4 shrink-0 mt-0.5 md:mt-0");
  svgAlert.setAttribute("aria-hidden", "true");
  svgAlert.setAttribute("width", "24");
  svgAlert.setAttribute("height", "24");
  svgAlert.setAttribute("fill", "none");
  svgAlert.setAttribute("viewBox", "0 0 24 24");

  // Usar createElementNS também para o path
  const pathAlert = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path",
  );
  pathAlert.setAttribute("stroke", "currentColor");
  pathAlert.setAttribute("stroke-linecap", "round");
  pathAlert.setAttribute("stroke-linejoin", "round");
  pathAlert.setAttribute("stroke-width", "2");
  pathAlert.setAttribute(
    "d",
    "M10 11h2v5m-2 0h4m-2.592-8.5h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  );

  svgAlert.appendChild(pathAlert);

  const divMessage = document.createElement("div");
  divMessage.classList.add("mx-2", "text-sm");
  divMessage.innerText = message;

  const button = document.createElement("button");
  button.type = "button";
  button.className =
    "ms-auto -mx-1.5 -my-1.5 rounded focus:ring-2 focus:ring-brand-medium hover:bg-brand-soft inline-flex items-center justify-center h-8 w-8 shrink-0";
  // Corrigir o data-dismiss-target para apontar para o ID do alerta atual
  button.setAttribute("data-dismiss-target", `#${myId}`);
  button.setAttribute("aria-label", "Close");

  // Adicionar funcionalidade de fechar
  button.addEventListener("click", function () {
    alert.classList.add("opacity-0");
    alert.addEventListener(
      "transitionend",
      function (event) {
        alert.remove();
      },
      { once: true },
    );
  });

  const closeText = document.createElement("span");
  closeText.className = "sr-only";
  closeText.textContent = "Close";

  const svgBtn = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgBtn.setAttribute("class", "w-4 h-4");
  svgBtn.setAttribute("aria-hidden", "true");
  svgBtn.setAttribute("width", "24");
  svgBtn.setAttribute("height", "24");
  svgBtn.setAttribute("fill", "none");
  svgBtn.setAttribute("viewBox", "0 0 24 24");

  const pathBtn = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path",
  );
  pathBtn.setAttribute("stroke", "currentColor");
  pathBtn.setAttribute("stroke-linecap", "round");
  pathBtn.setAttribute("stroke-linejoin", "round");
  pathBtn.setAttribute("stroke-width", "2");
  pathBtn.setAttribute("d", "M6 18 17.94 6M18 18 6.06 6");

  svgBtn.appendChild(pathBtn);
  button.appendChild(closeText);
  button.appendChild(svgBtn);

  alert.appendChild(svgAlert);
  alert.appendChild(divMessage);
  alert.appendChild(button);

  containerAlerts.appendChild(alert);

  // Implementar auto-remover se time > 0
  if (time > 0) {
    setTimeout(() => {
      if (alert.parentNode) {
        alert.remove();
      }
    }, time);
  }
}

export async function requestAPI(url, method, body, time=5000) {
  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
      }, 
      ...(method !== "GET" && method !== "HEAD"
      ? { body: JSON.stringify(body) }
      : {}),
    });
    const status = response.status;
    const data = await response.json();

    switch (status) {
      case 100:
        triggerAlert(data.message, "INFO", time);

        break;
      case 101:
        triggerAlert(data.message, "INFO", time);

        break;

      case 200:
        triggerAlert(data.message, "SUCCESS", time);

        break;
      case 201:
        triggerAlert(data.message, "SUCCESS", time);

        break;
      case 202:
        triggerAlert(data.message, "SUCCESS", time);

        break;
      case 204:
        triggerAlert(data.message, "SUCCESS", time);

        break;

      case 301:
        triggerAlert(data.message, "WARNING", time);
        break;
      case 302:
        triggerAlert(data.message, "WARNING", time);
        break;
      case 304:
        triggerAlert(data.message, "WARNING", time);
        break;

      case 400:
        triggerAlert(data.message, "DANGER", time);
        break;
      case 401:
        triggerAlert(data.message, "DANGER", time);
        break;
      case 403:
        triggerAlert(data.message, "DANGER", time);
        break;
      case 404:
        triggerAlert(data.message, "DANGER", time);
        break;
      case 409:
        triggerAlert(data.message, "DANGER", time);
        break;
      case 422:
        triggerAlert(data.message, "DANGER", time);
        break;

      case 500:
        triggerAlert(data.message, "DANGER", time);

        break;
      case 502:
        triggerAlert(data.message, "DANGER", time);

        break;
      case 503:
        triggerAlert(data.message, "DANGER", time);

        break;
      case 504:
        triggerAlert(data.message, "DANGER", time);

        break;

      default:
        triggerAlert("Codigo não listado", "INFO", time);
    }

    return data.content;
  } catch (e) {
    triggerAlert("Erro na requisição: " + e.message, "DANGER", time);
    console.log(e);
    return null;
  }
}
