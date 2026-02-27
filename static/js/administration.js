import { convertRomajiToJapanCaracter, requestAPI, triggerAlert } from "./exportFunc.js";


async function loadCards(popupModal, tableBody, category = "ALL", listCard) {
  const data = await requestAPI(
    `api/cards?category=${category}`,
    "GET",
    null,
    5000,
  );
  renderCards(popupModal, tableBody,data);
  listCard.splice(0, listCard.length, ...data);
}
async function renderCards(popupModal, tableBody, cards) {
  tableBody.innerHTML = cards.map(card => `
    <tr id="${card.id}" class="hover:bg-gray-50 align-top">

      <td class="px-4 py-2 border-b font-semibold text-gray-600">
        ${card.id}
      </td>

      <td class="px-4 py-2 border-b">
        <p class="w-full border border-gray-300 rounded px-2 py-1"
           data-field="word">${card.word ?? ""}</p>
      </td>

      <td class="px-4 py-2 border-b">
        <p class="w-full border border-gray-300 rounded px-2 py-1"
           data-field="category">${card.category ?? ""}</p>
      </td>

      <td class="px-4 py-2 border-b">
        <div class="flex flex-col gap-1">
          ${(card.meaning || []).map((m, i) => `
            <p class="w-full border border-gray-300 rounded px-2 py-1"
               data-type="meaning"
               data-index="${i}">${m ?? ""}</p>
          `).join("")}
        </div>
      </td>

      <td class="px-4 py-2 border-b">
        <div class="flex flex-col gap-1">
          ${(card.reading || []).map((r, i) => `
            <p class="w-full border border-gray-300 rounded px-2 py-1"
               data-type="reading"
               data-index="${i}">${r ?? ""}</p>
          `).join("")}
        </div>
      </td>

      <td class="px-4 py-2 border-b">
        <div class="flex justify-center gap-2">
          <button
            class="px-3 py-1 text-sm text-white bg-blue-500 rounded hover:bg-blue-600"
            data-action="update"
            data-id="${card.id}">
            Atualizar
          </button>

          <button
            class="px-3 py-1 text-sm text-white bg-red-500 rounded hover:bg-red-600"
            data-action="delete"
            data-id="${card.id}">
            Excluir
          </button>
        </div>
      </td>

    </tr>
  `).join("");

    tableBody.addEventListener("click", e => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const id = Number(btn.dataset.id);

    if (btn.dataset.action === "update") {
        const card = cards.find(c => c.id === id);
        openModal(popupModal, card);
    }

    if (btn.dataset.action === "delete") {
        deleteCard(id);
    }
    });


}

