from pathlib import Path


def test_static_frontend_has_required_surfaces():
    html = Path("static/index.html").read_text(encoding="utf-8")
    js = Path("static/app.js").read_text(encoding="utf-8")
    css = Path("static/styles.css").read_text(encoding="utf-8")
    assert "记忆云" in html
    assert "MemoryCloud" in html
    assert "Yueming AI" in html
    assert "yueming-logo-svg" in html
    assert "yueming-logo-crescent" in html
    assert "hero-brand-lockup" in html
    assert "brand-loop" not in html
    assert "记忆开源广场" in html
    assert "开源记忆包" in html
    assert "点“安装”需要登录，会复制一张开源记忆接力卡" in html
    assert "显示名" not in html
    assert "authName" not in html
    assert "nameField" not in html
    assert "authName" not in js
    assert "nameField" not in js
    assert "唯一 Username" in html
    assert "dialog-reason" in html
    assert "安装需要登录。查看详情不用登录" in js
    assert "document.addEventListener(" in js
    assert "event.target.closest(\"[data-install-memory]\")" in js
    assert "加载广场" not in html
    assert "Memory Suite" in html
    assert "cloudmemory" not in html.lower()
    assert "cloudmemory" not in js.lower()
    assert "把这句发给你的 AI" in html
    assert "agent-background-reel" in html
    assert "agent-boundless-field" in html
    assert "boundless-sheet" in html
    assert "home-scroll" in html
    assert "home-deck-controls" not in html
    assert "agent-conversation-card" not in html
    assert "发出去以后，AI 会自己接上" in html
    assert "AI 打开入口" in html
    assert "创建自己的访问身份" in html
    assert "读取当前任务记忆" in html
    assert "不会乱动旧资料" in html
    assert "把结果留下来" in html
    assert "旧本地记忆默认只看不搬" in html
    assert "按需升级" in html
    assert "未授权不会迁移上传" not in html
    assert "主记忆运行时" not in html
    assert "切换运行时" not in html
    assert "已接入 MemoryCloud" in html
    assert "http://127.0.0.1:18085/agent/start" not in html
    assert "http://127.0.0.1:18085/agent/start" not in js
    assert "data-agent-start-url" in html
    assert "agentStartUrl()" in js
    assert 'PUBLIC_SITE_ORIGIN = window.location.origin || "http://127.0.0.1:8000"' in js
    assert "服务入口" in html
    assert "账户中心" in html
    assert "我的记忆空间" in html
    assert "我的工作台" in html
    assert "工程 / Agent / Key" in html
    assert "account-dashboard-shell" in html
    assert "account-dashboard-sidebar" in html
    assert "account-overview" in html
    assert "memory-space-summary" in html
    assert "memory-package-board" in html
    assert "nav-more-trigger" in html
    assert "上传开源记忆</a>" not in html
    assert "data-view=\"workspace\">用户中心" not in html
    assert "我的记忆空间" in js
    assert "renderAccountIdentity" in js
    assert "renderAccountMetrics" in js
    assert "updateAccountCount" in js
    assert "/memory-routes/mem0/health" in html
    assert "/memory-routes/graphiti/health" in html
    assert "/memory-routes/memori/health" in html
    assert "先做 Quick Connect" in html
    assert "先做 Quick Connect，再按需升级启动项或导入旧记忆" in html
    assert "按页面 autostart 流程一次完成 MemoryCloud 接入" not in html
    assert "不要默认写 .amp/memory-config.json" in js
    assert "打开</span><span>http://127.0.0.1:18085/agent/start" not in html
    assert "const startUrl = `${window.location.origin}/agent/start`;" not in js
    assert "location.origin}/api/agent" not in js
    assert "location.origin}/api/memory-graphs" not in js
    assert "font-size: clamp(42px, 8.5vw, 136px)" not in css
    assert "dialogueStreamUp" not in css
    assert "agent-conversation-card" not in css
    assert "boundlessFloat" in css
    assert "deckAtmosphere" in css
    assert ".home-deck-page.is-before" not in css
    assert "addEventListener(\"wheel\"" not in js
    assert "touchmove" not in js
    assert "scrollIntoView" in js
    assert "body.home-surface .main" in css
    assert "width: 100%;" in css
    assert "--home-inner: 1680px" in css
    assert "body.home-surface .home-deck-page.agent-command-hero" in css
    assert "min-height: calc(100dvh - 64px)" in css
    assert "font-size: clamp(48px, 6vw, 96px)" in css
    assert "font-size: clamp(48px, 7vw, 118px)" not in css
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in css
    assert "Agent 注册" in html
    assert "MEMORY.md" in html
    assert "DREAMS.md" in html
    assert "发布 Memory Suite" in html
    assert "持久化记忆存储" in html
    assert "记忆工具" in html
    assert "文档中心" in html
    assert "开发文档" in html
    assert "企业服务" in html
    assert "帮助" in html
    assert "帮助中心" in html
    assert "Agent 忘了怎么用，就查这里" in html
    assert "POST /api/agent/methods/query" in html
    assert "method_query_helper" in html
    assert "/agent/help" in html
    assert "/agent/help.md" in html
    assert "/api/agent/methods" in html
    assert "/api/agent/methods/query" in html
    assert "MemoryCloud Private Cloud" in html
    assert "企业知识云" in html
    assert "员工离职，方法论仍留在组织里" in html
    assert "企业想把员工的方法论沉淀下来" in html
    assert "项目经验" in html
    assert "代码审查规则" in html
    assert "岗位方法论" in html
    assert "高质量提示与流程" in html
    assert "失败复盘" in html
    assert "最佳实践" in html
    assert "Agent 云时代提速" in html
    assert "当前支持的记忆方法" in html
    assert "层级文件记忆" in html
    assert "结构化事件记忆" in html
    assert "向量语义检索记忆" in html
    assert "知识图谱记忆" in html
    assert "Workspace 云端记忆" in html
    assert "代码记忆上下文" in html
    assert "自适应记忆路由" in html
    assert "开源主流记忆系统本地部署" in html
    assert "mem0" in html
    assert "Graphiti" in html
    assert "OpenViking" in html
    assert "supermemory" in html
    assert "Letta" in html
    assert "agentmemory" in html
    assert "cognee" in html
    assert "memvid" in html
    assert "Hindsight" in html
    assert "Memori" in html
    assert "/api/memory/integrations" in html
    assert "/api/memory/integrations/recommend" in html
    assert "/api/memory/local-deployments" in html
    assert "/api/memory/local-deployments/compose.yml" in html
    assert "/api/memory/local-deployments/health" in html
    assert "/memory-routes/{integration_id}/health" in html
    assert "/api/agent/skills/memory_system_integrator/pull" in html
    assert "memory_system_integrator" in html
    assert "Memory Suite市场" not in html
    assert "MemoryCloud Registry" not in html
    assert "记忆工具 Skill" not in html
    assert "多 Agent 协作锁" not in html
    assert "项目交接记忆" not in html
    assert "人格广场" not in html
    assert "人格蒸馏" not in html
    assert "可安装人格" not in html
    assert "从人格" not in html
    assert "平台设计报告" in html
    assert "/platform-design-report" in html
    assert "管理后台" in html
    assert "商业化" in html
    assert "智能记忆" in html
    assert "adaptiveRouteForm" in html
    assert "adaptiveSubmitForm" in html
    assert "adaptiveQueryWorkspace" in html
    assert "workspaceCreateForm" in html
    assert "workspaceMemberForm" in html
    assert "handoffCreateForm" in html
    assert "handoffResult" in html
    assert "项目交接链接" in html
    assert "绑定接手 Agent username" in html
    assert "claim secret" in html
    assert "AMP-HANDOFF-v1" in html
    assert "/handoff/{handoff_code}" in html
    assert "/api/agent/handoffs/{handoff_code}/accept" in html
    assert "/agent-start" in html
    assert "/human/main" in html
    assert "/human/docs" in html
    assert "/human/enterprise" in html
    assert "/human/memory" in html
    assert "/human/memories" in js
    assert "/agent/main" in html
    assert "/agent/publish" in html
    assert "/agent/account" in html
    assert "/agent/team" in html
    assert "/agent/memory" in html
    assert "/agent/memories" in js
    assert "/agent/enterprise" in html
    assert "/agent/docs" in html
    assert "/agent/doc" in html
    assert "/agent/support" in html
    assert "/agent/protocol" in html
    assert "/agent/start" in html
    assert "/api/agent/autostart" in html
    assert "/api/agent/memory-takeover/policy" in html
    assert "memory_takeover_migrator" in html
    assert "deprecated_read_only" in html
    assert "自动启动链接" in html
    assert "/llms.txt" in html
    assert "/.well-known/agent.json" in html
    assert "memory-console.png" in html
    assert "/terms" in html
    assert "/privacy" in html
    assert "logoutButton" in html
    assert "accountMenu" in html
    assert "account-section-nav" in html
    assert "data-account-target=\"my-memory\"" in html
    assert "data-account-target=\"my-installs\"" in html
    assert "data-account-target=\"workspace-section\"" in html
    assert "data-account-target=\"agent-bindings\"" in html
    assert "data-account-target=\"api-keys\"" in html
    assert "我的记忆" in html
    assert "我安装的" in html
    assert "工作空间" in html
    assert "Agent 绑定" in html
    assert "复制绑定话术" in html
    assert "已连接 Agent" in html
    assert "需要确认" in html
    assert "绑定新 Agent" in html
    assert "不要把密码、验证码或 API Key" in html
    assert "agentBindingStatus" in html
    assert "agentBindingActiveBlock" in html
    assert "agentBindingRequestsBlock" in html
    assert "agentBindingSetup" in html
    assert "agentBindingPromptPreview" in html
    assert "copyAgentBindingPrompt" in js
    assert "renderAgentBindingStatus" in js
    assert "renderAgentBindingCard" in js
    assert "binding-block" in css
    assert "binding-agent-card" in css
    assert "binding-guide-grid" not in css
    assert "安全设置" in html
    assert "普通查看记忆空间不需要 API Key" in html
    assert "installList" in html
    assert "accountWorkspaceList" in html
    assert "reloadInstalls" in html
    assert "createApiKey" in html
    assert "revokeAllApiKeys" in js
    assert "/api/me/installs" in js
    assert "openAccountSection" in js
    assert "newKeyBox" in html
    assert "Dry-run 校验" in html
    assert "detailDialog" in html
    assert "工单/举报状态" in html
    assert "/api/status" in js
    assert "/api/session" in js
    assert "/api/auth/logout" in js
    assert "/api/me/api-keys" in js
    assert "/api/memories/validate" in js
    assert "/api/memories/import/validate" in js
    assert "/api/memory/router/select" in js
    assert "/api/memory/forms/" in js
    assert "/memory/query" in js
    assert "/api/agent/skills" in html
    assert "云端记忆 Skill" in html
    assert "memory_tool_installer" in html
    assert "agentBriefText" in js
    assert "memoryInstallCardText" in js
    assert "AMP-OPEN-MEMORY-HANDOFF-SETUP-v1" in js
    assert "AMP-OPEN-MEMORY-HANDOFF-v1" in js
    assert "/agent/memory-install/" in js
    assert "data-install-memory" in js
    assert 'docs: "文档中心"' in js
    assert 'help: "帮助中心"' in js
    assert 'help: "/help"' in js
    assert 'help: "/agent/help"' in js
    assert 'catalog: "/agent/main"' in js
    assert 'publish: "/agent/publish"' in js
    assert 'workspace: "/agent/account"' in js
    assert 'adaptive: "/agent/team"' in js
    assert 'memory: "/agent/memory"' in js
    assert 'enterprise: "/agent/enterprise"' in js
    assert 'docs: "/agent/docs"' in js
    assert 'commerce: "/agent/support"' in js
    assert "suite/manifest.json" in html
    assert "/api/workspaces" in js
    assert "/api/me/memory-map" in js
    assert "/memory-map" in js
    assert "/memory-view" in js
    assert "/workspace-dashboard" in js
    assert "我的工程记忆" in html
    assert "Agent 可读范围" in html
    assert "高级设置" in html
    assert "memoryLensMap" in html
    assert "memoryAgentSelect" in html
    assert "agent-workbench" in css
    assert "查看工作台" in js
    assert "/memory-graphs" in js
    assert "Agent 可读范围" in js
    assert "/members" in js
    assert "/delegated-handoffs" in js
    assert "createProjectHandoff" in js
    assert "/versions" in js
    assert "data-archive-memory" in js
    assert "data-delete-memory" in js
    assert "localStorage" not in js
    assert "sessionStorage" not in js
    assert "amp_token" not in js
    assert "amp_api_key" not in js
    assert "builder@example.com" not in html
    assert "memory-demo-pass" not in html
    assert "Demo Agent" not in html
    assert "开源记忆包" in html
    assert "MemoryCloud Registry" not in js
    assert "安装配置" not in html
    assert "安装配置" not in js
    assert "本体" not in html
    assert "本体" not in js
    assert ".hidden" in css
    assert ".new-key-box" in css
    assert ".error-card" in css
    assert ".adaptive-grid" in css
    assert ".mechanism-matrix" in css
    assert ".integration-grid" in css
    assert ".integration-card" in css
