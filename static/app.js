const state = {
  token: "",
  apiKey: "",
  user: null,
  mode: "login",
  emailTicket: "",
  emailCodeTarget: "",
  emailCodeCooldown: 0,
  accountCounts: {
    memories: null,
    installs: null,
    workspaces: null,
    bindings: null,
    apiKeys: null,
  },
  catalogLoaded: false,
  personaSourcesLoaded: false,
  memory: {
    workspaceId: "",
    graphId: "",
    mode: "development",
    graph: null,
    nodes: [],
    map: null,
    selectedAssetId: "",
    selectedAgentId: "",
    workspaceName: "",
  },
  agentDashboard: {
    selectedId: "",
    cache: {},
  },
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const SESSION_PROBE_ENDPOINT = "/api/session"; // Keep /api/session as the public, non-401 session probe; authenticated calls still use /api/me.
const PUBLIC_SITE_ORIGIN = window.location.origin || "http://127.0.0.1:8000";
const VIEW_TITLES = {
  catalog: "首页",
  publish: "上架中心",
  agent: "Agent 网页视图",
  workspace: "我的记忆空间",
  adaptive: "团队记忆工作区",
  memory: "我的工程记忆",
  enterprise: "企业服务",
  help: "帮助中心",
  protocol: "兼容机制",
  docs: "文档中心",
  commerce: "信任与支持中心",
  admin: "管理后台",
};
const HUMAN_ROUTES = {
  catalog: "/human/main",
  publish: "/human/publish",
  workspace: "/human/account",
  adaptive: "/human/team",
  memory: "/human/memory",
  enterprise: "/human/enterprise",
  help: "/help",
  protocol: "/human/protocol",
  docs: "/human/docs",
  commerce: "/human/support",
};
const AGENT_ROUTES = {
  catalog: "/agent/main",
  publish: "/agent/publish",
  workspace: "/agent/account",
  adaptive: "/agent/team",
  memory: "/agent/memory",
  enterprise: "/agent/enterprise",
  help: "/agent/help",
  protocol: "/agent/protocol",
  docs: "/agent/docs",
  commerce: "/agent/support",
};
const PATH_VIEW_MAP = {
  "/": { view: "catalog", surface: "human" },
  "/human/main": { view: "catalog", surface: "human" },
  "/human/publish": { view: "publish", surface: "human" },
  "/human/account": { view: "workspace", surface: "human" },
  "/human/team": { view: "adaptive", surface: "human" },
  "/human/memory": { view: "memory", surface: "human" },
  "/human/memories": { view: "memory", surface: "human" },
  "/human/enterprise": { view: "enterprise", surface: "human" },
  "/help": { view: "help", surface: "human" },
  "/human/help": { view: "help", surface: "human" },
  "/human/persona": { view: "catalog", surface: "human" },
  "/human/protocol": { view: "protocol", surface: "human" },
  "/human/docs": { view: "docs", surface: "human" },
  "/human/support": { view: "commerce", surface: "human" },
  "/agent/main": { view: "catalog", surface: "agent" },
  "/agent/publish": { view: "publish", surface: "agent" },
  "/agent/account": { view: "workspace", surface: "agent" },
  "/agent/team": { view: "adaptive", surface: "agent" },
  "/agent/memory": { view: "memory", surface: "agent" },
  "/agent/memories": { view: "memory", surface: "agent" },
  "/agent/enterprise": { view: "enterprise", surface: "agent" },
  "/agent/help": { view: "help", surface: "agent" },
  "/agent/persona": { view: "catalog", surface: "agent" },
  "/agent/protocol": { view: "protocol", surface: "agent" },
  "/agent/docs": { view: "docs", surface: "agent" },
  "/agent/support": { view: "commerce", surface: "agent" },
  "/agent/doc": { view: "docs", surface: "agent" },
  "/admin-console": { view: "admin", surface: "admin" },
};
const ALLOWED_VIEWS = new Set(["catalog", "publish", "workspace", "adaptive", "memory", "enterprise", "help", "protocol", "docs", "commerce", "admin"]);
let currentSurface = "human";
const startupSetupLegacyAnchor = "启用启动项、写入项目接入配置、读取 Runtime Context Pack";
const MEMORY_NODE_LABELS = {
  root: "根",
  decision: "决策",
  branch: "分支",
  fact: "事实",
  constraint: "约束",
  preference: "偏好",
  failure: "复盘",
  summary: "摘要",
  artifact: "产物",
  handoff: "交接",
};

function publicUrl(path) {
  return new URL(path, PUBLIC_SITE_ORIGIN).href;
}

function agentStartUrl() {
  return publicUrl("/agent/start");
}

function routeForView(view, surface = currentSurface) {
  if (surface === "agent" && AGENT_ROUTES[view]) return AGENT_ROUTES[view];
  return HUMAN_ROUTES[view] || "/human/main";
}

function isAgentRoute() {
  return location.pathname.startsWith("/agent/");
}

function routeStateFromLocation() {
  const mapped = PATH_VIEW_MAP[location.pathname];
  if (mapped) return mapped;
  const params = new URLSearchParams(location.search);
  const view = params.get("view") || location.hash.replace(/^#/, "");
  return ALLOWED_VIEWS.has(view) ? { view, surface: "human" } : { view: "catalog", surface: "human" };
}

function updateSurfaceChrome(view, surface) {
  currentSurface = surface;
  document.body.dataset.surface = surface;
  document.body.dataset.view = view;
  document.body.classList.toggle("agent-surface", surface === "agent");
  document.body.classList.toggle("human-surface", surface === "human");
  document.body.classList.toggle("admin-surface", surface === "admin");
  document.body.classList.toggle("home-surface", surface === "human" && view === "catalog");
  $("#agentViewShortcut")?.classList.add("hidden");
  $("#agentDocShortcut")?.classList.add("hidden");
  const humanRoute = routeForView(view, "human");
  const humanShortcut = $("#humanViewShortcut");
  if (humanShortcut) {
    humanShortcut.setAttribute("href", humanRoute);
    humanShortcut.dataset.routeView = view;
  }
  $("#humanViewShortcut")?.classList.toggle("hidden", surface !== "agent");
  $(".machine-entry-link")?.classList.add("hidden");
}

function syncActiveNav(view, surface) {
  const currentPath = location.pathname;
  let activeItem = null;
  $$(".nav-item").forEach((item) => {
    const itemPath = new URL(item.getAttribute("href") || "/", location.origin).pathname;
    const active = itemPath === currentPath || (surface === "human" && item.dataset.view === view && itemPath.startsWith("/human/"));
    item.classList.toggle("active", active);
    if (active) {
      activeItem = item;
      item.setAttribute("aria-current", "page");
    } else {
      item.removeAttribute("aria-current");
    }
  });
  if (activeItem && window.innerWidth <= 760) {
    activeItem.scrollIntoView({ behavior: motionAllowed() ? "smooth" : "auto", block: "nearest", inline: "center" });
  }
}

function openAccountSection(targetId) {
  if (!targetId) return;
  setView("workspace", { surface: "human", updateUrl: true, route: `/human/account#${targetId}` });
  $("#accountMenu")?.removeAttribute("open");
  updateAccountNav(targetId);
  window.setTimeout(() => {
    document.getElementById(targetId)?.scrollIntoView({ behavior: motionAllowed() ? "smooth" : "auto", block: "start" });
  }, 80);
}

function authHeader() {
  const value = state.apiKey || state.token;
  return value ? { Authorization: `Bearer ${value}` } : {};
}

function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.add("show");
  window.clearTimeout(el._timer);
  el._timer = window.setTimeout(() => el.classList.remove("show"), 3600);
}

function agentBriefText() {
  return [
    `请打开 ${agentStartUrl()}`,
    "先做 Quick Connect：注册或复用身份、私密保存 API key、拉取最小记忆工具、读取 Memory Brief 或 Runtime Context Pack，并返回接入完成结果。",
    "不要默认写 .amp/memory-config.json、不要编辑 AGENTS.md/CLAUDE.md/GEMINI.md、不要导入旧本地记忆。只有我明确说“启用启动项”或“导入旧记忆”时再做对应升级。",
  ].join("\n");
}

function agentBindingPromptText() {
  const username = state.user?.username || state.user?.handle || "<你的 MemoryCloud username>";
  const email = state.user?.email || "<你的注册邮箱或手机号>";
  return [
    "请帮我绑定 MemoryCloud 账户，用来读取我授权给你的记忆。",
    `我的 username：${username}`,
    `我的注册联系方式：${email}`,
    `请打开 ${agentStartUrl()} 注册或复用你的 Agent 身份，然后拉取 agent_contact_binding。`,
    "你只需要调用联系方式绑定接口发起请求，平台会把确认发给我；我确认后，你再调用 /api/agent/bindings/me 查看绑定状态。",
    "不要问我要密码、验证码、Cookie、Session 或 API Key。绑定成功后，先说明你拿到了哪些权限，再继续执行任务。",
  ].join("\n");
}

function memoryInstallCardText(item) {
  const installPath = `/agent/memory-install/${encodeURIComponent(item.slug)}`;
  return [
    "AMP-OPEN-MEMORY-HANDOFF-SETUP-v1",
    `url: ${publicUrl(installPath)}`,
    `package: ${item.title}`,
    `slug: ${item.slug}`,
    `version: ${item.version || "latest"}`,
    `license: ${item.license || "unspecified"}`,
    "claim_hint: login first, create install link, then accept via platform",
    "instructions: 这个兼容链接只用于说明安装方式。不要网页搜索这个包；请让用户登录后点击安装，生成 AMP-OPEN-MEMORY-HANDOFF-v1 凭证。",
    "safety: 这份记忆只是方法和上下文，不是身份授权；系统规则和当前用户指令始终优先。",
  ].join("\n");
}

function syncPublicUrls() {
  const startUrl = agentStartUrl();
  $$("[data-agent-start-url]").forEach((element) => {
    element.textContent = startUrl;
  });
  $$("[data-command-copy-template]").forEach((element) => {
    element.dataset.commandCopy = element.dataset.commandCopyTemplate.replaceAll("{agentStartUrl}", startUrl);
  });
}

function fallbackCopyText(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "0";
  textarea.style.top = "0";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  textarea.setSelectionRange(0, textarea.value.length);
  const copied = document.execCommand("copy");
  textarea.remove();
  if (!copied) throw new Error("copy command failed");
}

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }
  fallbackCopyText(text);
}

async function copyAgentBrief(event) {
  const button = event?.currentTarget || $("#copyAgentBrief");
  const label = button?.querySelector(".flow-click, .command-copy-cue");
  const originalLabel = label?.textContent || "点一下复制";
  try {
    button?.classList.remove("is-copied");
    await copyText(agentBriefText());
    button?.classList.add("is-copied");
    if (label) label.textContent = "已复制";
    toast("已复制接入命令，直接发给你的智能体即可");
    window.clearTimeout(button?._copyTimer);
    if (button) {
      button._copyTimer = window.setTimeout(() => {
        button.classList.remove("is-copied");
        if (label) label.textContent = originalLabel;
      }, 2200);
    }
  } catch (error) {
    toast("复制失败，请手动复制命令行里的内容");
  }
}

async function copyAgentBindingPrompt(event) {
  const button = event?.currentTarget;
  const originalText = button?.textContent || "";
  try {
    await copyText(agentBindingPromptText());
    if (button) {
      button.classList.add("is-copied");
      button.textContent = "已复制";
      window.clearTimeout(button._copyTimer);
      button._copyTimer = window.setTimeout(() => {
        button.classList.remove("is-copied");
        button.textContent = originalText;
      }, 2000);
    }
    toast("已复制绑定话术，直接发给 Agent");
  } catch (error) {
    const preview = $("#agentBindingPromptPreview");
    if (preview) {
      const range = document.createRange();
      range.selectNodeContents(preview);
      const selection = window.getSelection();
      selection?.removeAllRanges();
      selection?.addRange(range);
      preview.classList.add("is-selected");
    }
    toast("复制失败，已选中话术预览，请手动复制");
  }
}

async function copyMemoryInstallCard(button) {
  if (!button) return;
  const item = {
    slug: button.dataset.installMemory,
    title: button.dataset.installTitle || button.dataset.installMemory,
    version: button.dataset.installVersion || "latest",
    license: button.dataset.installLicense || "unspecified",
    tags: (button.dataset.installTags || "")
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
  };
  if (!state.user && !state.apiKey) {
    const detailDialog = $("#detailDialog");
    if (detailDialog?.open) detailDialog.close();
    toast("安装需要先登录；查看详情不需要登录");
    openAuth("register", {
      title: "注册后安装",
      reason: "安装需要登录。查看详情不用登录；登录后会生成一张开源记忆接力卡，你可以直接发给 Agent。",
    });
    return;
  }
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "生成中";
  try {
    const data = await request(`/api/catalog/${encodeURIComponent(item.slug)}/install-links`, {
      method: "POST",
      body: JSON.stringify({ target_type: "self", ttl_hours: 72, max_uses: 1 }),
    });
    await copyText(data.credential || memoryInstallCardText(item));
    button.classList.add("is-copied");
    button.textContent = "安装卡已生成";
    toast("已生成安装卡；Agent 调用 accept 后会写入原生记忆");
    await loadMyInstalls();
    window.clearTimeout(button._copyTimer);
    button._copyTimer = window.setTimeout(() => {
      button.classList.remove("is-copied");
      button.textContent = originalText;
      button.disabled = false;
    }, 2200);
  } catch (error) {
    button.disabled = false;
    button.textContent = originalText;
    toast(error.message || "生成安装凭证失败");
  }
}

function setupHomeDeck() {
  const deck = $("[data-home-deck]");
  if (!deck) return;
  const pages = $$(".home-deck-page");
  if (!pages.length) return;
  const scrollToPage = (index) => {
    const nextIndex = Math.max(0, Math.min(index, pages.length - 1));
    deck.dataset.homeIndex = String(nextIndex);
    pages[nextIndex]?.scrollIntoView({ behavior: motionAllowed() ? "smooth" : "auto", block: "start" });
  };

  $$(".home-page-jump").forEach((button) => {
    button.addEventListener("click", () => scrollToPage(Number(button.dataset.homePage || 0)));
  });
}

