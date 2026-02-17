const study = document.getElementById("study");
const statistic = document.getElementById("statistic");
const adm = document.getElementById("administration");
const route = document.getElementById("route");


const scriptManager = {
  current: null,
  destroyer:null,

  normalize(path) {
    if (path.startsWith('/') || path.startsWith('./')) return path;
    return '/' + path;
  },

  async load(modulePath, content, context) {
    
    await this.unload();

    const normalized = this.normalize(modulePath);
    const url = `${normalized}`;

    const module = await import(url);

    if (module.init) {
      try {
        this.destroyer = await module.init(content);
      } catch (e) {
        console.error("Erro ao iniciar módulo:", normalized, e);
      }
    }

    this.current = { path: normalized, module};
  },

  async unload() {
    if(this.destroyer){
      this.destroyer.destroy()
      
    }
  }
};


const router = {
  currentPath: window.location.pathname,
  disabled:false,

  async navigate(path, push = true) {
    if (push) {
      history.pushState({ path }, '', path);
    }

    this.currentPath = path;

    try {
      if(!this.disabled){
        this.disabled=true
        await this.loadPage(path);
      }
    } catch (e) {
      this.showError();
    }
    this.disabled=false

  },

  async loadPage(path) {

    const { html, module , content} = await requestHTML(path);

    // 🔥 descarrega módulo atual (remove eventos!)
    await scriptManager.unload();

    // troca DOM
    route.style.opacity = '0';
    route.replaceChildren(...parseHTML(html));

    await nextFrame();
    route.style.opacity = '1';
    await nextFrame();

    // carrega módulo novo
    if (module) {
      await scriptManager.load(module, content , {
        root: route,
        path
      });
    }

  },

  showError() {
    route.innerHTML = `
      <div style="padding:2rem;text-align:center">
        <h3>Erro ao carregar página</h3>
      </div>
    `;
  }
};

/* ==============================
   EVENTOS DE NAVEGAÇÃO
================================ */
study.addEventListener("click", () => router.navigate("/study"));
statistic.addEventListener("click", () => router.navigate("/statistic"));
adm.addEventListener("click", () => router.navigate("/administration"));

window.addEventListener("popstate", e => {
  router.navigate(e.state?.path || window.location.pathname, false);
});

/* ==============================
   HELPERS
================================ */
async function requestHTML(path) {
  const res = await fetch(path, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json'
    },
    cache: 'no-store'
  });

  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }

  const data = await res.json();

  if (!data.html) {
    throw new Error('Resposta inválida (html ausente)');
  }

  return {
    html: data.html,
    module: data.module || null, // ex: "/static/js/study.js"
    content:data.content || null
  };
}

function parseHTML(html) {
  const tpl = document.createElement('template');
  tpl.innerHTML = html.trim();
  return [...tpl.content.children];
}

function nextFrame() {
  return new Promise(r => requestAnimationFrame(r));
}


window.debugRouter = {
  reload: () => router.navigate(router.currentPath),
  unload: () => scriptManager.unload()
};


router.navigate(window.location.pathname)
