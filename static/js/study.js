import { requestAPI } from "./exportFunc.js";


function normalizeText(text) {
  return text
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\s+/g, " ")
    .replace(/[\u0300-\u036f]/g, "");
}



export async function init(content) {
  const word = document.getElementById("word");
  const inAnswer = document.getElementById("in-answer");
  const correctAnswer = document.getElementById("correct-answer");
  const typeAnswer = document.getElementById("type-answer");
  const btnSend = document.getElementById("btn-send");
  const btnValidateAnswer = document.getElementById("btn-validate-answer");
  const ratioRange = document.getElementById("ratio-range");
  const buttonsLevel = document.querySelectorAll(".button-level");


  const btnOpenConfig = document.getElementById("btn-open-config");
  const popupConfig = document.getElementById("popup-config");  


  btnOpenConfig.addEventListener("click", async () => {
    const data = await requestAPI("/api/get_config_of_select_card", "GET",null ,null);

    console.log("Configurações recebidas:", data);  
    ratioRange.value = Number( data.range.value );
    ratioRange.dispatchEvent(new Event("input", { bubbles: true }));

    buttonsLevel.forEach(button => {  
      button.checked = data.levels.find( item => item.key == button.dataset.level ).value == "ON" ? true:false;

    })

    popupConfig.classList.toggle("hidden");
  })

  let myAnswer = {
    cardId: null,
    reading: null,
    meaning: null,
  };
  let card = null;
  let state = [];


  function startNextCard(nextCard) {
    inAnswer.focus();

    card = nextCard;
    myAnswer = {
      cardId: card.id,
      reading: null,
      meaning: null,
    };
    state = [];

    const br = document.createElement("br");
    correctAnswer.replaceChildren(br);

    btnSend.classList.remove("bg-green-300", "bg-red-300");
    btnSend.classList.add("bg-blue-300");

    if (card.reading.length <= 0) {
      typeAnswer.textContent = "significado";
      state.push("READING", "CHECK-READING");
    } else {
      typeAnswer.textContent = "leitura";
    }

    word.textContent = card.word;
  }


  if (!word || !inAnswer || !typeAnswer || !btnSend || !btnValidateAnswer) {
    console.error("❌ Elementos não encontrados!");
    return;
  }

  async function handleSendClick() {
    const myWord = normalizeText(inAnswer.value);

    if (!state.includes("READING")) {
      // Verifica leitura
      let existMyAnswerInCorrectList = false;
      for (const item of card.reading) {
        if (myWord === normalizeText(item)) {
          existMyAnswerInCorrectList = true;
          break;
        }
      }

      if (existMyAnswerInCorrectList) {
        btnSend.classList.remove("bg-blue-300");
        btnSend.classList.add("bg-green-300");
        myAnswer.reading = 1;
      } else {
        btnSend.classList.remove("bg-blue-300");
        btnSend.classList.add("bg-red-300");
        btnValidateAnswer.classList.remove("bg-gray-300");
        btnValidateAnswer.classList.add("bg-green-300");
        btnValidateAnswer.disabled = false;
        myAnswer.reading = 0;
      }

      correctAnswer.textContent = card.reading.join(", ");
      inAnswer.disabled = true;
      state.push("READING");
    } else if (!state.includes("CHECK-READING")) {
      // Transição para significado
      btnSend.classList.remove("bg-red-300", "bg-green-300");
      btnSend.classList.add("bg-blue-300");

      const br = document.createElement("br");
      correctAnswer.replaceChildren(br);

      typeAnswer.textContent = "significado";

      inAnswer.value = "";
      inAnswer.disabled = false;

      btnValidateAnswer.classList.remove("bg-green-300");
      btnValidateAnswer.classList.add("bg-gray-300");
      btnValidateAnswer.disabled = true;

      state.push("CHECK-READING");
    } else if (!state.includes("MEANING")) {
      // Verifica significado
      let existMyAnswerInCorrectList = false;
      for (const item of card.meaning) {
        if (myWord === normalizeText(item)) {
          existMyAnswerInCorrectList = true;
          break;
        }
      }

      if (existMyAnswerInCorrectList) {
        btnSend.classList.remove("bg-blue-300");
        btnSend.classList.add("bg-green-300");
        myAnswer.meaning = 1;
      } else {
        btnSend.classList.remove("bg-blue-300");
        btnSend.classList.add("bg-red-300");
        btnValidateAnswer.classList.remove("bg-gray-300");
        btnValidateAnswer.classList.add("bg-green-300");
        btnValidateAnswer.disabled = false;
        myAnswer.meaning = 0;
      }

      correctAnswer.textContent = card.meaning.join(", ");
      inAnswer.disabled = true;
      state.push("MEANING");
    } else if (!state.includes("CHECK-MEANING")) {
      // Finaliza e busca próxima carta
      btnSend.classList.remove("bg-red-300", "bg-green-300");
      btnSend.classList.add("bg-blue-300");

      btnValidateAnswer.classList.remove("bg-green-300");
      btnValidateAnswer.classList.add("bg-gray-300");
      btnValidateAnswer.disabled = true;

      inAnswer.value = "";
      inAnswer.disabled = false;

      correctAnswer.replaceChildren(document.createElement("br"));

      // Envia resposta e busca próxima      
      state.push("CHECK-MEANING");

      startNextCard(await requestAPI("/api/my_answer", "POST", myAnswer,5000 /* 5 segundos*/));

    }

    // Desabilita botão temporariamente
    btnSend.disabled = true;
    setTimeout(() => {
      btnSend.disabled = false;
    }, 400);

    inAnswer.focus();
  }


  function handleValidateClick() {
    const popup = document.getElementById("popup-modal");
    const btnConfirm = document.getElementById("btn-confirm");
    const btnCancel = document.getElementById("btn-cancel");
    const btnClose = document.getElementById("btn-close");
    const inNewAnswer = document.getElementById("in-new-answer");

    if (!popup || !btnConfirm || !btnCancel || !btnClose || !inNewAnswer) {
      console.error("❌ Elementos do popup não encontrados");
      return;
    }

    popup.classList.remove("hidden");
    inNewAnswer.value = inAnswer.value;
    inNewAnswer.focus();

    function closePopup() {
      popup.classList.add("hidden");
    }

    
    // Remove listeners anteriores para evitar duplicação
    btnCancel.replaceWith(btnCancel.cloneNode(true));
    btnClose.replaceWith(btnClose.cloneNode(true));
    btnConfirm.replaceWith(btnConfirm.cloneNode(true));

    // Re-referencia após clone
    const newBtnCancel = document.getElementById("btn-cancel");
    const newBtnClose = document.getElementById("btn-close");
    const newBtnConfirm = document.getElementById("btn-confirm");

    newBtnCancel.addEventListener("click", closePopup);
    newBtnClose.addEventListener("click", closePopup);

    newBtnConfirm.addEventListener("click", async function handleConfirm() {
      this.disabled = true;

      btnValidateAnswer.classList.remove("bg-green-300");
      btnValidateAnswer.classList.add("bg-gray-300");

      const sendAnswer = {
        CARDID: myAnswer.cardId,
        TAG: null,
        WORD: inAnswer.value.trim(),
      };

      if (state.at(-1) === "READING") {
        sendAnswer["TAG"] = "READING";
        myAnswer.reading = 1;
      } else if (state.at(-1) === "MEANING") {
        sendAnswer["TAG"] = "MEANING";
        myAnswer.meaning = 1;
      } else {
        closePopup();
        return;
      }

      try {
        const response = await fetch("api/answer", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(sendAnswer),
        });

        if (response.ok) {
          btnSend.classList.remove("bg-blue-300", "bg-red-300");
          btnSend.classList.add("bg-green-300");
        }
      } catch (error) {
        console.error("Erro ao enviar resposta alternativa:", error);
      }

      setTimeout(() => {
        this.disabled = false;
      }, 400);

      btnValidateAnswer.disabled = true;
      closePopup();

      // Remove este listener após uso
      this.removeEventListener("click", handleConfirm);
    });
  }


  buttonsLevel.forEach(button => {
    button.addEventListener("change", (e) => {
      requestAPI("/api/update_level", "POST", 
        { 
          level: e.target.dataset.level, 
          value: e.target.checked 
        });
    })}
  )
  ratioRange.addEventListener("change", (e) => {
    requestAPI("/api/update_ratio", "POST", { ratio: e.target.value });
  })

  btnSend.addEventListener("click", handleSendClick); 

  btnValidateAnswer.addEventListener("click", handleValidateClick);

  function handleKeyup(event) {
    if (event.repeat) return;
    if (event.key === "Enter") {
      btnSend.click();
    }
  }

  document.addEventListener("keyup", handleKeyup);
  

  try {
    // Foca no input
    inAnswer.focus();

    // Busca primeira carta
    card = content;

    // Configura estado inicial
    myAnswer.cardId = card.id;
    word.textContent = card.word;
    btnValidateAnswer.disabled = true;

    if (card.reading.length <= 0) {
      typeAnswer.textContent = "significado";
      state.push("READING", "CHECK-READING");
    } else {
      typeAnswer.textContent = "leitura";
    }

    console.log("✅ Módulo inicializado com sucesso");
    console.log("- Palavra:", card.word);
    console.log("- typeAnswer:", typeAnswer.textContent);
    console.log("- Estado inicial:", state);
  } catch (error) {
    console.error("❌ Erro na inicialização:", error);
  }

  return {
    destroy: async function () {
      console.log("🧹 Destruindo módulo study");

      btnSend.removeEventListener("click", handleSendClick);
      btnValidateAnswer.removeEventListener("click", handleValidateClick);
      document.removeEventListener("keyup", handleKeyup);

      myAnswer = { cardId: null, reading: null, meaning: null };
      card = null;
      state = [];

    },
  };
}