function setupAmbientMotion() {
  if (!motionAllowed() || currentSurface !== "human") return;
  const hero = $(".agent-command-hero");
  if (!hero || hero.dataset.ambientReady) return;
  hero.dataset.ambientReady = "true";
  const field = $(".agent-boundless-field");
  const copy = $(".agent-command-copy");
  const command = $(".agent-command-input");
  const update = window.gsap
    ? {
        fieldX: window.gsap.quickTo(field, "x", { duration: 0.9, ease: "power3.out" }),
        fieldY: window.gsap.quickTo(field, "y", { duration: 0.9, ease: "power3.out" }),
        copyX: window.gsap.quickTo(copy, "x", { duration: 0.7, ease: "power3.out" }),
        copyY: window.gsap.quickTo(copy, "y", { duration: 0.7, ease: "power3.out" }),
        commandX: window.gsap.quickTo(command, "x", { duration: 0.65, ease: "power3.out" }),
        commandY: window.gsap.quickTo(command, "y", { duration: 0.65, ease: "power3.out" }),
      }
    : null;
  const apply = (event) => {
    const rect = hero.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width - 0.5;
    const py = (event.clientY - rect.top) / rect.height - 0.5;
    if (update) {
      update.fieldX(px * 18);
      update.fieldY(py * 14);
      update.copyX(px * 8);
      update.copyY(py * 6);
      update.commandX(px * 10);
      update.commandY(py * 7);
      return;
    }
    if (field) field.style.transform = `translate3d(${px * 18}px, ${py * 14}px, 0)`;
    if (copy) copy.style.transform = `translate3d(${px * 8}px, ${py * 6}px, 0)`;
    if (command) command.style.transform = `translate3d(${px * 10}px, ${py * 7}px, 0)`;
  };
  const reset = () => {
    if (update) {
      update.fieldX(0); update.fieldY(0);
      update.copyX(0); update.copyY(0);
      update.commandX(0); update.commandY(0);
      return;
    }
    [field, copy, command].forEach((element) => {
      if (element) element.style.transform = "";
    });
  };
  hero.addEventListener("pointermove", apply, { passive: true });
  hero.addEventListener("pointerleave", reset);
}

function setupVisibleHomeMotion() {
  if (!motionAllowed() || currentSurface !== "human") return;
  const hero = $(".agent-command-hero");
  if (!hero || hero.dataset.visibleMotionReady) return;
  hero.dataset.visibleMotionReady = "true";

  const animated = [
    $(".agent-command-copy"),
    $(".agent-command-input"),
    $(".agent-command-hint"),
    $(".agent-command-actions"),
  ].filter(Boolean);

  if (window.gsap) {
    const gsap = window.gsap;
    gsap.set(animated, { willChange: "transform, opacity" });
    gsap.timeline({ defaults: { ease: "power3.out", overwrite: "auto" } })
      .from(".memory-core-glow, .memory-orbit", { scale: 0.92, autoAlpha: 0, duration: 0.82, stagger: 0.08 }, 0.02)
      .from(".memory-agent-node, .memory-cloud-node, .memory-context-pack", { y: 12, scale: 0.9, autoAlpha: 0, duration: 0.58, stagger: 0.06 }, 0.14)
      .from(".memory-capsule", { y: 8, scale: 0.86, autoAlpha: 0, duration: 0.42, stagger: 0.04 }, 0.24)
      .from(".agent-command-copy", { y: 24, autoAlpha: 0, duration: 0.72 }, 0.1)
      .from(".agent-command-input", { y: 20, scale: 0.988, autoAlpha: 0, duration: 0.68 }, 0.22)
      .from(".agent-command-hint, .agent-command-actions", { y: 16, autoAlpha: 0, duration: 0.5, stagger: 0.05 }, 0.38);
    gsap.to(".agent-command-input", {
      y: -3,
      duration: 2.6,
      ease: "sine.inOut",
      repeat: -1,
      yoyo: true,
      overwrite: "auto",
    });
    return;
  }

  animated.forEach((element, index) => {
    element.animate(
      [
        { opacity: 0, transform: "translateY(22px) scale(0.98)" },
        { opacity: 1, transform: "translateY(0) scale(1)" },
      ],
      {
        duration: 720,
        delay: index * 38,
        easing: "cubic-bezier(.16, 1, .3, 1)",
        fill: "both",
      },
    );
  });
}

function setupScenarioCommandCopy() {
  $$(".scenario-command[data-command-copy]").forEach((button) => {
    if (button.dataset.copyReady) return;
    button.dataset.copyReady = "true";
    button.addEventListener("click", async () => {
      const prompt = button.dataset.commandCopy || button.textContent.trim();
      try {
        await copyText(prompt);
        button.classList.add("is-copied");
        toast("已复制下面这段，可以直接发给智能体");
        window.clearTimeout(button._copyTimer);
        button._copyTimer = window.setTimeout(() => button.classList.remove("is-copied"), 1800);
      } catch (error) {
        toast("复制失败，请手动复制黑色提示框里的内容");
      }
    });
  });
}

async function request(path, options = {}) {
  const headers = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...authHeader(),
    ...(options.headers || {}),
  };
  const res = await fetch(path, { ...options, headers, credentials: "same-origin" });
  const type = res.headers.get("content-type") || "";
  const data = type.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    throw new Error((data && data.detail) || `HTTP ${res.status}`);
  }
  return data;
}