function openModal(popupModal, rendCard) {
    const modalElements = {
      inUpdateWord: document.getElementById("in-update-word"),
      selectUpdateCategory: document.getElementById("select-update-category"),
      meaningFields: document.getElementById("meaning-fields"),
      readingFields: document.getElementById("reading-fields"),
      btnCloseModal: document.getElementById("btn-close-modal"),
      btnUpdateCancel: document.getElementById("btn-update-cancel"),
      btnUpateConfirm: document.getElementById("btn-update-confirm"),
      btnAddNewReading: document.getElementById("btn-add-new-reading"),
      btnAddNewMeaning: document.getElementById("btn-add-new-meaning"),
    };

    function closeModal() {
      popupModal.classList.add("hidden");
    }

    function renderUpdateCard(field, item, rendCardList, type) {
      const row = document.createElement("div");
      row.classList.add("flex", "gap-2");

      const input = document.createElement("input");
      input.type = "text";
      input.value = item;
      input.classList.add(
        "flex-1",
        "px-3",
        "py-2",
        "border",
        "border-gray-300",
        "rounded-md",
        "focus:outline-none",
        "focus:ring-2",
        "focus:ring-blue-500",
        "focus:border-blue-500",
      );

      if (type === "meaning") {
        input.classList.add("input-mean");
      } else if (type === "reading") {
        input.classList.add("input-read");
      }

      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "✕";
      button.classList.add(
        "px-3",
        "py-2",
        "text-red-600",
        "hover:text-red-800",
      );

      button.addEventListener("click", () => {
        field.replaceChildren();
        const newRendCardList = rendCardList.filter(
          (itemList) => itemList.trim() !== item.trim(),
        );
        newRendCardList.forEach((newItem) =>
          renderUpdateCard(field, newItem, newRendCardList, type),
        );
      });

      row.appendChild(input);
      row.appendChild(button);
      field.appendChild(row);
    }

    function setupModalEventListeners() {
      // Remove listeners antigos (clone elements)
      modalElements.btnCloseModal.replaceWith(
        modalElements.btnCloseModal.cloneNode(true),
      );
      modalElements.btnUpdateCancel.replaceWith(
        modalElements.btnUpdateCancel.cloneNode(true),
      );
      modalElements.btnUpateConfirm.replaceWith(
        modalElements.btnUpateConfirm.cloneNode(true),
      );
      modalElements.btnAddNewReading.replaceWith(
        modalElements.btnAddNewReading.cloneNode(true),
      );
      modalElements.btnAddNewMeaning.replaceWith(
        modalElements.btnAddNewMeaning.cloneNode(true),
      );

      // Re-referencia
      const newBtnCloseModal = document.getElementById("btn-close-modal");
      const newBtnUpdateCancel = document.getElementById("btn-update-cancel");
      const newBtnUpateConfirm = document.getElementById("btn-update-confirm");
      const newBtnAddNewReading = document.getElementById(
        "btn-add-new-reading",
      );
      const newBtnAddNewMeaning = document.getElementById(
        "btn-add-new-meaning",
      );

      // Adiciona novos listeners
      newBtnCloseModal.addEventListener("click", closeModal);
      newBtnUpdateCancel.addEventListener("click", closeModal);

      newBtnAddNewReading.addEventListener("click", () => {
        rendCard.reading.unshift("");
        modalElements.readingFields.replaceChildren();
        rendCard.reading.forEach((read) =>
          renderUpdateCard(
            modalElements.readingFields,
            read,
            rendCard.reading,
            "reading",
          ),
        );
      });

      newBtnAddNewMeaning.addEventListener("click", () => {
        rendCard.meaning.unshift("");
        modalElements.meaningFields.replaceChildren();
        rendCard.meaning.forEach((mean) =>
          renderUpdateCard(
            modalElements.meaningFields,
            mean,
            rendCard.meaning,
            "meaning",
          ),
        );
      });

      newBtnUpateConfirm.addEventListener("click", () => {
        const cardUpdated = {
          id: rendCard.id,
          word: modalElements.inUpdateWord.value,
          reading: Array.from(document.querySelectorAll(".input-read"))
            .filter((item) => item.value.trim() !== "")
            .map((item) => item.value),
          meaning: Array.from(document.querySelectorAll(".input-mean"))
            .filter((item) => item.value.trim() !== "")
            .map((item) => item.value),
          category: modalElements.selectUpdateCategory.value,
        };

        fetch("/api/card", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(cardUpdated),
        }).then((res) => {
          if (res.status === 200) {
            closeModal();
          }
        });
      });
    }

    popupModal.classList.remove("hidden");
    modalElements.inUpdateWord.value = rendCard.word;
    modalElements.selectUpdateCategory.value = rendCard.category;

    modalElements.readingFields.replaceChildren();
    modalElements.meaningFields.replaceChildren();

    rendCard.reading.forEach((read) =>
      renderUpdateCard(
        modalElements.readingFields,
        read,
        rendCard.reading,
        "reading",
      ),
    );
    rendCard.meaning.forEach((mean) =>
      renderUpdateCard(
        modalElements.meaningFields,
        mean,
        rendCard.meaning,
        "meaning",
      ),
    );

    setupModalEventListeners();
}

function filterCards( popupModal, tableBody, inFilter, listCard) {

  const filterText = inFilter.value.trim().toLowerCase();

  const list = listCard.filter(item => {
      return item.word
      .trim()
      .toLowerCase()
      .includes(filterText
        .trim()
        .toLowerCase()) || 
      item.category
      .trim()
      .toLowerCase()
      .includes(filterText
        .trim()
        .toLowerCase()) || 
      item.meaning.some(m => m.trim().toLowerCase().includes(filterText)) ||
      item.reading.some(r => r.trim().toLowerCase().includes(filterText));
  })

  console.log("Filtro aplicado:", filterText, list);
  renderCards(popupModal, tableBody, list );

}


export async function init() {

  let listCard = []

  const elements = {
    inWord: document.getElementById("input-word"),
    inReading: document.getElementById("input-reading"),
    inMeaning: document.getElementById("input-meaning"),
    selectCategory: document.getElementById("select-category"),
    btnReadingAdd: document.getElementById("btn-reading-add"),
    btnMeaningAdd: document.getElementById("btn-meaning-add"),
    listReading: document.getElementById("list-reading"),
    listMeaning: document.getElementById("list-meaning"),
    btnSend: document.getElementById("btn-send"),
    btnCancel: document.getElementById("btn-cancel"),
    toast: document.getElementById("toast"),
    cardsTableBody: document.getElementById("cards-table-body"),
  };


  const btnFilter = document.getElementById("btn-filter");
  const inFilter = document.getElementById("in-filter");
  const tableBody = document.getElementById("cards-table-body")
  const optionsCategory = document.getElementById("options-category");
  const optionsKeyboard = document.getElementById("options-keyboard");
  const popupModal = document.getElementById("popup-modal");

  btnFilter.addEventListener("click", () => {
    filterCards( popupModal,tableBody, inFilter, listCard);
  })

  inFilter.addEventListener("input", (event) => { 
    event.target.value = convertRomajiToJapanCaracter(optionsKeyboard.value, event.target.value);

  })

  optionsCategory.addEventListener("change", async (event) => {
      await loadCards(popupModal, tableBody, event.target.value, listCard);
  })

  for (const [key, element] of Object.entries(elements)) {
    if (!element && key !== "popupModal") {
      // popupModal pode ser opcional
      console.error(`❌ Elemento não encontrado: ${key}`);
      return;
    }
  }

  let card = {
    word: null,
    reading: [],
    meaning: [],
    category: null,
  };

  const cardManager = {
    pushReading(card, value) {
      if (!value?.trim()) return card;
      return {
        ...card,
        reading: [...card.reading, value.trim()],
      };
    },

    pushMeaning(card, value) {
      if (!value?.trim()) return card;
      return {
        ...card,
        meaning: [...card.meaning, value.trim()],
      };
    },

    removeReading(card, index) {
      return {
        ...card,
        reading: card.reading.filter((_, i) => i !== index),
      };
    },

    removeMeaning(card, index) {
      return {
        ...card,
        meaning: card.meaning.filter((_, i) => i !== index),
      };
    },

    setWord(card, word) {
      return { ...card, word: word?.trim() || null };
    },

    setCategory(card, category) {
      return { ...card, category: category?.trim() || null };
    },

    clearCard() {
      return {
        word: null,
        reading: [],
        meaning: [],
        category: card.category,
      };
    },
  };

  function constructionItem(list, lambda, word) {
    const div = document.createElement("div");
    const p = document.createElement("p");
    const button = document.createElement("button");

    div.className =
      "inline-flex items-center shadow-lg px-1 hover:scale-105 rounded-lg gap-2 transition-all duration-200 transform origin-center";
    p.className = "m-0";
    button.className = "bg-red-200 px-2 py-1 rounded hover:bg-red-300";

    p.innerText = word;
    button.innerText = "+";

    button.addEventListener("click", lambda);

    div.appendChild(p);
    div.appendChild(button);

    list.appendChild(div);
  }

  function renderReadingList() {
    elements.listReading.replaceChildren();
    card.reading.forEach((item, index) => {
      constructionItem(
        elements.listReading,
        () => {
          card = cardManager.removeReading(card, index);
          renderReadingList();
        },
        item,
      );
    });
  }

  function renderMeaningList() {
    elements.listMeaning.replaceChildren();
    card.meaning.forEach((item, index) => {
      constructionItem(
        elements.listMeaning,
        () => {
          card = cardManager.removeMeaning(card, index);
          renderMeaningList();
        },
        item,
      );
    });
  }


  function deleteCard(id) {
    if (confirm("Tem certeza que deseja excluir este card?")) {
      fetch(`/api/card/${id}`, {
        method: "DELETE",
      })
        .then(async (res) => {
          const data = await res.json();
          const p = document.createElement("p");

          if (res.ok) {
            const tr = document.getElementById(String(id));
            if (tr) tr.remove();
            p.innerText = data.message || "Card excluído com sucesso!";
            p.className = "text-green-600";
          } else {
            p.innerText = data.error || "Erro ao excluir card";
            p.className = "text-red-600";
          }

          elements.toast.appendChild(p);
          setTimeout(() => elements.toast.replaceChildren(), 3000);
        })
        .catch((error) => {
          const p = document.createElement("p");
          p.innerText = "Erro na requisição";
          p.className = "text-red-600";
          elements.toast.appendChild(p);
          setTimeout(() => elements.toast.replaceChildren(), 3000);
        });
    }
  }

  function clearForm() {
    card = cardManager.clearCard();
    renderMeaningList();
    renderReadingList();
    elements.inWord.value = "";
    elements.inMeaning.value = "";
    elements.inReading.value = "";
  }

  elements.inWord.addEventListener("input", (e) => {
    card = cardManager.setWord(card, e.target.value);
  });

  // Botão adicionar leitura
  elements.btnReadingAdd.addEventListener("click", () => {
    const value = elements.inReading.value.trim();
    if (value) {
      card = cardManager.pushReading(card, value);
      elements.inReading.value = "";
      renderReadingList();
    }
  });

  // Botão adicionar significado
  elements.btnMeaningAdd.addEventListener("click", () => {
    const value = elements.inMeaning.value.trim();
    if (value) {
      card = cardManager.pushMeaning(card, value);
      elements.inMeaning.value = "";
      renderMeaningList();
    }
  });

  // Seletor de categoria
  elements.selectCategory.addEventListener("change", (e) => {
    card = cardManager.setCategory(card, e.target.value);
    localStorage.setItem("default-category", e.target.value);
  });

  // Botão cancelar
  elements.btnCancel.addEventListener("click", clearForm);

  // Botão enviar
  elements.btnSend.addEventListener("click", () => {
    const erros = [];
    const p = document.createElement("p");

    if (!card.word) erros.push("word");
    if (card.meaning.length <= 0) erros.push("Meaning");
    if (!card.category) erros.push("category");

    if (erros.length > 0) {
      p.innerText = "Campos não preenchidos: " + erros.join(", ");
      elements.toast.appendChild(p);
      setTimeout(() => elements.toast.replaceChildren(), 5 * 1000);
      return;
    }

    fetch("api/card", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(card),
    })
      .then((res) => {
        const p = document.createElement("p");

        if (res.status === 201) {
          p.innerText = "Card criado com sucesso!";
          p.className = "text-green-600";
          clearForm();
        } else {
          p.innerText = "Erro na criação do card!";
          p.className = "text-red-600";
        }

        elements.toast.appendChild(p);
        setTimeout(() => elements.toast.replaceChildren(), 5 * 1000);

        // Recarrega a lista de cards
      })
      .catch((error) => {
        console.error("Erro ao criar card:", error);
      });
  });


  try {
    const defaultCategory = localStorage.getItem("default-category");
    if (defaultCategory) {
      card.category = defaultCategory;
      elements.selectCategory.value = defaultCategory;
    } else {
      localStorage.setItem("default-category", elements.selectCategory.value);
      card.category = elements.selectCategory.value;
    }


    console.log("✅ Módulo administration inicializado com sucesso");
  } catch (error) {
    console.error("❌ Erro na inicialização:", error);
  }

  return {
    destroy: async function () {

      listCard = [];
      console.log("✅ Listas limpas");
      card = {
        word: null,
        reading: [],
        meaning: [],
        category: null,
      };

      elements.listReading.replaceChildren();
      elements.listMeaning.replaceChildren();
      elements.cardsTableBody.replaceChildren();

      console.log("✅ Módulo administration destruído");
    },
  };
}

export function createAdministrationModule() {
  return {
    init: init,
    destroy: async () => console.log("Destroy padrão"),
  };
}