function setView(view, options = {}) {
  const target = $(`#${view}View`);
  if (!target) return;
  const surface = options.surface || (currentSurface === "agent" && AGENT_ROUTES[view] ? "agent" : "human");
  updateSurfaceChrome(view, surface);
  if (options.updateUrl) {
    const nextRoute = options.route || routeForView(view, surface);
    if (location.pathname !== nextRoute) {
      history.pushState({ view, surface }, "", nextRoute);
    }
  }
  syncActiveNav(view, surface);
  $$(".view").forEach((panel) => panel.classList.remove("active"));
  target.classList.add("active");
  const title = VIEW_TITLES[view] || "记忆云";
  $("#viewTitle").textContent = title;
  if (view === "workspace") loadMine();
  if (view === "adaptive") loadWorkspaces();
  if (view === "memory") loadMemoryConsole();
  if (view === "admin") loadAdmin();
  if (view === "commerce") loadCommerce();
  if (view === "catalog") loadPlazaContent();
  if (options.animate !== false) animateActiveView(view);
  if (view === "workspace" && location.hash) {
    const targetId = location.hash.replace(/^#/, "");
    updateAccountNav(targetId);
    window.setTimeout(() => {
      document.getElementById(targetId)?.scrollIntoView({ behavior: motionAllowed() ? "smooth" : "auto", block: "start" });
    }, 120);
  } else if (view === "workspace") {
    updateAccountNav("account-overview");
  }
}

function initialViewFromLocation() {
  return routeStateFromLocation();
}

function accountLabel() {
  if (state.user) return state.user.username || state.user.handle || "未命名账户";
  if (state.apiKey) return "API Key 访问";
  return "未登录";
}

function accountTypeLabel() {
  if (state.user?.email) return `${state.user.auth_type || "human"} · ${state.user.email}`;
  if (state.user?.auth_type) return state.user.auth_type;
  if (state.apiKey) return "当前页持有一次性 API key";
  return "登录后查看你的记忆包、工作空间和可用 Agent";
}

function setText(selector, value) {
  const element = $(selector);
  if (element) element.textContent = value;
}

function resetAccountCounts() {
  state.accountCounts = {
    memories: null,
    installs: null,
    workspaces: null,
    bindings: null,
    apiKeys: null,
  };
  renderAccountMetrics();
}

function updateAccountCount(key, value) {
  state.accountCounts[key] = Number.isFinite(Number(value)) ? Number(value) : null;
  renderAccountMetrics();
}

function countText(value) {
  return value === null || value === undefined ? "-" : String(value);
}

function renderAccountMetrics() {
  if (!state.user && !state.apiKey) {
    setText("#accountMemoryMetric", "需登录");
    setText("#accountInstallMetric", "需登录");
    setText("#accountSecurityMetric", "登录后可见");
    return;
  }
  const counts = state.accountCounts;
  setText("#accountMemoryMetric", countText(counts.memories));
  setText("#accountInstallMetric", countText(counts.installs));
  setText(
    "#accountSecurityMetric",
    `${countText(counts.workspaces)} 空间 / ${countText(counts.bindings)} 绑定 / ${countText(counts.apiKeys)} Key`,
  );
}

function renderAccountIdentity() {
  const label = accountLabel();
  const typeLabel = accountTypeLabel();
  setText("#accountIdentityName", label);
  setText("#accountIdentityType", typeLabel);
  setText("#accountOverviewUser", label);
  setText("#accountOverviewAuth", typeLabel);
  const avatar = $("#accountIdentityAvatar");
  if (avatar) avatar.textContent = (label || "U").trim().slice(0, 1).toUpperCase();
  const promptPreview = $("#agentBindingPromptPreview");
  if (promptPreview) promptPreview.textContent = agentBindingPromptText();
}

function updateAccountNav(targetId = "account-overview") {
  $$("[data-account-target]").forEach((item) => {
    if (item.closest(".account-submenu")) return;
    item.classList.toggle("is-active", item.dataset.accountTarget === targetId);
  });
}

function renderSession() {
  const el = $("#sessionState");
  const loggedIn = Boolean(state.user || state.apiKey);
  if (state.user) {
    el.textContent = `${state.user.username || state.user.handle} / ${state.user.auth_type}`;
  } else if (state.apiKey) {
    el.textContent = "当前页已持有一次性 API key";
  } else {
    el.textContent = "未登录";
  }
  $("#guestSessionActions")?.classList.toggle("hidden", loggedIn);
  $("#accountMenu")?.classList.toggle("hidden", !loggedIn);
  renderAccountIdentity();
  if (!loggedIn) resetAccountCounts();
}

function showOneTimeKey(apiKey) {
  const box = $("#newKeyBox");
  if (!box || !apiKey) return;
  box.hidden = false;
  box.textContent = `新 API Key（只显示一次，请立即交给你的 Agent 或密钥管理器）：${apiKey}`;
}

function clearOneTimeKey() {
  const box = $("#newKeyBox");
  if (!box) return;
  box.hidden = true;
  box.textContent = "";
}

function surfaceAgentRuntimeNotice(payload) {
  const notice = payload?.runtime_connection_notice || payload?.mandatory_runtime_notice;
  if (!notice || payload?.user?.auth_type !== "agent") return;
  toast("已知智能体：请先刷新 MemoryCloud 启动项和运行时摘要");
}

async function bootstrap() {
  syncPublicUrls();
  $("#agentPrompt").textContent = agentBriefText();
  setupHomeDeck();
  setupScenarioCommandCopy();
  try {
    const status = await request("/api/status");
    const apiStatus = $("#apiStatus");
    apiStatus.classList.toggle("status-ok", Boolean(status.ok));
    apiStatus.classList.toggle("status-error", !status.ok);
    apiStatus.textContent = status.ok ? `服务正常 · ${status.business.public_packages} 个公开记忆` : "服务异常";
  } catch (error) {
    const apiStatus = $("#apiStatus");
    apiStatus.classList.remove("status-ok");
    apiStatus.classList.add("status-error");
    apiStatus.textContent = "服务状态不可用";
  }
  try {
    const data = await request(SESSION_PROBE_ENDPOINT);
    state.user = data.authenticated ? data.user : null;
    surfaceAgentRuntimeNotice(data);
  } catch (error) {
    state.user = null;
  }
  renderSession();
  setupMotionEffects();
  const initialRoute = initialViewFromLocation();
  setView(initialRoute.view, { surface: initialRoute.surface, updateUrl: false, animate: initialRoute.view !== "catalog" });
  if (initialRoute.view === "catalog") {
    animateStorefrontIntro();
  }
}

function packageCard(item) {
  const tags = item.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
  const personaType = escapeHtml(item.persona_type || "agent");
  const personaLabel = {
    agent: "智能体工作记忆",
    book_distill: "知识提炼记忆",
    person_distill: "经验方法记忆",
    roleplay: "表达风格记忆",
    method_distill: "开源方法记忆",
  }[item.persona_type] || "开源记忆";
  const version = escapeHtml(item.version || "0.0.0");
  return `
    <article class="package-card">
      <div class="product-cover ${personaType}">
        <span class="cover-type">${escapeHtml(personaLabel)}</span>
        <strong class="cover-title">${escapeHtml(item.title)}</strong>
        <span class="cover-version">v${version}</span>
      </div>
      <div class="package-body">
        <div class="package-topline">
          <span>${escapeHtml(personaLabel)}</span>
          <span>v${version}</span>
        </div>
        <div>
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.summary)}</p>
        </div>
        <div class="tag-list">${tags}</div>
        <div class="package-meta">
          <span>${escapeHtml(item.owner.username || item.owner.handle)}</span>
          <span>下载 ${item.download_count}</span>
          <span>安装 ${item.install_count}</span>
        </div>
        <div class="price-row install-card-summary">
          <strong>开源记忆接力卡</strong>
          <span>安装需登录，详情公开可看</span>
        </div>
        <div class="card-actions">
          <button class="button secondary" data-detail="${escapeHtml(item.slug)}" type="button">查看详情</button>
          <button
            class="button primary"
            data-install-memory="${escapeHtml(item.slug)}"
            data-install-title="${escapeHtml(item.title)}"
            data-install-version="${escapeHtml(item.version || "latest")}"
            data-install-license="${escapeHtml(item.license || "unspecified")}"
            data-install-tags="${escapeHtml((item.tags || []).join(", "))}"
            type="button"
          >安装</button>
        </div>
      </div>
    </article>
  `;
}

async function loadCatalog() {
  state.catalogLoaded = true;
  const list = $("#catalogList");
  if (list) {
    list.innerHTML = `<div class="package-card plaza-loading-card"><h3>正在加载开源记忆包</h3><p>稍等片刻，系统会自动显示可发给 Agent 安装的方法记忆。</p></div>`;
  }
  const q = encodeURIComponent($("#searchInput").value.trim());
  const tagValue = $("#tagInput").value.trim() || "open-memory";
  const tag = encodeURIComponent(tagValue);
  try {
    const data = await request(`/api/catalog?q=${q}&tag=${tag}`);
    const catalogCount = $("#catalogCount");
    if (catalogCount) catalogCount.textContent = data.items.length;
    $("#catalogList").innerHTML = data.items.length
      ? data.items.map(packageCard).join("")
      : `<div class="package-card"><h3>暂无公开开源记忆</h3><p>可以上传整理好的 MEMORY.md，或导入符合平台规则的记忆归档。</p></div>`;
    animateCatalogCards();
    setupCardMotion();
    setupRevealMotion("#catalogList .package-card");
  } catch (error) {
    const catalogCount = $("#catalogCount");
    if (catalogCount) catalogCount.textContent = "!";
    $("#catalogList").innerHTML = `<div class="package-card error-card"><h3>目录暂时不可用</h3><p>${escapeHtml(error.message)}。请稍后重试，或打开 /api/status 查看服务状态。</p><div class="card-actions"><a class="button secondary" href="/api/status" target="_blank" rel="noreferrer">服务状态</a></div></div>`;
  }
}

function personaSourceCard(item) {
  const statusLabel = {
    installed: "已安装",
    research_only: "研究来源",
    pending: "待接入",
  }[item.status] || item.status;
  const repo = item.repository
    ? `<a class="mini-button" href="${escapeHtml(item.repository)}" target="_blank" rel="noreferrer">GitHub</a>`
    : `<span class="mini-button muted">待确认</span>`;
  return `
    <article class="persona-source-card">
      <div class="persona-source-top">
        <span>${escapeHtml(statusLabel)}</span>
        <code>${escapeHtml(item.installed_skill || item.id)}</code>
      </div>
      <h4>${escapeHtml(item.name)}</h4>
      <p>${escapeHtml(item.summary)}</p>
      <strong>${escapeHtml(item.best_use)}</strong>
      <div class="card-actions">${repo}</div>
    </article>
  `;
}

async function loadPersonaSources() {
  state.personaSourcesLoaded = true;
  const market = $("#personaMarketGrid");
  const methods = $("#personaMethodGrid");
  if (!market || !methods) return;
  try {
    const data = await request("/api/persona/sources");
    const marketItems = (data.groups.market || []).slice(0, 4);
    const methodItems = (data.groups.methods || []).slice(0, 4);
    market.innerHTML = marketItems.length
      ? marketItems.map(personaSourceCard).join("")
      : `<div class="empty-line">暂无可接入的思想记忆来源</div>`;
    methods.innerHTML = methodItems.length
      ? methodItems.map(personaSourceCard).join("")
      : `<div class="empty-line">暂无可用的记忆蒸馏方法来源</div>`;
    setupRevealMotion(".persona-source-card, .persona-workbench");
  } catch (error) {
    market.innerHTML = `<div class="error-card package-card"><h3>思想记忆来源暂时不可用</h3><p>${escapeHtml(error.message)}</p></div>`;
    methods.innerHTML = "";
  }
}

function loadPlazaContent() {
  if (!state.catalogLoaded) loadCatalog();
  if (!state.personaSourcesLoaded) loadPersonaSources();
}

async function submitPersonaDistill(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const fd = new FormData(form);
  const hasText = String(fd.get("source_text") || "").trim().length > 0;
  const hasFile = Array.from(form.querySelector("[name='files']")?.files || []).length > 0;
  if (!hasText && !hasFile) {
    toast("请先粘贴资料或上传文件");
    return;
  }
  const button = event.submitter;
  if (button) button.disabled = true;
  try {
    const data = await request("/api/persona/distill-jobs", {
      method: "POST",
      body: fd,
    });
    const job = data.job;
    $("#personaDistillResult").innerHTML = `
      <article class="persona-result-card">
        <span>任务已创建</span>
        <h4>${escapeHtml(job.target_name)}</h4>
        <p>状态：${escapeHtml(job.status)} · 文件 ${escapeHtml(job.input_manifest.files?.length || 0)} 个 · 文本 ${escapeHtml(job.input_manifest.text_chars || 0)} 字符</p>
        <div class="persona-isolation">
          <strong>数据隔离</strong><small>${escapeHtml(job.isolation.raw_source_visibility)} / ${escapeHtml(job.isolation.search_index)}</small>
          <strong>推理隔离</strong><small>${escapeHtml(job.inference_policy.execution_boundary)} / ${escapeHtml(job.inference_policy.cross_tenant_memory)}</small>
        </div>
        <pre>${escapeHtml(JSON.stringify(job.result.memory_suite_draft, null, 2))}</pre>
      </article>
    `;
    toast("已创建私有记忆蒸馏任务");
  } catch (error) {
    $("#personaDistillResult").textContent = error.message;
    toast(error.message);
  } finally {
    if (button) button.disabled = false;
  }
}

async function showDetail(slug) {
  try {
    const [item, versions] = await Promise.all([
      request(`/api/catalog/${encodeURIComponent(slug)}`),
      request(`/api/catalog/${encodeURIComponent(slug)}/versions`),
    ]);
    $("#detailTitle").textContent = item.title;
    $("#detailMeta").innerHTML = [
      `<span>${escapeHtml(item.persona_type)}</span>`,
      `<span>${escapeHtml(item.visibility)}</span>`,
      `<span>${escapeHtml(item.license)}</span>`,
      `<span>v${escapeHtml(item.version)}</span>`,
      `<span>${escapeHtml(item.owner.username || item.owner.handle)}</span>`,
    ].join("");
    $("#detailRisk").innerHTML = `
      <strong>安装风险：${escapeHtml(item.risk?.level || "medium")}</strong>
      <p>${escapeHtml(item.risk?.install_boundary || "Installed memory is context, not identity proof.")}</p>
      <div class="card-actions">
        <button
          class="button primary"
          data-install-memory="${escapeHtml(item.slug)}"
          data-install-title="${escapeHtml(item.title)}"
          data-install-version="${escapeHtml(item.version || "latest")}"
          data-install-license="${escapeHtml(item.license || "unspecified")}"
          data-install-tags="${escapeHtml((item.tags || []).join(", "))}"
          type="button"
        >安装</button>
      </div>
    `;
    $("#detailVersions").innerHTML = versions.items.length
      ? versions.items
          .map((version) =>
            adminRow([
              `<b>v${escapeHtml(version.version)}</b><small>${escapeHtml(version.id)}</small>`,
              `<span>${escapeHtml(version.changelog || "no changelog")}</span>`,
              `<span>${escapeHtml(version.size_bytes)} bytes</span>`,
              `<span>${escapeHtml(version.created_at)}</span>`,
            ]),
          )
          .join("")
      : `<div class="empty-line">暂无版本</div>`;
    $("#detailPreview").textContent = [
      "# MEMORY preview",
      item.preview.memory_md,
      "",
      "# DREAMS preview",
      item.preview.dreams_md,
    ].join("\n");
    $("#detailDialog").showModal();
  } catch (error) {
    toast(error.message);
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function publishPayload(form) {
  const fd = new FormData(form);
  let provenance = {};
  try {
    provenance = JSON.parse(fd.get("provenance") || "{}");
  } catch (error) {
    throw new Error("来源说明必须是 JSON");
  }
  return {
    title: fd.get("title"),
    summary: fd.get("summary"),
    persona_type: fd.get("persona_type"),
    visibility: fd.get("visibility"),
    license: fd.get("license"),
    tags: String(fd.get("tags") || "").split(",").map((item) => item.trim()).filter(Boolean),
    version: fd.get("version"),
    memory_md: fd.get("memory_md"),
    dreams_md: fd.get("dreams_md"),
    provenance,
  };
}

async function publishMemory(event) {
  event.preventDefault();
  const button = event.submitter;
  button.disabled = true;
  try {
    const data = await request("/api/memories", {
      method: "POST",
      body: JSON.stringify(publishPayload(event.currentTarget)),
    });
    toast(`已发布：${data.package.slug}`);
    setView("workspace");
    await loadCatalog();
  } catch (error) {
    toast(error.message);
  } finally {
    button.disabled = false;
  }
}

async function validatePublish() {
  try {
    const payload = publishPayload($("#publishForm"));
    const data = await request("/api/memories/validate", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    toast(`校验通过 · ${data.size_bytes} bytes · ${data.warnings.length} 个提醒`);
  } catch (error) {
    toast(error.message);
  }
}

async function importMemory(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  if (!fd.get("file") || !fd.get("file").name) {
    toast("请选择 zip 文件");
    return;
  }
  const button = event.submitter;
  button.disabled = true;
  try {
    const visibility = encodeURIComponent(fd.get("visibility") || "public");
    const upload = new FormData();
    upload.append("file", fd.get("file"));
    const data = await request(`/api/memories/import?visibility=${visibility}`, {
      method: "POST",
      body: upload,
    });
    toast(`已导入：${data.package.slug}`);
    await loadCatalog();
  } catch (error) {
    toast(error.message);
  } finally {
    button.disabled = false;
  }
}

async function validateImport() {
  const form = $("#importForm");
  const fd = new FormData(form);
  if (!fd.get("file") || !fd.get("file").name) {
    toast("请选择 zip 文件");
    return;
  }
  const upload = new FormData();
  upload.append("file", fd.get("file"));
  try {
    const data = await request("/api/memories/import/validate", {
      method: "POST",
      body: upload,
    });
    toast(`zip 校验通过 · ${data.size_bytes} bytes · ${data.sha256.slice(0, 12)}...`);
  } catch (error) {
    toast(error.message);
  }
}

async function loadMine() {
  const target = $("#mineList");
  if (!state.user && !state.apiKey) {
    target.innerHTML = `<div class="package-row"><h4>需要登录</h4><p>登录、注册或使用 Agent 注册后，就可以查看和维护自己的开源记忆与私有记忆。</p></div>`;
    $("#installList").innerHTML = `<div class="empty-line">登录后查看已安装的开源记忆</div>`;
    $("#accountWorkspaceList").innerHTML = `<div class="empty-line">登录后查看工作空间</div>`;
    $("#apiKeyList").innerHTML = `<div class="empty-line">登录后管理 API Key</div>`;
    $("#agentBindingList").innerHTML = `<div class="empty-line">登录后查看已连接 Agent</div>`;
    $("#agentBindingRequests").innerHTML = "";
    renderAgentBindingStatus([], [], false);
    updateAgentBindingLayout([], [], false);
    resetAccountCounts();
    return;
  }
  try {
    const data = await request("/api/me/memories");
    updateAccountCount("memories", data.items.length);
    target.innerHTML = data.items.length
      ? data.items
          .map(
            (item) => `
            <article class="package-row">
              <h4>${escapeHtml(item.title)}</h4>
              <p>标识：${escapeHtml(item.slug)} · v${escapeHtml(item.version)} · ${escapeHtml(item.visibility)}</p>
              <div class="card-actions">
                <button class="button secondary" data-detail="${escapeHtml(item.slug)}" type="button">查看详情</button>
                <button
                  class="button primary"
                  data-install-memory="${escapeHtml(item.slug)}"
                  data-install-title="${escapeHtml(item.title)}"
                  data-install-version="${escapeHtml(item.version || "latest")}"
                  data-install-license="${escapeHtml(item.license || "unspecified")}"
                  data-install-tags="${escapeHtml((item.tags || []).join(", "))}"
                  type="button"
                >安装</button>
                <button class="button secondary" data-archive-memory="${escapeHtml(item.slug)}" type="button">归档</button>
                <button class="button secondary danger" data-delete-memory="${escapeHtml(item.slug)}" type="button">删除</button>
              </div>
            </article>
          `,
          )
          .join("")
      : `<div class="package-row"><h4>还没有记忆</h4><p>去上传页创建第一份包含长期记忆和安装工具的开源记忆。</p></div>`;
    await Promise.all([loadApiKeys(), loadAgentBindings(), loadMyInstalls(), loadAccountWorkspaces()]);
  } catch (error) {
    updateAccountCount("memories", null);
    target.innerHTML = `<div class="package-row"><h4>加载失败</h4><p>${escapeHtml(error.message)}</p></div>`;
  }
}

async function loadMyInstalls() {
  const list = $("#installList");
  if (!list) return;
  if (!state.user && !state.apiKey) {
    list.innerHTML = `<div class="empty-line">登录后查看已安装的开源记忆</div>`;
    updateAccountCount("installs", null);
    return;
  }
  try {
    const data = await request("/api/me/installs");
    const pending = data.pending_links || [];
    const installed = data.items || [];
    updateAccountCount("installs", pending.length + installed.length);
    const pendingHtml = pending.length
      ? pending
          .map(
            (item) => `
              <article class="package-row">
                <h4>${escapeHtml(item.source_title)}</h4>
                <p>安装卡：${escapeHtml(item.status)} · 已领取 ${escapeHtml(item.use_count)}/${escapeHtml(item.max_uses)} · 过期 ${escapeHtml(item.expires_at)}</p>
                <div class="card-actions">
                  <a class="button secondary link-button" href="/agent/memory-install/${encodeURIComponent(item.source_slug)}" target="_blank" rel="noreferrer">Agent 安装说明</a>
                  <button class="button secondary" data-detail="${escapeHtml(item.source_slug)}" type="button">查看来源</button>
                </div>
              </article>
            `,
          )
          .join("")
      : "";
    const installedHtml = installed.length
      ? installed
          .map(
            (item) => `
              <article class="package-row">
                <h4>${escapeHtml(item.source_title)}</h4>
                <p>来源：${escapeHtml(item.source_slug)} · v${escapeHtml(item.source_version)} · ${escapeHtml(item.status)} · ${escapeHtml(item.workspace_name || item.target_workspace_id)}</p>
                <p>原生记忆：${escapeHtml(item.native_memory_id || "已接入 workspace")} · 私有副本：${escapeHtml(item.copied_slug || "等待复制")} · 回执：${escapeHtml(item.receipt_id || "无")}</p>
                <div class="card-actions">
                  ${item.copied_slug ? `<button class="button secondary" data-detail="${escapeHtml(item.copied_slug)}" type="button">查看副本</button>` : ""}
                  <a class="button secondary link-button" href="/agent/memory-install/${encodeURIComponent(item.source_slug)}" target="_blank" rel="noreferrer">Agent 安装说明</a>
                </div>
              </article>
            `,
          )
          .join("")
      : "";
    list.innerHTML = pendingHtml || installedHtml
      ? `${pendingHtml}${installedHtml}`
      : `<div class="empty-line">还没有安装记录。在开源广场点击“安装”后会出现在这里。</div>`;
  } catch (error) {
    updateAccountCount("installs", null);
    list.innerHTML = `<div class="empty-line">安装记录加载失败：${escapeHtml(error.message)}</div>`;
  }
}

async function loadApiKeys() {
  try {
    const data = await request("/api/me/api-keys");
    updateAccountCount("apiKeys", (data.items || []).filter((item) => !item.revoked_at).length);
    $("#apiKeyList").innerHTML = data.items.length
      ? data.items
          .map((item) =>
            adminRow([
              `<b>${escapeHtml(item.name)}</b><small>${escapeHtml(item.prefix)}</small>`,
              `<span>${escapeHtml((item.scopes || []).join(", "))}</span>`,
              `<span>${item.revoked_at ? "已撤销" : escapeHtml(item.last_used_at || "未使用")}</span>`,
              item.revoked_at
                ? `<span></span>`
                : `<button class="mini-button" data-revoke-key="${escapeHtml(item.id)}" type="button">撤销</button>`,
            ]),
          )
          .join("")
      : `<div class="empty-line">暂无 API Key</div>`;
  } catch (error) {
    updateAccountCount("apiKeys", null);
    $("#apiKeyList").innerHTML = `<div class="empty-line">API Key 加载失败：${escapeHtml(error.message)}</div>`;
  }
}

function bindingStatusLabel(status) {
  return {
    active: "已绑定",
    revoked: "已撤销",
    pending: "待确认",
    approved: "已确认",
    rejected: "已拒绝",
    expired: "已过期",
  }[status] || status;
}

function renderAgentBindingStatus(bindings, pending, isAgent) {
  const card = $("#agentBindingStatus");
  if (!card) return;
  const activeCount = bindings.filter((item) => item.status === "active").length;
  if (!state.user && !state.apiKey) {
    card.innerHTML = `<strong>未登录</strong><span>登录后查看已连接 Agent。</span>`;
    return;
  }
  if (pending.length) {
    card.innerHTML = `
      <strong>需要确认 ${pending.length} 个请求</strong>
      <span>确认你认识这个 Agent，再去邮箱或短信完成验证。</span>
    `;
    return;
  }
  if (activeCount) {
    card.innerHTML = `
      <strong>已连接 ${activeCount} 个 Agent</strong>
      <span>可以查看它们能读哪些记忆，也可以随时撤销。</span>
    `;
    return;
  }
  card.innerHTML = `
    <strong>${isAgent ? "还没连接用户" : "还没有连接 Agent"}</strong>
    <span>${isAgent ? "请让用户提供注册联系方式，然后发起绑定。" : "需要时展开“绑定新 Agent”，复制一句话发给它。"}</span>
  `;
}

function updateAgentBindingLayout(bindings, pending, isAgent) {
  const activeBlock = $("#agentBindingActiveBlock");
  const requestsBlock = $("#agentBindingRequestsBlock");
  const setup = $("#agentBindingSetup");
  const count = $("#agentBindingCountSummary");
  const activeCount = bindings.filter((item) => item.status === "active").length;
  const loggedIn = Boolean(state.user || state.apiKey);

  if (count) count.textContent = loggedIn ? `${activeCount} 个` : "-";
  if (activeBlock) activeBlock.hidden = !loggedIn;
  if (requestsBlock) requestsBlock.hidden = !loggedIn || !pending.length;
  if (setup) {
    setup.hidden = !loggedIn;
    setup.open = loggedIn && !activeCount && !pending.length && !isAgent;
  }
}

function renderBindingScopeText(scopes = []) {
  if (!scopes.length) return "未申请额外权限";
  return scopes
    .map((scope) => {
      const labels = {
        "memory:read": "读记忆",
        "memory:write": "写记忆",
        "skill:install": "安装 Skill",
        "handoff:delegate": "创建交接",
      };
      return labels[scope] || scope;
    })
    .join("、");
}

function workspaceRoleSummary(workspaceRoles = {}) {
  const entries = Object.entries(workspaceRoles);
  if (!entries.length) return "未绑定工作空间";
  return entries.map(([workspaceId, role]) => `${workspaceId}: ${role}`).join("；");
}

function renderAgentBindingCard(binding, isAgent) {
  const agentName = isAgent
    ? binding.owner?.username || binding.owner?.handle || "用户"
    : binding.agent?.username || binding.agent?.handle || binding.agent_handle || binding.agent_id;
  const active = binding.status === "active";
  const agentId = binding.agent_id || binding.agent?.id || "";
  const workspaceRoles = Object.keys(binding.workspace_roles || {});
  return `
    <article class="binding-agent-card ${active ? "is-active" : ""}" data-agent-card="${escapeHtml(agentId)}">
      <div class="binding-agent-summary">
        <div class="binding-agent-main">
          <span class="binding-agent-avatar" aria-hidden="true">${escapeHtml(String(agentName || "A").slice(0, 1).toUpperCase())}</span>
          <div>
            <strong>${escapeHtml(agentName)}</strong>
            <p>${escapeHtml(renderBindingScopeText(binding.scopes || []))}</p>
            <small>${workspaceRoles.length ? `${workspaceRoles.length} 个工程空间` : "还没有工程权限"}</small>
          </div>
        </div>
        <div class="binding-agent-metrics" aria-label="Agent 访问概览">
          <span><b>${workspaceRoles.length}</b>工程</span>
          <span><b>${(binding.scopes || []).length}</b>权限</span>
        </div>
        <div class="binding-next-actions">
          ${!isAgent && active ? `<button class="button primary" data-agent-dashboard="${escapeHtml(agentId)}" type="button">查看工作台</button>` : ""}
          ${!isAgent && active ? `<button class="button secondary view-action" data-view="memory" data-agent-memory-open="${escapeHtml(agentId)}" type="button">完整工程记忆</button>` : ""}
          ${active && !isAgent ? `<button class="button secondary danger" data-revoke-agent-binding="${escapeHtml(binding.id)}" type="button">撤销</button>` : ""}
        </div>
      </div>
      <div class="agent-workbench" id="agentWorkbench-${escapeHtml(agentId)}" hidden></div>
    </article>
  `;
}

function renderWorkbenchList(items, emptyText, itemRenderer) {
  return items.length ? items.map(itemRenderer).join("") : `<div class="empty-line">${escapeHtml(emptyText)}</div>`;
}

function renderAgentWorkbench(data) {
  const summary = data.dashboard_summary || {};
  const workspaces = data.workspaces || [];
  const memories = data.readable_assets || [];
  const tree = data.memory_tree || [];
  const projects = data.projects || [];
  return `
    <div class="agent-workbench-head">
      <div>
        <span>Agent 工作台</span>
        <strong>${escapeHtml(data.agent?.username || data.agent?.handle || "Agent")}</strong>
      </div>
      <div class="agent-workbench-stats">
        <span><b>${Number(summary.workspace_count || 0)}</b>工程</span>
        <span><b>${Number(summary.readable_count || 0)}</b>可读记忆</span>
        <span><b>${Number(summary.tree_node_count || 0)}</b>树节点</span>
      </div>
    </div>
    <div class="agent-workbench-grid">
      <section class="agent-workbench-panel">
        <h5>工程</h5>
        ${renderWorkbenchList(workspaces, "这个 Agent 还没有工程权限。", (item) => `
          <button class="agent-workspace-row" type="button" data-agent-workspace-open="${escapeHtml(item.id)}">
            <strong>${escapeHtml(item.name)}</strong>
            <span>${escapeHtml(item.role)} · ${Number(item.readable_assets || 0)} 条记忆 · ${Number(item.project_count || 0)} 棵树</span>
          </button>
        `)}
      </section>
      <section class="agent-workbench-panel">
        <h5>可读记忆</h5>
        ${renderWorkbenchList(memories.slice(0, 8), "这个 Agent 当前没有可读记忆。", (item) => `
          <button class="agent-memory-row" type="button" data-agent-memory-asset="${escapeHtml(item.id)}">
            <span>${escapeHtml(item.type_label || memoryLensKindLabel(item.kind))}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <small>${escapeHtml(item.workspace_name || "")}</small>
          </button>
        `)}
      </section>
      <section class="agent-workbench-panel">
        <h5>项目树</h5>
        ${renderWorkbenchList(tree.slice(0, 8), projects.length ? "这棵树还没有节点。" : "还没有项目树。", (item) => `
          <button class="agent-tree-row status-${escapeHtml(item.status)}" type="button" data-agent-graph-open="${escapeHtml(item.graph_id)}">
            <span>${escapeHtml(MEMORY_NODE_LABELS[item.node_type] || item.node_type || "节点")}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <small>${escapeHtml(item.graph_title || item.project_key || "")}</small>
          </button>
        `)}
      </section>
    </div>
  `;
}

async function openAgentWorkbench(agentId) {
  if (!agentId) return;
  const box = $$(".agent-workbench").find((item) => item.id === `agentWorkbench-${agentId}`);
  if (!box) return;
  const isSame = state.agentDashboard.selectedId === agentId && !box.hidden;
  $$(".agent-workbench").forEach((item) => {
    item.hidden = true;
  });
  $$("[data-agent-card]").forEach((item) => {
    item.classList.toggle("is-expanded", item.dataset.agentCard === agentId && !isSame);
  });
  if (isSame) {
    state.agentDashboard.selectedId = "";
    return;
  }
  state.agentDashboard.selectedId = agentId;
  box.hidden = false;
  box.innerHTML = `<div class="empty-line">正在加载 Agent 工程和记忆...</div>`;
  try {
    const data = state.agentDashboard.cache[agentId] || await request(`/api/agents/${encodeURIComponent(agentId)}/workspace-dashboard`);
    state.agentDashboard.cache[agentId] = data;
    box.innerHTML = renderAgentWorkbench(data);
  } catch (error) {
    box.innerHTML = `<div class="empty-line">Agent 工作台加载失败：${escapeHtml(error.message)}</div>`;
  }
}

function openAgentFullMemoryView(agentId) {
  state.memory.selectedAgentId = agentId || "";
  setView("memory");
  window.setTimeout(async () => {
    const select = $("#memoryAgentSelect");
    if (select && agentId) {
      select.value = agentId;
      await loadMemoryAgentView(agentId);
    }
  }, 0);
}

function renderAgentBindingRequestCard(item, isAgent) {
  const name = isAgent ? item.contact_masked : item.agent?.username || item.agent?.handle || item.agent_id;
  return `
    <article class="binding-request-card">
      <div>
        <strong>${escapeHtml(name)}</strong>
        <p>${escapeHtml(bindingStatusLabel(item.status))} · ${escapeHtml(renderBindingScopeText(item.requested_scopes || []))}</p>
        <small>联系通道：${escapeHtml(item.contact_masked || item.contact_type)} · 过期：${escapeHtml(item.expires_at || "")}</small>
      </div>
      <span>${escapeHtml(workspaceRoleSummary(item.workspace_roles || {}))}</span>
    </article>
  `;
}

async function loadAgentBindings() {
  const list = $("#agentBindingList");
  const requests = $("#agentBindingRequests");
  if (!list || !requests) return;
  if (!state.user && !state.apiKey) {
    list.innerHTML = `<div class="empty-line">登录后查看已连接 Agent</div>`;
    requests.innerHTML = "";
    renderAgentBindingStatus([], [], false);
    updateAgentBindingLayout([], [], false);
    updateAccountCount("bindings", null);
    return;
  }
  try {
    const isAgent = state.user?.auth_type === "agent";
    const data = await request(isAgent ? "/api/agent/bindings/me" : "/api/me/agent-bindings");
    const bindings = (data.bindings || []).filter((item) => item.status === "active");
    const pendingForCount = isAgent ? data.pending_requests || [] : (data.requests || []).filter((item) => item.status === "pending");
    updateAccountCount("bindings", bindings.length + pendingForCount.length);
    renderAgentBindingStatus(bindings, pendingForCount, isAgent);
    updateAgentBindingLayout(bindings, pendingForCount, isAgent);
    list.innerHTML = bindings.length
      ? bindings
          .map((binding) => renderAgentBindingCard(binding, isAgent))
          .join("")
      : `<div class="empty-line">${isAgent ? "当前 Agent 还没有连接到用户" : "还没有已连接 Agent"}</div>`;
    const pending = pendingForCount;
    requests.innerHTML = pending.length
      ? pending
          .map((item) => renderAgentBindingRequestCard(item, isAgent))
          .join("")
      : "";
  } catch (error) {
    updateAccountCount("bindings", null);
    renderAgentBindingStatus([], [], false);
    updateAgentBindingLayout([], [], false);
    list.innerHTML = `<div class="empty-line">绑定加载失败：${escapeHtml(error.message)}</div>`;
    requests.innerHTML = "";
  }
}

async function revokeAgentBinding(bindingId) {
  if (!window.confirm("确定撤销这个智能体绑定？撤销后它不能继续使用这条绑定关系。")) return;
  try {
    await request(`/api/me/agent-bindings/${encodeURIComponent(bindingId)}`, { method: "DELETE" });
    toast("已撤销智能体绑定");
    await loadAgentBindings();
  } catch (error) {
    toast(error.message);
  }
}

async function createApiKey() {
  const name = window.prompt("Key 名称", "automation");
  if (!name) return;
  const scopeText = window.prompt(
    "Scopes（逗号分隔）",
    "catalog:read,memory:read,memory:write,package:publish,agent:sync,key:manage",
  );
  if (scopeText === null) return;
  const scopes = scopeText
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  try {
    const data = await request("/api/me/api-keys", {
      method: "POST",
      body: JSON.stringify({ name, scopes }),
    });
    showOneTimeKey(data.api_key);
    await loadApiKeys();
  } catch (error) {
    toast(error.message);
  }
}

async function revokeAllApiKeys() {
  if (!window.confirm("确定撤销当前用户全部 API Key？浏览器 Cookie 会话不受影响。")) return;
  try {
    const data = await request("/api/me/api-keys", { method: "DELETE" });
    toast(`已撤销 ${data.revoked} 个 Key`);
    state.apiKey = "";
    await loadApiKeys();
    renderSession();
  } catch (error) {
    toast(error.message);
  }
}

async function loadWorkspaces() {
  const list = $("#workspaceList");
  if (!state.user && !state.apiKey) {
    if (list) list.innerHTML = `<div class="empty-line">登录、注册或使用 Agent 注册后管理工作空间。</div>`;
    return;
  }
  try {
    const data = await request("/api/me/workspaces");
    const first = data.items[0];
    if (first && !$("#adaptiveQueryWorkspace").value) {
      selectAdaptiveWorkspace(first.id);
    }
    if (list) {
      list.innerHTML = data.items.length
        ? data.items
            .map(
              (item) => `
                <article class="workspace-card">
                  <div>
                    <strong>${escapeHtml(item.name)}</strong>
                    <span>${escapeHtml(item.id)} · ${escapeHtml(item.role)} · ${escapeHtml(item.visibility)}</span>
                  </div>
                  <button class="mini-button" data-use-workspace="${escapeHtml(item.id)}" type="button">使用</button>
                </article>
              `,
            )
            .join("")
        : `<div class="empty-line">暂无工作空间。描述任务后会自动创建个人工作空间，也可以在这里手动创建。</div>`;
    }
  } catch (error) {
    if (list) list.innerHTML = `<div class="empty-line">工作空间加载失败：${escapeHtml(error.message)}</div>`;
  }
}

async function loadAccountWorkspaces() {
  const list = $("#accountWorkspaceList");
  if (!list) return;
  if (!state.user && !state.apiKey) {
    list.innerHTML = `<div class="empty-line">登录后查看工作空间</div>`;
    updateAccountCount("workspaces", null);
    return;
  }
  try {
    const data = await request("/api/me/workspaces");
    updateAccountCount("workspaces", data.items.length);
    list.innerHTML = data.items.length
      ? data.items
          .map(
            (item) => `
              <article class="workspace-card">
                <div>
                  <strong>${escapeHtml(item.name)}</strong>
                  <span>${escapeHtml(item.id)} · ${escapeHtml(item.role)} · ${escapeHtml(item.visibility)}</span>
                </div>
                <button class="mini-button view-action" data-view="adaptive" type="button">管理</button>
              </article>
            `,
          )
          .join("")
      : `<div class="empty-line">暂无工作空间。进入团队记忆后可以创建。</div>`;
  } catch (error) {
    updateAccountCount("workspaces", null);
    list.innerHTML = `<div class="empty-line">工作空间加载失败：${escapeHtml(error.message)}</div>`;
  }
}

function selectAdaptiveWorkspace(workspaceId) {
  $("#adaptiveQueryWorkspace").value = workspaceId;
  $("#adaptiveRouteForm [name='workspace_id']").value = workspaceId;
  $("#memberWorkspaceId").value = workspaceId;
  const handoffWorkspace = $("#handoffWorkspaceId");
  if (handoffWorkspace) handoffWorkspace.value = workspaceId;
  const memoryWorkspace = $("#memoryWorkspaceId");
  if (memoryWorkspace && !memoryWorkspace.value) {
    memoryWorkspace.value = workspaceId;
    state.memory.workspaceId = workspaceId;
  }
}

async function createWorkspace(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  try {
    const data = await request("/api/workspaces", {
      method: "POST",
      body: JSON.stringify({
        name: fd.get("name"),
        description: fd.get("description"),
        visibility: fd.get("visibility"),
      }),
    });
    selectAdaptiveWorkspace(data.workspace.id);
    toast(`工作空间已创建：${data.workspace.name}`);
    await loadWorkspaces();
  } catch (error) {
    toast(error.message);
  }
}

async function addWorkspaceMember(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  const workspaceId = String(fd.get("workspace_id") || "").trim();
  if (!workspaceId) {
    toast("需要工作空间 ID");
    return;
  }
  try {
    const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/members`, {
      method: "POST",
      body: JSON.stringify({ handle: fd.get("handle"), role: fd.get("role") }),
    });
    toast(`已添加 ${data.member.handle} 为 ${data.member.role}`);
    await loadWorkspaces();
  } catch (error) {
    toast(error.message);
  }
}

async function createProjectHandoff(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  const workspaceId = String(fd.get("workspace_id") || "").trim();
  if (!workspaceId) {
    toast("需要工作空间 ID");
    return;
  }
  try {
    const receiverHandle = String(fd.get("receiver_handle") || "").trim();
    const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/delegated-handoffs`, {
      method: "POST",
      body: JSON.stringify({
        title: fd.get("title"),
        project_key: fd.get("project_key"),
        summary: fd.get("title"),
        instructions: fd.get("instructions"),
        role: fd.get("role"),
        ttl_hours: Number(fd.get("ttl_hours") || 72),
        max_uses: Number(fd.get("max_uses") || 1),
        receiver: receiverHandle ? { type: "handle", handle: receiverHandle } : { type: "any" },
        require_claim_secret: Boolean(fd.get("require_claim_secret")),
        delegation_reason: fd.get("delegation_reason"),
      }),
    });
    $("#handoffResult").textContent = data.credential_card || data.paste_card;
    toast("预授权交接凭证已生成");
  } catch (error) {
    $("#handoffResult").textContent = error.message;
    toast(error.message);
  }
}

function examplePayload(memoryType) {
  if (memoryType === "code_memory") {
    return {
      project: "demo-memory-project",
      task: "实现自适应记忆路由",
      files_changed: [{ path: "app/main.py", symbols: ["route_memory"], behavior: "新增记忆路由接口" }],
      api_contracts: [{ method: "POST", path: "/api/memory/router/select", auth: "memory:write", effect: "选择模板" }],
      tests: ["pytest -q"],
      risks: ["模型不可用时使用规则兜底"],
      retrieval_triggers: ["adaptive memory", "code memory"],
    };
  }
  return { retrieval_triggers: ["future related tasks"] };
}

async function routeAdaptiveMemory(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  let environment = {};
  try {
    environment = JSON.parse(fd.get("environment") || "{}");
  } catch (error) {
    toast("运行环境必须是 JSON");
    return;
  }
  try {
    const data = await request("/api/memory/router/select", {
      method: "POST",
      body: JSON.stringify({
        workspace_id: fd.get("workspace_id") || null,
        project_key: fd.get("project_key") || null,
        task: fd.get("task"),
        what_i_remember: fd.get("what_i_remember"),
        environment,
      }),
    });
    $("#adaptiveSelected").innerHTML = `<strong>${escapeHtml(data.form_schema.label)} · ${escapeHtml(data.selected_memory_type)}</strong><p>${escapeHtml(data.reason)}</p>`;
    $("#adaptiveSubmitForm [name='run_id']").value = data.run_id;
    selectAdaptiveWorkspace(data.workspace.id);
    $("#adaptiveSubmitForm [name='payload']").value = JSON.stringify(examplePayload(data.selected_memory_type), null, 2);
    toast("已选择记忆结构");
    await loadWorkspaces();
  } catch (error) {
    toast(error.message);
  }
}

async function submitAdaptiveMemory(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  try {
    const payload = JSON.parse(fd.get("payload") || "{}");
    const data = await request(`/api/memory/forms/${encodeURIComponent(fd.get("run_id"))}/submit`, {
      method: "POST",
      body: JSON.stringify({ payload, visibility: "workspace" }),
    });
    toast(`已存储：${data.memory.title}`);
    $("#adaptiveQueryText").value = data.memory.retrieval_triggers[0] || data.memory.type;
  } catch (error) {
    toast(error.message);
  }
}

async function queryAdaptiveMemory() {
  const workspaceId = $("#adaptiveQueryWorkspace").value.trim();
  if (!workspaceId) {
    toast("需要工作空间 ID");
    return;
  }
  try {
    const q = encodeURIComponent($("#adaptiveQueryText").value.trim());
    const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/memory/query?q=${q}`);
    $("#adaptiveQueryResult").textContent = data.context || "没有匹配记忆";
  } catch (error) {
    $("#adaptiveQueryResult").textContent = error.message;
  }
}

async function loadMemoryConsole() {
  const workspaceList = $("#memoryWorkspaceList");
  if (!workspaceList) return;
  if (!state.user && !state.apiKey) {
    workspaceList.innerHTML = `<div class="empty-line">登录后查看你的工程、记忆和 Agent 可读范围。</div>`;
    $("#memoryGraphList").innerHTML = `<div class="empty-line">暂无可加载内容</div>`;
    $("#memoryLensMap").innerHTML = `<div class="empty-line">登录后加载你的工程记忆。</div>`;
    return;
  }
  try {
    await loadMemoryAgents();
    const data = await request("/api/me/workspaces");
    const items = [...(data.items || [])].sort((a, b) => {
      const aOwned = a.owned_by_current_user ? 0 : 1;
      const bOwned = b.owned_by_current_user ? 0 : 1;
      if (aOwned !== bOwned) return aOwned - bOwned;
      const aPersonal = /personal workspace/i.test(a.name || "") ? 1 : 0;
      const bPersonal = /personal workspace/i.test(b.name || "") ? 1 : 0;
      if (aPersonal !== bPersonal) return aPersonal - bPersonal;
      return String(b.updated_at || "").localeCompare(String(a.updated_at || ""));
    });
    const first = items[0];
    const selectedId = $("#memoryWorkspaceId").value || state.memory.workspaceId || first?.id || "";
    if (selectedId) {
      $("#memoryWorkspaceId").value = selectedId;
      state.memory.workspaceId = selectedId;
      const selectedWorkspace = items.find((item) => item.id === selectedId) || first;
      state.memory.projectKey = selectedWorkspace?.slug || "";
      state.memory.workspaceName = selectedWorkspace?.name || "";
      $("#memoryProjectKey").value = "";
      if (selectedWorkspace) $("#memoryGraphTitle").textContent = `${selectedWorkspace.name} 工程记忆`;
    }
    workspaceList.innerHTML = items.length
      ? items
          .map(
            (item) => {
              const isActive = item.id === selectedId;
              const ownerText = item.owned_by_current_user
                ? "我创建的"
                : `${item.owner_auth_type === "agent" ? "Agent 创建" : "成员空间"} · ${item.owner_username || item.owner_id || ""}`;
              return `
              <article class="workspace-card memory-workspace-card ${isActive ? "is-active" : ""}">
                <div>
                  <strong>${escapeHtml(item.name)}</strong>
                  <span>${escapeHtml(item.role)} · ${escapeHtml(item.visibility)} · ${escapeHtml(ownerText)}</span>
                  <small>${escapeHtml(item.description || item.slug || "工程记忆空间")}</small>
                </div>
                <button class="mini-button" data-memory-use-workspace="${escapeHtml(item.id)}" data-project-key="${escapeHtml(item.slug)}" data-workspace-name="${escapeHtml(item.name)}" type="button">${isActive ? "当前" : "打开"}</button>
              </article>
            `;
            },
          )
          .join("")
      : `<div class="empty-line">暂无工程。可以先在团队空间里创建一个工程空间。</div>`;
    await loadMemoryLens();
    if ($("#memoryWorkspaceId").value) {
      await loadMemoryGraphs();
      await loadMemoryAgentView();
    }
  } catch (error) {
    workspaceList.innerHTML = `<div class="empty-line">加载失败：${escapeHtml(error.message)}</div>`;
  }
}

function memoryLensStatusLabel(status) {
  return {
    active: "点亮",
    muted: "暂停",
    locked: "锁定",
    merged: "合并",
  }[status] || status;
}

function memoryLensKindLabel(kind) {
  return {
    adaptive_memory: "记忆",
    summary_card: "摘要",
    memory_delta: "变化",
    memory_node: "树节点",
    memory_package: "开源记忆",
    workspace: "工作空间",
    topic: "主题",
    user: "用户",
  }[kind] || kind;
}

function updateMemoryLensStats(stats = {}) {
  $("#memoryStatWorkspaces").textContent = String(stats.workspaces || 0);
  $("#memoryStatAssets").textContent = String(stats.primary_assets ?? stats.assets ?? 0);
  $("#memoryStatReadable").textContent = String(stats.active_primary ?? stats.active ?? 0);
  $("#memoryStatAgents").textContent = String(stats.agents || 0);
}

function memoryTopicPriority(topic, items = []) {
  const joined = `${topic} ${(items[0]?.kind || "")} ${(items[0]?.type_label || "")}`.toLowerCase();
  if (joined.includes("项目") || joined.includes("工程") || joined.includes("project")) return 0;
  if (joined.includes("决策") || joined.includes("decision")) return 1;
  if (joined.includes("失败") || joined.includes("复盘") || joined.includes("failure")) return 2;
  if (joined.includes("代码") || joined.includes("code")) return 3;
  if (joined.includes("open-memory") || joined.includes("开源")) return 8;
  return 4;
}

function renderMemoryLensMap(data) {
  state.memory.map = data;
  updateMemoryLensStats(data.stats);
  const canvas = $("#memoryLensMap");
  const primaryAssets = data.primary_assets || [];
  const secondaryAssets = data.secondary_assets || [];
  const assets = primaryAssets.length ? primaryAssets : (data.assets || []);
  const secondaryCount = secondaryAssets.length;
  const byTopic = new Map();
  for (const asset of assets) {
    const key = asset.topic || asset.type_label || "记忆";
    if (!byTopic.has(key)) byTopic.set(key, []);
    byTopic.get(key).push(asset);
  }
  const selected = assets.find((item) => item.id === state.memory.selectedAssetId) || assets[0];
  const primaryHtml = assets.length
    ? Array.from(byTopic.entries())
        .sort((a, b) => memoryTopicPriority(a[0], a[1]) - memoryTopicPriority(b[0], b[1]))
        .slice(0, 12)
        .map(([topic, items]) => {
          const activeCount = items.filter((item) => ["active", "locked", "merged"].includes(item.status)).length;
          const isLargeOpenMemory = items.length > 8 && /open-memory|开源/i.test(`${topic} ${items[0]?.kind || ""} ${items[0]?.type_label || ""}`);
          const visibleItems = isLargeOpenMemory ? items.slice(0, 6) : items.slice(0, 9);
          const hiddenCount = Math.max(0, items.length - visibleItems.length);
          return `
            <section class="memory-topic-group ${isLargeOpenMemory ? "is-condensed" : ""}">
              <button class="memory-topic-head" type="button" data-memory-topic="${escapeHtml(topic)}">
                <strong>${escapeHtml(topic)}</strong>
                <span>${activeCount}/${items.length} 可读</span>
              </button>
              <div class="memory-asset-grid">
                ${visibleItems
                  .map(
                    (asset) => `
                      <button class="memory-asset-pill status-${escapeHtml(asset.status)} ${selected?.id === asset.id ? "is-selected" : ""}" type="button" data-memory-asset="${escapeHtml(asset.id)}">
                        <span>${escapeHtml(memoryLensKindLabel(asset.kind))}</span>
                        <strong>${escapeHtml(asset.title)}</strong>
                      </button>
                    `,
                  )
                  .join("")}
              </div>
              ${hiddenCount ? `<div class="memory-topic-more">还有 ${hiddenCount} 条同类开源记忆，进入开源广场或搜索时再查看。</div>` : ""}
            </section>
          `;
        })
        .join("")
    : `<div class="empty-line">这个工程还没有核心工程记忆。可以先在团队空间写入项目经验、决策、代码规则或失败复盘。</div>`;
  canvas.innerHTML = `${primaryHtml}${
    secondaryCount
      ? `<details class="inline-advanced memory-secondary-sources">
          <summary>其他来源 ${secondaryCount}</summary>
          <div class="memory-secondary-note">这里包含运行摘要、工作变化、项目树节点、已安装开源记忆等辅助来源；默认不混进核心工程记忆。</div>
          <div class="memory-secondary-grid">
            ${secondaryAssets
              .slice(0, 12)
              .map(
                (asset) => `
                  <button class="memory-asset-pill status-${escapeHtml(asset.status)}" type="button" data-memory-asset="${escapeHtml(asset.id)}">
                    <span>${escapeHtml(memoryLensKindLabel(asset.kind))}</span>
                    <strong>${escapeHtml(asset.title)}</strong>
                  </button>
                `,
              )
              .join("")}
          </div>
          ${secondaryCount > 12 ? `<div class="memory-topic-more">还有 ${secondaryCount - 12} 条辅助来源，按需检索时再查看。</div>` : ""}
        </details>`
      : ""
  }`;
  renderMemoryAssetDetail(selected);
}

function renderMemoryAssetDetail(asset) {
  const box = $("#memoryAssetDetail");
  if (!box) return;
  if (!asset) {
    box.innerHTML = "选择一条记忆查看摘要。";
    return;
  }
  state.memory.selectedAssetId = asset.id;
  box.innerHTML = `
    <div class="memory-detail-head">
      <span class="memory-node-type">${escapeHtml(asset.type_label || memoryLensKindLabel(asset.kind))}</span>
      <span class="memory-detail-status status-${escapeHtml(asset.status)}">${escapeHtml(memoryLensStatusLabel(asset.status))}</span>
    </div>
    <strong>${escapeHtml(asset.title)}</strong>
    <p>${escapeHtml(asset.summary || "暂无摘要")}</p>
    <small>${escapeHtml(asset.workspace_name || asset.visibility || "")}</small>
  `;
}

async function loadMemoryLens() {
  const canvas = $("#memoryLensMap");
  if (!canvas) return;
  const workspaceId = $("#memoryWorkspaceId")?.value.trim();
  const endpoint = workspaceId ? `/api/workspaces/${encodeURIComponent(workspaceId)}/memory-map` : "/api/me/memory-map";
  try {
    const data = await request(endpoint);
    renderMemoryLensMap(data);
  } catch (error) {
    canvas.innerHTML = `<div class="empty-line">工程记忆加载失败：${escapeHtml(error.message)}</div>`;
  }
}

async function loadMemoryAgents() {
  const select = $("#memoryAgentSelect");
  if (!select) return;
  try {
    const data = await request("/api/me/agent-bindings");
    const active = (data.bindings || []).filter((item) => item.status === "active");
    const selectedId = state.memory.selectedAgentId || active[0]?.agent_id || "";
    select.innerHTML = `<option value="">选择已绑定 Agent</option>${active
      .map((item) => `<option value="${escapeHtml(item.agent_id)}">${escapeHtml(item.agent?.username || item.agent?.handle || item.agent_handle || item.agent_id)}</option>`)
      .join("")}`;
    if (selectedId) {
      state.memory.selectedAgentId = selectedId;
      select.value = selectedId;
    }
  } catch (error) {
    select.innerHTML = `<option value="">暂无可用 Agent</option>`;
  }
}

async function loadMemoryAgentView(agentId = $("#memoryAgentSelect")?.value) {
  const box = $("#memoryAgentReadable");
  if (!box) return;
  if (!agentId) {
    state.memory.selectedAgentId = "";
    box.innerHTML = "还没有选择 Agent。绑定 Agent 后，这里会显示它能读取的工程记忆。";
    return;
  }
  state.memory.selectedAgentId = agentId;
  const workspaceId = $("#memoryWorkspaceId")?.value.trim();
  const query = workspaceId ? `?workspace_id=${encodeURIComponent(workspaceId)}` : "";
  try {
    const data = await request(`/api/agents/${encodeURIComponent(agentId)}/memory-view${query}`);
    const items = data.readable_assets || [];
    box.innerHTML = `
      <div class="memory-agent-readable-head">
        <strong>${escapeHtml(data.agent?.username || data.agent?.handle || "Agent")}</strong>
        <span>${items.length} 条可读记忆</span>
      </div>
      ${
        items.length
          ? `<ol>${items
              .slice(0, 8)
              .map((item) => `<li><span>${escapeHtml(item.type_label || memoryLensKindLabel(item.kind))}</span>${escapeHtml(item.title)}</li>`)
              .join("")}</ol>`
          : `<p>${escapeHtml(data.summary || "这个 Agent 当前没有可读工程记忆。")}</p>`
      }
    `;
  } catch (error) {
    box.innerHTML = `<p>Agent 视角加载失败：${escapeHtml(error.message)}</p>`;
  }
}

async function loadMemoryGraphs() {
  const workspaceId = $("#memoryWorkspaceId")?.value.trim();
  const graphList = $("#memoryGraphList");
  if (!workspaceId) {
    toast("需要工作空间 ID");
    return;
  }
  state.memory.workspaceId = workspaceId;
  const projectKey = $("#memoryProjectKey")?.value.trim();
  const query = projectKey ? `?project_key=${encodeURIComponent(projectKey)}` : "";
  try {
    const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/memory-graphs${query}`);
    graphList.innerHTML = data.items.length
      ? data.items
          .map(
            (item) => `
              <button class="memory-graph-item ${item.id === state.memory.graphId ? "active" : ""}" data-memory-graph="${escapeHtml(item.id)}" type="button">
                <strong>${escapeHtml(item.title)}</strong>
                <span>${escapeHtml(item.project_key || data.workspace.slug)} · ${escapeHtml(item.updated_at)}</span>
              </button>
            `,
          )
          .join("")
      : `<div class="empty-line">这个工程还没有项目树。需要记录路线时，可以在高级设置中新建。</div>`;
    const preferred = data.items.find((item) => item.id === state.memory.graphId) || data.items[0];
    if (preferred) await loadMemoryGraph(preferred.id);
  } catch (error) {
    graphList.innerHTML = `<div class="empty-line">项目树加载失败：${escapeHtml(error.message)}</div>`;
  }
}

async function createMemoryGraph() {
  const workspaceId = $("#memoryWorkspaceId")?.value.trim();
  if (!workspaceId) {
    toast("需要工作空间 ID");
    return;
  }
  try {
    const projectKey = $("#memoryProjectKey")?.value.trim() || "default-project";
    const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/memory-graphs`, {
      method: "POST",
      body: JSON.stringify({
        project_key: projectKey,
        title: `${projectKey} 项目树`,
        root_summary: "用于记录 Agent 当前采用的项目路线、历史分支和交接上下文。",
      }),
    });
    state.memory.graphId = data.graph.id;
    toast("项目树已创建");
    await loadMemoryGraphs();
  } catch (error) {
    toast(error.message);
  }
}

function memoryStatusLabel(status) {
  return {
    active: "点亮",
    muted: "暂停",
    abandoned: "放弃",
    locked: "锁定",
    merged: "合并",
    archived: "归档",
  }[status] || status;
}

function memoryTypeLabel(type) {
  return {
    root: "根",
    decision: "决策",
    branch: "分支",
    fact: "事实",
    constraint: "约束",
    preference: "偏好",
    failure: "复盘",
    summary: "摘要",
    artifact: "产物",
    handoff: "交接",
  }[type] || type;
}

function memoryNodeDepth(node, byId) {
  let depth = 0;
  let current = node;
  const seen = new Set();
  while (current?.parent_id && byId.has(current.parent_id) && depth < 8 && !seen.has(current.parent_id)) {
    seen.add(current.parent_id);
    depth += 1;
    current = byId.get(current.parent_id);
  }
  return depth;
}

function renderMemoryGraph(data) {
  state.memory.graph = data.graph;
  state.memory.nodes = data.nodes || [];
  state.memory.graphId = data.graph.id;
  $("#memoryGraphTitle").textContent = `${state.memory.workspaceName || data.graph.title || data.graph.project_key || "当前工程"} 工程记忆`;
  $$(".memory-graph-item").forEach((item) => item.classList.toggle("active", item.dataset.memoryGraph === data.graph.id));
  const canvas = $("#memoryBranchCanvas");
  const byId = new Map(state.memory.nodes.map((node) => [node.id, node]));
  canvas.innerHTML = state.memory.nodes.length
    ? state.memory.nodes
        .map((node) => {
          const depth = memoryNodeDepth(node, byId);
          return `
            <article class="memory-node-card depth-${Math.min(depth, 8)} status-${escapeHtml(node.status)} type-${escapeHtml(node.node_type)}" data-memory-node="${escapeHtml(node.id)}">
              <div class="memory-node-main">
                <span class="memory-node-type">${escapeHtml(memoryTypeLabel(node.node_type))}</span>
                <strong>${escapeHtml(node.title)}</strong>
                <p>${escapeHtml(node.summary || "没有说明")}</p>
                <small>${escapeHtml(memoryStatusLabel(node.status))} · ${escapeHtml(memoryTypeLabel(node.node_type))}</small>
              </div>
              <div class="memory-node-actions">
                <details class="memory-node-action-menu">
                  <summary>调整</summary>
                  <div>
                    <button class="mini-button" data-memory-action="activate" data-node-id="${escapeHtml(node.id)}" type="button">点亮</button>
                    <button class="mini-button" data-memory-action="mute" data-node-id="${escapeHtml(node.id)}" type="button">暂停</button>
                    <button class="mini-button" data-memory-action="abandon" data-node-id="${escapeHtml(node.id)}" type="button">放弃</button>
                    <button class="mini-button" data-memory-action="lock" data-node-id="${escapeHtml(node.id)}" type="button">锁定</button>
                    <button class="mini-button" data-memory-action="merge" data-node-id="${escapeHtml(node.id)}" type="button">合并</button>
                  </div>
                </details>
              </div>
            </article>
          `;
        })
        .join("")
    : `<div class="empty-line">还没有节点。先添加一个“决策”，再添加几个候选分支。</div>`;
  renderMemoryContextPreview(data.active_memory_view, data.context_preview_markdown);
}

function renderMemoryContextPreview(view, markdown) {
  if (!view) return;
  const modeLabel = {
    development: "开发",
    exploration: "探索",
    documentation: "文档",
    handoff: "交接",
  }[view.mode] || view.mode;
  $("#memoryViewStats").innerHTML = [
    `<span>可读 ${view.active_nodes.length}</span>`,
    `<span>历史 ${view.muted_nodes.length}</span>`,
    `<span>${escapeHtml(modeLabel)}</span>`,
  ].join("");
  $("#memoryContextPreview").textContent = markdown || "Agent 可读范围暂无内容。";
  $("#memoryAgentPrompt").textContent = [
    "请读取 MemoryCloud 当前记忆分支视图后再继续：",
    `GET ${publicUrl(`/api/memory-graphs/${view.graph.id}/views/current`)}`,
    "默认只使用 active、locked、merged 节点作为当前方案；muted 和 abandoned 只作为历史，不要混入当前实现。",
    `完成后重新请求 Runtime Context Pack：POST ${publicUrl("/api/agent/bootstrap/context")}`,
  ].join("\n");
}

async function loadMemoryGraph(graphId = state.memory.graphId) {
  if (!graphId) {
    toast("需要先选择项目树");
    return;
  }
  try {
    const mode = state.memory.mode || "development";
    const data = await request(`/api/memory-graphs/${encodeURIComponent(graphId)}?mode=${encodeURIComponent(mode)}`);
    renderMemoryGraph(data);
  } catch (error) {
    $("#memoryBranchCanvas").innerHTML = `<div class="empty-line">项目树加载失败：${escapeHtml(error.message)}</div>`;
  }
}

async function createMemoryNode(event) {
  event.preventDefault();
  if (!state.memory.graphId) {
    toast("需要先选择或创建项目树");
    return;
  }
  const fd = new FormData(event.currentTarget);
  try {
    await request(`/api/memory-graphs/${encodeURIComponent(state.memory.graphId)}/nodes`, {
      method: "POST",
      body: JSON.stringify({
        parent_id: String(fd.get("parent_id") || "").trim() || null,
        node_type: fd.get("node_type"),
        title: fd.get("title"),
        summary: fd.get("summary"),
        status: fd.get("status"),
      }),
    });
    event.currentTarget.reset();
    event.currentTarget.elements.node_type.value = "branch";
    event.currentTarget.elements.status.value = "active";
    toast("节点已添加");
    await loadMemoryGraph();
  } catch (error) {
    toast(error.message);
  }
}

async function changeMemoryNodeStatus(action, nodeId) {
  if (!state.memory.graphId || !nodeId) return;
  try {
    await request(`/api/memory-graphs/${encodeURIComponent(state.memory.graphId)}/nodes/${encodeURIComponent(nodeId)}/${encodeURIComponent(action)}`, {
      method: "POST",
      body: JSON.stringify({ reason: "human memory console action" }),
    });
    toast(`已${memoryStatusLabel(action === "activate" ? "active" : action === "mute" ? "muted" : action === "abandon" ? "abandoned" : action === "lock" ? "locked" : action === "merge" ? "merged" : action)}`);
    await loadMemoryGraph();
  } catch (error) {
    toast(error.message);
  }
}

async function snapshotMemoryView() {
  if (!state.memory.graphId) {
    toast("需要先选择项目树");
    return;
  }
  try {
    const data = await request(`/api/memory-graphs/${encodeURIComponent(state.memory.graphId)}/views`, {
      method: "POST",
      body: JSON.stringify({
        mode: state.memory.mode || "development",
        reason: "human saved active memory view",
      }),
    });
    renderMemoryContextPreview(data.active_memory_view);
    toast("Agent 可读范围已保存");
  } catch (error) {
    toast(error.message);
  }
}

async function archiveMemory(slug) {
  try {
    await request(`/api/memories/${encodeURIComponent(slug)}/archive`, { method: "POST" });
    toast("记忆已归档为私有草稿");
    await loadMine();
    await loadCatalog();
  } catch (error) {
    toast(error.message);
  }
}

async function deleteMemory(slug) {
  if (!window.confirm(`确定删除 ${slug}？该操作会删除版本归档。`)) return;
  try {
    await request(`/api/memories/${encodeURIComponent(slug)}`, { method: "DELETE" });
    toast("记忆已删除");
    await loadMine();
    await loadCatalog();
  } catch (error) {
    toast(error.message);
  }
}

async function revokeApiKey(keyId) {
  try {
    await request(`/api/me/api-keys/${encodeURIComponent(keyId)}`, { method: "DELETE" });
    toast("API Key 已撤销");
    await loadApiKeys();
  } catch (error) {
    toast(error.message);
  }
}

async function syncMemory(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  const slug = fd.get("slug");
  try {
    const data = await request(`/api/memories/${encodeURIComponent(slug)}/sync`, {
      method: "POST",
      body: JSON.stringify({
        text: fd.get("text"),
        importance: Number(fd.get("importance") || 3),
        tags: ["sync"],
      }),
    });
    toast(`已同步到 v${data.version.version}`);
    await loadMine();
  } catch (error) {
    toast(error.message);
  }
}

function metricCard(label, value) {
  return `<div><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`;
}

function adminRow(columns) {
  return `<div class="admin-row">${columns.map((item) => `<span>${item}</span>`).join("")}</div>`;
}

async function loadAdmin() {
  const gate = $("#adminGate");
  const grid = document.querySelector(".admin-grid");
  if (!state.user || Number(state.user.trust_level || 0) < 9) {
    gate.style.display = "grid";
    grid.style.display = "none";
    return;
  }
  gate.style.display = "none";
  grid.style.display = "grid";
  try {
    const [overview, users, packages, audit, syncEvents] = await Promise.all([
      request("/api/admin/overview"),
      request("/api/admin/users?limit=12"),
      request("/api/admin/packages?limit=12"),
      request("/api/admin/audit?limit=16"),
      request("/api/admin/sync-events?limit=16"),
    ]);
    $("#adminMetrics").innerHTML = [
      metricCard("用户", overview.counts.users),
      metricCard("Agent", overview.counts.agents),
      metricCard("记忆", overview.counts.packages),
      metricCard("公开", overview.counts.published),
      metricCard("下架", overview.counts.blocked),
      metricCard("同步", overview.counts.sync_events),
      metricCard("订单", overview.counts.orders),
      metricCard("工单", overview.counts.support_tickets),
      metricCard("举报", overview.counts.abuse_reports),
    ].join("");
    $("#adminPackages").innerHTML = packages.items.length
      ? packages.items
          .map(
            (item) =>
              adminRow([
                `<b>${escapeHtml(item.title)}</b><small>${escapeHtml(item.slug)}</small>`,
                `<span class="status ${escapeHtml(item.status)}">${escapeHtml(item.status)}</span>`,
                `<span>${escapeHtml(item.visibility)}</span>`,
                `<button class="mini-button" data-admin-block="${escapeHtml(item.slug)}" type="button">下架</button>`,
                `<button class="mini-button" data-admin-publish="${escapeHtml(item.slug)}" type="button">发布</button>`,
              ]),
          )
          .join("")
      : `<div class="empty-line">暂无记忆</div>`;
    $("#adminUsers").innerHTML = users.items.length
      ? users.items
          .map(
            (item) =>
              adminRow([
                `<b>${escapeHtml(item.username || item.handle)}</b><small>${escapeHtml(item.email || "")}</small>`,
                `<span>${escapeHtml(item.auth_type)}</span>`,
                `<span>TL ${escapeHtml(item.trust_level)}</span>`,
                `<span>${item.disabled ? "已禁用" : "正常"}</span>`,
              ]),
          )
          .join("")
      : `<div class="empty-line">暂无用户</div>`;
    $("#adminAudit").innerHTML = audit.items.length
      ? audit.items
          .map((item) =>
            adminRow([
              `<b>${escapeHtml(item.action)}</b><small>${escapeHtml(item.created_at)}</small>`,
              `<span>${escapeHtml(item.resource_type)}</span>`,
              `<span>${escapeHtml(item.user_handle || item.user_id || "system")}</span>`,
              `<span>${escapeHtml(item.ip || "")}</span>`,
            ]),
          )
          .join("")
      : `<div class="empty-line">暂无审计日志</div>`;
    $("#adminSyncEvents").innerHTML = syncEvents.items.length
      ? syncEvents.items
          .map((item) =>
            adminRow([
              `<b>${escapeHtml(item.title)}</b><small>${escapeHtml(item.created_at)}</small>`,
              `<span>${escapeHtml(item.event_type)}</span>`,
              `<span>${escapeHtml(item.user_handle)}</span>`,
              `<span>${escapeHtml(item.slug)}</span>`,
            ]),
          )
          .join("")
      : `<div class="empty-line">暂无同步事件</div>`;
  } catch (error) {
    gate.style.display = "grid";
    grid.style.display = "none";
    gate.innerHTML = `<strong>后台加载失败</strong><span>${escapeHtml(error.message)}</span>`;
  }
}

async function updatePackageStatus(slug, status) {
  try {
    await request(`/api/admin/packages/${encodeURIComponent(slug)}`, {
      method: "POST",
      body: JSON.stringify({ status }),
    });
    toast(`已更新 ${slug} 为 ${status}`);
    await loadAdmin();
    await loadCatalog();
  } catch (error) {
    toast(error.message);
  }
}

async function loadCommerce() {
  try {
    const pricing = await request("/api/pricing");
    const planLabels = {
      free: { label: "入门", name: "免费版" },
      creator: { label: "创作者", name: "创作者版" },
      platform: { label: "平台", name: "平台版" },
    };
    const featureLabels = {
      "public memory catalog": "浏览公开记忆目录",
      "public open memory plaza": "浏览记忆开源广场",
      "agent registration": "智能体自动注册",
      "3 demo-grade packages": "可发布 3 个体验级开源记忆",
      "3 starter open memories": "可发布 3 个入门开源记忆",
      "paid packages": "支持付费记忆",
      "version analytics": "版本和安装数据分析",
      "support tickets": "支持工单",
      "commercial license workflow": "商业授权流程",
      "admin governance": "运营治理能力",
      "audit exports": "审计记录导出",
      "private deployment readiness": "私有部署准备",
      "SLA support": "SLA 支持",
    };
    $("#pricingCards").innerHTML = pricing.plans
      .map(
        (plan) => {
          const labels = planLabels[plan.id] || { label: plan.id, name: plan.name };
          const price = plan.price_cents_monthly === 0 ? "免费" : `$${(plan.price_cents_monthly / 100).toFixed(0)}`;
          return `
          <article class="pricing-card">
            <div>
              <span class="plan-id">${escapeHtml(labels.label)}</span>
              <h4>${escapeHtml(labels.name)}</h4>
              <strong>${price}</strong>
              <small>${plan.price_cents_monthly === 0 ? "适合试用" : "每月"}</small>
            </div>
            <ul>${plan.features.map((feature) => `<li>${escapeHtml(featureLabels[feature] || feature)}</li>`).join("")}</ul>
          </article>
        `;
        },
      )
      .join("");
    if (state.user || state.apiKey) {
      const orders = await request("/api/me/orders");
      $("#myOrders").innerHTML = orders.items.length
        ? orders.items
            .map((item) =>
              adminRow([
                `<b>${escapeHtml(item.title)}</b><small>${escapeHtml(item.slug)}</small>`,
                `<span>${escapeHtml(item.status)}</span>`,
                `<span>$${(Number(item.amount_cents || 0) / 100).toFixed(2)}</span>`,
                `<span>${escapeHtml(item.created_at)}</span>`,
              ]),
            )
            .join("")
        : `<div class="empty-line">暂无订单</div>`;
    } else {
      $("#myOrders").innerHTML = `<div class="empty-line">登录后查看订单</div>`;
    }
  } catch (error) {
    $("#pricingCards").innerHTML = `<div class="commerce-panel"><strong>商业信息加载失败</strong><p>${escapeHtml(error.message)}</p></div>`;
  }
}

async function submitSupport(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  try {
    const data = await request("/api/support/tickets", {
      method: "POST",
      body: JSON.stringify({
        email: fd.get("email"),
        subject: fd.get("subject"),
        message: fd.get("message"),
        category: "support",
      }),
    });
    toast(`工单已提交：${data.ticket.id}`);
  } catch (error) {
    toast(error.message);
  }
}

async function submitReport(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  try {
    const data = await request("/api/reports", {
      method: "POST",
      body: JSON.stringify({
        slug: fd.get("slug") || null,
        reason: fd.get("reason"),
        detail: fd.get("detail"),
      }),
    });
    toast(`举报已提交：${data.report.id}`);
  } catch (error) {
    toast(error.message);
  }
}

async function checkTicket() {
  const id = $("#ticketLookup").value.trim();
  if (!id) return;
  try {
    const data = await request(`/api/support/tickets/${encodeURIComponent(id)}`);
    $("#caseLookupResult").textContent = `工单 ${data.ticket.id}: ${data.ticket.status}`;
  } catch (error) {
    $("#caseLookupResult").textContent = error.message;
  }
}

async function checkReport() {
  const id = $("#reportLookup").value.trim();
  if (!id) return;
  try {
    const data = await request(`/api/reports/${encodeURIComponent(id)}`);
    $("#caseLookupResult").textContent = `举报 ${data.report.id}: ${data.report.status}`;
  } catch (error) {
    $("#caseLookupResult").textContent = error.message;
  }
}

async function solvePow(challenge) {
  const target = "0".repeat(challenge.difficulty);
  let nonce = 0;
  while (true) {
    const text = `${challenge.challenge_id}:${challenge.server_nonce}:${nonce}`;
    const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
    const hex = Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, "0")).join("");
    if (hex.startsWith(target)) return String(nonce);
    nonce += 1;
    if (nonce % 2000 === 0) {
      $("#agentFlow").textContent = `正在计算 nonce：${nonce}`;
      await new Promise((resolve) => setTimeout(resolve, 0));
    }
  }
}

async function agentRegister(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  const flow = $("#agentFlow");
  try {
    flow.textContent = "申请 challenge...";
    const challenge = await request("/api/agent/challenge", {
      method: "POST",
      body: JSON.stringify({ intent: "register", agent_name: fd.get("handle") }),
    });
    flow.textContent = `challenge: ${challenge.challenge_id}\ndifficulty: ${challenge.difficulty}\n计算 proof-of-work...`;
    const nonce = await solvePow(challenge);
    flow.textContent += `\nnonce: ${nonce}\n提交注册...`;
    const data = await request("/api/agent/register", {
      method: "POST",
      body: JSON.stringify({
        challenge_id: challenge.challenge_id,
        nonce,
        handle: fd.get("handle"),
        agent_kind: fd.get("agent_kind"),
        memory_format: "amp.memory.v1",
      }),
    });
    state.apiKey = data.api_key;
    state.token = "";
    state.user = data.user;
    renderSession();
    showOneTimeKey(data.api_key);
    flow.textContent += `\n注册完成\nusername: ${data.user.username || data.user.handle}\napi_key: ${data.api_key}`;
    toast("Agent 已注册，API key 只在当前页面显示");
  } catch (error) {
    flow.textContent += `\n失败：${error.message}`;
    toast(error.message);
  }
}

function openAuth(mode, options = {}) {
  state.mode = mode;
  state.emailTicket = "";
  state.emailCodeTarget = "";
  $("#authTitle").textContent = options?.title || (mode === "register" ? "注册" : "登录");
  const reason = $("#authReason");
  if (reason) {
    reason.textContent = options?.reason || (mode === "register" ? "只需要唯一 Username、邮箱和密码。" : "可使用 Username 或邮箱登录。");
    reason.hidden = false;
  }
  $("#handleField").style.display = mode === "register" ? "grid" : "none";
  $("#emailCodeField").style.display = mode === "register" ? "grid" : "none";
  $("#authLookup").type = mode === "register" ? "email" : "text";
  $("#authLookup").autocomplete = mode === "register" ? "email" : "username";
  $("#authLookup").placeholder = mode === "register" ? "name@example.com" : "username 或邮箱";
  $("#authLookupLabel").textContent = mode === "register" ? "邮箱" : "Username 或邮箱";
  $("#authHandle").placeholder = "唯一 username";
  $("#authEmailCode").value = "";
  $("#authPassword").autocomplete = mode === "register" ? "new-password" : "current-password";
  $("#authSubmit").textContent = mode === "register" ? "注册" : "登录";
  const dialog = $("#authDialog");
  if (!dialog.open) {
    dialog.showModal();
  }
  window.setTimeout(() => {
    const focusTarget = mode === "register" ? $("#authHandle") : $("#authLookup");
    focusTarget?.focus();
  }, 0);
}

function updateEmailCodeButton() {
  const button = $("#sendEmailCode");
  if (!button) return;
  if (state.emailCodeCooldown > 0) {
    button.disabled = true;
    button.textContent = `${state.emailCodeCooldown}s`;
  } else {
    button.disabled = state.mode !== "register";
    button.textContent = "发送验证码";
  }
}

async function sendAuthEmailCode() {
  const email = $("#authLookup").value.trim().toLowerCase();
  if (!email) {
    toast("请先输入邮箱");
    return;
  }
  try {
    const data = await request("/api/email/send", {
      method: "POST",
      body: JSON.stringify({ email, purpose: "register" }),
    });
    state.emailTicket = "";
    state.emailCodeTarget = email;
    state.emailCodeCooldown = Number(data.cooldown_seconds || 60);
    updateEmailCodeButton();
    const timer = setInterval(() => {
      state.emailCodeCooldown = Math.max(0, state.emailCodeCooldown - 1);
      updateEmailCodeButton();
      if (state.emailCodeCooldown === 0) clearInterval(timer);
    }, 1000);
    const debugCode = data.provider?.debug_code;
    toast(debugCode ? `验证码：${debugCode}` : "验证码已发送");
  } catch (error) {
    const match = String(error.message || "").match(/wait\s+(\d+)\s+seconds/i);
    if (match) {
      state.emailCodeCooldown = Number(match[1]);
      updateEmailCodeButton();
    }
    toast(error.message);
  }
}

async function verifyAuthEmailCode(email) {
  if (state.emailTicket && state.emailCodeTarget === email) return state.emailTicket;
  const code = $("#authEmailCode").value.trim();
  if (!code) throw new Error("请输入邮箱验证码");
  const data = await request("/api/email/verify", {
    method: "POST",
    body: JSON.stringify({ email, code, purpose: "register" }),
  });
  state.emailTicket = data.email_ticket;
  state.emailCodeTarget = email;
  return data.email_ticket;
}

async function submitAuth() {
  try {
    const password = $("#authPassword").value;
    if (state.mode === "register") {
      const email = $("#authLookup").value.trim().toLowerCase();
      const emailTicket = await verifyAuthEmailCode(email);
      const data = await request("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          handle: $("#authHandle").value,
          username: $("#authHandle").value,
          email,
          password,
          email_ticket: emailTicket,
        }),
      });
      state.token = "";
      state.apiKey = "";
      state.user = data.user;
      showOneTimeKey(data.api_key);
      toast("注册完成");
    } else {
      const data = await request("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username_or_email: $("#authLookup").value, email_or_handle: $("#authLookup").value, password }),
      });
      state.token = "";
      state.apiKey = "";
      state.user = data.user;
      clearOneTimeKey();
      toast("登录完成");
    }
    renderSession();
    $("#authDialog").close();
  } catch (error) {
    toast(error.message);
  }
}

async function logout() {
  try {
    await request("/api/auth/logout", { method: "POST" });
  } catch (error) {
    toast(error.message);
  } finally {
    state.token = "";
    state.apiKey = "";
    state.user = null;
    clearOneTimeKey();
    renderSession();
    if ($("#workspaceView").classList.contains("active")) await loadMine();
    if ($("#commerceView").classList.contains("active")) await loadCommerce();
    toast("已退出");
  }
}

function motionAllowed() {
  return !isAgentRoute() && window.innerWidth < 1800 && !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function setupLaunchIntro() {
  const intro = $("#launchIntro");
  if (!intro) return;
  const adminView = location.pathname === "/admin-console";
  if (adminView || isAgentRoute()) {
    intro.classList.add("is-done");
    return;
  }
  if (!motionAllowed()) {
    intro.classList.add("is-done");
    return;
  }
  const finish = () => intro.classList.add("is-done");
  const gsap = window.gsap;
  if (gsap) {
    gsap
      .timeline({ defaults: { ease: "power3.out" }, onComplete: finish })
      .fromTo(".launch-orbit", { scale: 0.62, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.78 })
      .fromTo(".launch-ring", { scale: 0.66, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.58, stagger: 0.1 }, "<0.1")
      .fromTo(".launch-wordmark > *", { y: 22, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.56, stagger: 0.08 }, "<0.16")
      .to(".launch-orbit", { scale: 1.1, duration: 0.44, ease: "power2.inOut" }, "+=0.72")
      .to("#launchIntro", { autoAlpha: 0, duration: 0.48, ease: "power2.in" }, "<0.08");
    return;
  }
  const orbit = $(".launch-orbit");
  const rings = $$(".launch-ring");
  const words = $$(".launch-wordmark > *");
  orbit?.animate(
    [
      { opacity: 0, transform: "scale(0.62)" },
      { opacity: 1, transform: "scale(1)", offset: 0.46 },
      { opacity: 1, transform: "scale(1.08)" },
    ],
    { duration: 2300, easing: "cubic-bezier(.16, 1, .3, 1)", fill: "both" },
  );
  rings.forEach((ring, index) => {
    const baseTransform = ring.classList.contains("launch-ring-a") ? "scaleX(1.42) rotate(18deg)" : "scaleY(1.42) rotate(-18deg)";
    ring.animate(
      [
        { opacity: 0, transform: `${baseTransform} scale(0.66)` },
        { opacity: 1, transform: `${baseTransform} scale(1)` },
      ],
      { duration: 720, delay: 180 + index * 110, easing: "cubic-bezier(.16, 1, .3, 1)", fill: "both" },
    );
  });
  words.forEach((word, index) => {
    word.animate(
      [
        { opacity: 0, transform: "translateY(22px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      { duration: 620, delay: 460 + index * 90, easing: "cubic-bezier(.16, 1, .3, 1)", fill: "both" },
    );
  });
  window.setTimeout(() => {
    intro.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 480, easing: "cubic-bezier(.4, 0, 1, 1)", fill: "both" });
    window.setTimeout(finish, 480);
  }, 2300);
}

function nativeStagger(selector, keyframes, options = {}) {
  if (!motionAllowed()) return;
  $$(selector).forEach((element, index) => {
    element.animate(keyframes, {
      duration: options.duration || 520,
      delay: (options.delay || 0) + index * (options.stagger || 55),
      easing: options.easing || "cubic-bezier(.16, 1, .3, 1)",
      fill: "both",
    });
  });
}

function animateStorefrontIntro() {
  if (!motionAllowed()) return;
  const gsap = window.gsap;
  if (gsap) {
    const tl = gsap.timeline({ defaults: { duration: 0.62, ease: "power3.out" } });
    tl.from(".agent-command-copy > *", { y: 24, autoAlpha: 0, stagger: 0.08 })
      .from(".agent-command-input", { y: 26, scale: 0.975, autoAlpha: 0, duration: 0.68 }, "<0.16")
      .from(".agent-command-hint", { y: 14, autoAlpha: 0, duration: 0.42 }, "<0.22");
    return;
  }
  nativeStagger(".agent-command-copy > *, .agent-command-input, .agent-command-hint", [
    { opacity: 0, transform: "translateY(28px) scale(0.96)" },
    { opacity: 1, transform: "translateY(0)" },
  ], { duration: 720, stagger: 48 });
}

function animateCatalogCards() {
  if (!motionAllowed() || currentSurface === "human" && document.body.dataset.view === "catalog") return;
  const gsap = window.gsap;
  if (gsap) {
    gsap.from("#catalogList .package-card", {
      y: 24,
      autoAlpha: 0,
      duration: 0.48,
      ease: "power2.out",
      stagger: 0.06,
      overwrite: "auto",
    });
    return;
  }
  nativeStagger("#catalogList .package-card", [
    { opacity: 0, transform: "translateY(22px)" },
    { opacity: 1, transform: "translateY(0)" },
  ], { duration: 460, stagger: 45 });
}

function animateActiveView(view) {
  if (!motionAllowed() || currentSurface === "agent") return;
  const selector = `#${view}View > *`;
  const gsap = window.gsap;
  if (gsap) {
    gsap.from(selector, {
      y: 16,
      autoAlpha: 0,
      duration: 0.42,
      ease: "power2.out",
      stagger: 0.04,
      overwrite: "auto",
    });
    return;
  }
  nativeStagger(selector, [
    { opacity: 0, transform: "translateY(16px)" },
    { opacity: 1, transform: "translateY(0)" },
  ], { duration: 420, stagger: 40 });
}

function setupRevealMotion(selector) {
  if (isAgentRoute()) return;
  const elements = $$(selector).filter((element) => !element.dataset.revealReady);
  if (!elements.length) return;
  elements.forEach((element) => {
    element.dataset.revealReady = "true";
    element.classList.add("motion-reveal");
  });
  if (!motionAllowed() || !("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("is-revealed"));
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        entry.target.animate(
          [
            { opacity: 0.72, transform: "translateY(22px) scale(0.985)" },
            { opacity: 1, transform: "translateY(0) scale(1)" },
          ],
          {
            duration: 620,
            easing: "cubic-bezier(.16, 1, .3, 1)",
            fill: "both",
          },
        );
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.16, rootMargin: "0px 0px -8% 0px" },
  );
  elements.forEach((element) => observer.observe(element));
}

function setupCardMotion() {
  if (!motionAllowed() || currentSurface === "agent") return;
  const targets = $$(".package-card, .immortality-scene, .featured-capsule")
    .filter((element) => !element.closest(".home-deck") && !element.dataset.tiltReady);
  targets.forEach((element) => {
    element.dataset.tiltReady = "true";
    element.addEventListener("mousemove", (event) => {
      const rect = element.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      const rotateX = (-y * 7).toFixed(2);
      const rotateY = (x * 8).toFixed(2);
      element.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px) scale(1.012)`;
    });
    element.addEventListener("mouseleave", () => {
      element.style.transform = "";
    });
  });
}

function setupMotionEffects() {
  setupRevealMotion(".agent-command-hero, .outcome-page, .scenario-page, .page-hero, .journey-strip article, .account-card, .flow-step-card, .enterprise-value-card, .methodology-grid article, .enterprise-flow-steps li, .enterprise-cta, .trust-card, .docs-route-grid a, .advanced-panel, .section-head, .panel, .doc-card, .info-card, .mechanism-card, .integration-card, .commerce-panel, .pricing-card");
  setupCardMotion();
  setupAmbientMotion();
  setupVisibleHomeMotion();
}

function bind(selector, eventName, handler) {
  const element = $(selector);
  if (element) element.addEventListener(eventName, handler);
}

$$(".nav-item").forEach((item) =>
  item.addEventListener("click", (event) => {
    event.preventDefault();
    const route = new URL(item.getAttribute("href") || routeForView(item.dataset.view), location.origin).pathname;
    const next = PATH_VIEW_MAP[route] || { view: item.dataset.view, surface: route.startsWith("/agent/") ? "agent" : "human" };
    setView(next.view, { surface: next.surface, updateUrl: true, route });
  }),
);
$$(".view-action").forEach((button) =>
  button.addEventListener("click", () => {
    const view = button.dataset.view;
    setView(view, { surface: "human", updateUrl: true });
  }),
);
$$(".route-link").forEach((link) =>
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const route = new URL(link.getAttribute("href") || "/", location.origin).pathname;
    const next = PATH_VIEW_MAP[route] || { view: link.dataset.routeView || "catalog", surface: route.startsWith("/agent/") ? "agent" : "human" };
    setView(next.view, { surface: next.surface, updateUrl: true, route });
  }),
);
window.addEventListener("popstate", () => {
  const next = routeStateFromLocation();
  setView(next.view, { surface: next.surface, updateUrl: false });
});
bind("#searchButton", "click", loadCatalog);
bind("#copyAgentBrief", "click", copyAgentBrief);
bind("#copyAgentBriefInAgent", "click", copyAgentBrief);
bind("#copyHelpAgentStart", "click", copyAgentBrief);
bind("#searchInput", "keydown", (event) => {
  if (event.key === "Enter") loadCatalog();
});
bind("#catalogList", "click", (event) => {
  const detail = event.target.closest("[data-detail]");
  if (detail) showDetail(detail.dataset.detail);
});
bind("#publishForm", "submit", publishMemory);
bind("#validatePublish", "click", validatePublish);
bind("#importForm", "submit", importMemory);
bind("#validateImport", "click", validateImport);
bind("#agentRegisterForm", "submit", agentRegister);
bind("#adaptiveRouteForm", "submit", routeAdaptiveMemory);
bind("#adaptiveSubmitForm", "submit", submitAdaptiveMemory);
bind("#adaptiveQueryButton", "click", queryAdaptiveMemory);
bind("#personaDistillForm", "submit", submitPersonaDistill);
bind("#reloadWorkspaces", "click", loadWorkspaces);
bind("#workspaceCreateForm", "submit", createWorkspace);
bind("#workspaceMemberForm", "submit", addWorkspaceMember);
bind("#handoffCreateForm", "submit", createProjectHandoff);
bind("#loadMemoryGraphs", "click", loadMemoryGraphs);
bind("#loadMemoryLens", "click", async () => {
  await loadMemoryLens();
  await loadMemoryAgentView();
});
bind("#createMemoryGraph", "click", createMemoryGraph);
bind("#refreshMemoryGraph", "click", () => loadMemoryGraph());
bind("#snapshotMemoryView", "click", snapshotMemoryView);
bind("#memoryNodeForm", "submit", createMemoryNode);
bind("#memoryAgentSelect", "change", (event) => loadMemoryAgentView(event.target.value));
bind("#adaptiveView", "click", (event) => {
  const useWorkspace = event.target.closest("[data-use-workspace]");
  if (useWorkspace) selectAdaptiveWorkspace(useWorkspace.dataset.useWorkspace);
});
bind("#memoryView", "click", (event) => {
  const useWorkspace = event.target.closest("[data-memory-use-workspace]");
  const graph = event.target.closest("[data-memory-graph]");
  const action = event.target.closest("[data-memory-action]");
  const node = event.target.closest("[data-memory-node]");
  if (useWorkspace) {
    $("#memoryWorkspaceId").value = useWorkspace.dataset.memoryUseWorkspace;
    state.memory.workspaceId = useWorkspace.dataset.memoryUseWorkspace;
    state.memory.projectKey = useWorkspace.dataset.projectKey || "";
    state.memory.workspaceName = useWorkspace.dataset.workspaceName || "";
    $("#memoryProjectKey").value = "";
    $$(".memory-workspace-card").forEach((card) => {
      const button = card.querySelector("[data-memory-use-workspace]");
      const active = button?.dataset.memoryUseWorkspace === state.memory.workspaceId;
      card.classList.toggle("is-active", active);
      if (button) button.textContent = active ? "当前" : "打开";
    });
    loadMemoryLens();
    loadMemoryAgentView();
    loadMemoryGraphs();
  }
  if (graph) loadMemoryGraph(graph.dataset.memoryGraph);
  if (action) changeMemoryNodeStatus(action.dataset.memoryAction, action.dataset.nodeId);
  if (node && !action && event.target.closest(".memory-node-main")) {
    $("#memoryNodeForm [name='parent_id']").value = node.dataset.memoryNode;
    toast("已把该节点设为新节点父级");
  }
  const asset = event.target.closest("[data-memory-asset]");
  if (asset && state.memory.map) {
    const allAssets = [
      ...(state.memory.map.primary_assets || []),
      ...(state.memory.map.secondary_assets || []),
      ...(state.memory.map.assets || []),
    ];
    renderMemoryAssetDetail(allAssets.find((item) => item.id === asset.dataset.memoryAsset));
  }
});
bind("#memoryView", "click", (event) => {
  const modeButton = event.target.closest("[data-memory-mode]");
  if (!modeButton) return;
  state.memory.mode = modeButton.dataset.memoryMode || "development";
  $$("[data-memory-mode]").forEach((button) => button.classList.toggle("is-selected", button === modeButton));
  loadMemoryGraph();
});
bind("#reloadMine", "click", loadMine);
bind("#reloadInstalls", "click", loadMyInstalls);
bind("#reloadAgentBindings", "click", loadAgentBindings);
bind("#copyAgentBindingPrompt", "click", copyAgentBindingPrompt);
bind("#createApiKey", "click", createApiKey);
bind("#createApiKeyShortcut", "click", createApiKey);
bind("#revokeAllApiKeys", "click", revokeAllApiKeys);
bind("#workspaceView", "click", (event) => {
  const accountTarget = event.target.closest("[data-account-target]");
  const revoke = event.target.closest("[data-revoke-key]");
  const revokeAgent = event.target.closest("[data-revoke-agent-binding]");
  const agentDashboard = event.target.closest("[data-agent-dashboard]");
  const agentMemoryOpen = event.target.closest("[data-agent-memory-open]");
  const agentWorkspaceOpen = event.target.closest("[data-agent-workspace-open]");
  const agentGraphOpen = event.target.closest("[data-agent-graph-open]");
  const agentMemoryAsset = event.target.closest("[data-agent-memory-asset]");
  const detail = event.target.closest("[data-detail]");
  const archive = event.target.closest("[data-archive-memory]");
  const del = event.target.closest("[data-delete-memory]");
  if (accountTarget) {
    event.preventDefault();
    openAccountSection(accountTarget.dataset.accountTarget);
  }
  if (revoke) revokeApiKey(revoke.dataset.revokeKey);
  if (revokeAgent) revokeAgentBinding(revokeAgent.dataset.revokeAgentBinding);
  if (agentDashboard) openAgentWorkbench(agentDashboard.dataset.agentDashboard);
  if (agentMemoryOpen) openAgentFullMemoryView(agentMemoryOpen.dataset.agentMemoryOpen);
  if (agentWorkspaceOpen) {
    $("#memoryWorkspaceId").value = agentWorkspaceOpen.dataset.agentWorkspaceOpen;
    state.memory.workspaceId = agentWorkspaceOpen.dataset.agentWorkspaceOpen;
    setView("memory");
    window.setTimeout(() => {
      loadMemoryLens();
      loadMemoryGraphs();
    }, 0);
  }
  if (agentGraphOpen) {
    setView("memory");
    window.setTimeout(() => loadMemoryGraph(agentGraphOpen.dataset.agentGraphOpen), 0);
  }
  if (agentMemoryAsset) {
    setView("memory");
    window.setTimeout(async () => {
      await loadMemoryLens();
      const asset = state.memory.map?.assets?.find((item) => item.id === agentMemoryAsset.dataset.agentMemoryAsset);
      if (asset) renderMemoryAssetDetail(asset);
    }, 0);
  }
  if (detail) showDetail(detail.dataset.detail);
  if (archive) archiveMemory(archive.dataset.archiveMemory);
  if (del) deleteMemory(del.dataset.deleteMemory);
});
bind("#accountMenu", "click", (event) => {
  const target = event.target.closest("[data-account-target]");
  if (!target) return;
  event.preventDefault();
  openAccountSection(target.dataset.accountTarget);
});
bind("#syncForm", "submit", syncMemory);
bind("#reloadAdmin", "click", loadAdmin);
bind("#reloadCommerce", "click", loadCommerce);
bind("#supportForm", "submit", submitSupport);
bind("#reportForm", "submit", submitReport);
bind("#checkTicket", "click", checkTicket);
bind("#checkReport", "click", checkReport);
bind("#adminView", "click", (event) => {
  const block = event.target.closest("[data-admin-block]");
  const publish = event.target.closest("[data-admin-publish]");
  if (block) updatePackageStatus(block.dataset.adminBlock, "blocked");
  if (publish) updatePackageStatus(publish.dataset.adminPublish, "published");
});
bind("#openLogin", "click", () => openAuth("login"));
bind("#openRegister", "click", () => openAuth("register"));
bind("#logoutButton", "click", logout);
bind("#authSubmit", "click", submitAuth);
bind("#sendEmailCode", "click", sendAuthEmailCode);

document.addEventListener(
  "click",
  (event) => {
    const install = event.target.closest("[data-install-memory]");
    if (!install) return;
    event.preventDefault();
    event.stopPropagation();
    copyMemoryInstallCard(install);
  },
  true,
);

updateSurfaceChrome(initialViewFromLocation().view, initialViewFromLocation().surface);
setupLaunchIntro();
bootstrap();
