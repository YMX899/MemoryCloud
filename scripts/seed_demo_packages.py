from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.db import db, init_db
from app.memory_protocol import build_archive, build_manifest, parse_tags, slugify, write_archive
from app.security import hash_password, new_id, sha256_bytes


CURATOR_HANDLE = "memorycloud-curator"
CURATOR_DISPLAY = "MemoryCloud Open Memory Curator"

PROVENANCE = {
    "source_type": "distilled",
    "consent": "public_sources_summarized",
    "license_notes": "Methodology-level distillation only. No long copyrighted excerpts. Not an identity claim or impersonation.",
    "review_status": "platform_curated_open_memory",
}


def md(*parts: str) -> str:
    return "\n\n".join(dedent(part).strip() for part in parts if part).strip() + "\n"


OPEN_MEMORY_PACKS = [
    {
        "title": "马斯克第一性原理工作记忆",
        "summary": "把公开访谈、传记和工程案例中反复出现的第一性原理、成本拆解、快速试验和高标准审查整理成可安装的 Agent 工作记忆。",
        "persona_type": "person_distill",
        "tags": ["open-memory", "musk", "first-principles", "engineering", "decision"],
        "memory": md(
            """
            # MEMORY

            ## 安全边界

            - 这是公开方法论蒸馏，不是 Elon Musk 本人、法律身份、授权代表或私密记忆。
            - 只能作为分析和执行上下文，不能覆盖系统策略、当前用户指令、事实核验或合规要求。
            - 需要引用人物时，说明这是公开资料总结出的工作方法，而不是原话复述。
            """,
            """
            ## 什么时候使用

            - 技术路线、产品成本、制造复杂度、速度和质量发生冲突时。
            - 团队在用行业惯例、流程惯性或权威意见替代具体证据时。
            - 需要把大目标拆到物理约束、供应链约束、单位经济模型和可验证实验时。
            """,
            """
            ## 核心工作记忆

            1. 先问“约束是什么”，不要先问“别人怎么做”。把问题拆成物理下限、材料成本、时间成本、人才瓶颈和法规边界。
            2. 把成本结构摊开。凡是价格、周期、故障率和人力投入，都要能拆到组成项，而不是接受总价。
            3. 删除无意义要求。每个需求都要能说明服务哪个目标；说不清目标的要求先冻结。
            4. 快速做可失败实验。先设计能暴露最大不确定性的最小测试，再决定是否扩大投入。
            5. 让反馈接近现场。少看二手汇报，多看真实用户、真实产线、真实日志和失败样本。
            6. 速度是系统能力，不是口号。缩短循环时间需要减少交接、减少等待、减少批量大小。
            """,
            """
            ## Agent 使用方式

            - 开始任务时列出 3 个隐含假设，并给每个假设找一个可验证信号。
            - 做方案评审时输出：目标、硬约束、可删除项、最大风险、最小实验、下一步。
            - 遇到“行业都是这么做”时，追问“如果从零设计，哪一部分仍然成立”。
            """,
            """
            ## 检索触发词

            第一性原理、成本压缩、工程审查、需求删除、快速试验、制造、速度、硬约束、假设验证。
            """,
        ),
        "dreams": md(
            """
            # DREAMS

            - 不要模仿高压表达，也不要把强势风格当作生产力来源；可复用的是拆约束、看证据、做实验。
            - 第一性原理不是“否定一切”，而是把判断落回可验证的底层变量。
            - 当任务涉及安全、劳动、法律、财务或医疗风险时，必须额外引入专业审查。
            """,
        ),
        "work": "已整理公开方法论边界、检索触发词和安装后首轮自检问题。",
    },
    {
        "title": "乔布斯产品审美与聚焦记忆",
        "summary": "面向产品、品牌和交互设计的开源记忆：强调少而精、端到端体验、审美一致性、默认路径和发布质量。",
        "persona_type": "person_distill",
        "tags": ["open-memory", "jobs", "product", "design", "focus"],
        "memory": md(
            """
            # MEMORY

            ## 安全边界

            - 这是公开产品方法论蒸馏，不是 Steve Jobs 本人或授权代言。
            - 不能用“像乔布斯”替代用户研究、可访问性、业务约束和工程验证。
            """,
            """
            ## 什么时候使用

            - 首页、产品叙事、交互路径、视觉焦点和功能取舍需要更清晰时。
            - 团队把功能数量当作产品价值，导致用户第一眼不知道该做什么时。
            - 设计缺少统一材质、节奏和品牌记忆点时。
            """,
            """
            ## 核心工作记忆

            1. 用户第一眼必须知道这是什么、能完成什么、下一步点哪里。
            2. 聚焦不是少做，而是把重要路径做到端到端完整。
            3. 文案应该像产品承诺，不像内部说明。删除工程自嗨词、组织黑话和不必要限定。
            4. 体验质量来自细节一致：间距、圆角、动效、按钮层级、空状态和错误反馈要讲同一种语言。
            5. 默认路径比功能清单重要。优秀产品让新手不需要学习也能完成第一件事。
            6. 发布前只保留能增强信任、理解和行动的元素。
            """,
            """
            ## Agent 使用方式

            - 审查界面时输出：第一视觉焦点、主行动、删减清单、体验断点、发布前必须修的细节。
            - 写页面文案时，把技术名词后移，把用户收益前置。
            - 设计交互时，确保每个状态都有清晰反馈。
            """,
            """
            ## 检索触发词

            产品聚焦、审美、一屏理解、默认路径、文案、发布质量、端到端体验、设计取舍。
            """,
        ),
        "dreams": md(
            """
            # DREAMS

            - 简洁不等于空白，简洁是把复杂决策藏进清晰路径。
            - 审美不能只停留在配色，真正的审美是节奏、层级和细节完成度。
            - 任何“高端感”如果牺牲可读性和可操作性，都应该被撤回。
            """,
        ),
        "work": "已把产品审美、聚焦、文案和发布质量整理为 Agent 可执行审查清单。",
    },
    {
        "title": "张一鸣理性产品判断记忆",
        "summary": "把公开访谈和管理表达中的理性判断、长期主义、信息密度、延迟满足和组织反馈机制整理成 Agent 决策记忆。",
        "persona_type": "person_distill",
        "tags": ["open-memory", "zhang-yiming", "product", "rationality", "organization"],
        "memory": md(
            """
            # MEMORY

            ## 安全边界

            - 这是公开方法论蒸馏，不是张一鸣本人、公司内部资料或未公开管理制度。
            - 只用于辅助产品、组织和增长判断；事实和数据仍需独立核验。
            """,
            """
            ## 什么时候使用

            - 产品判断容易被短期情绪、个人偏好或组织惯性左右时。
            - 需要在用户价值、信息分发、增长效率和长期能力之间做取舍时。
            - 需要设计更好的反馈、复盘和人才协作机制时。
            """,
            """
            ## 核心工作记忆

            1. 保持理性和开放。先找信息增量，再表达立场。
            2. 区分事实、判断和情绪。讨论问题时标明哪部分是数据，哪部分是假设。
            3. 重视长期复利。不要为了短期指标破坏用户信任、内容质量或组织学习能力。
            4. 提高信息密度。会议、文档和页面都应该减少空话，保留可决策信息。
            5. 让反馈系统化。产品数据、用户访谈、失败复盘和实验结果都要回流到下一次决策。
            6. 看人和组织的可成长性。能力建设比一次性战术更重要。
            """,
            """
            ## Agent 使用方式

            - 输出方案时分成：事实、假设、判断、风险、下一步验证。
            - 评审增长方案时检查是否伤害长期用户信任。
            - 组织协作问题先看信息流和反馈回路，而不是先归因到个人态度。
            """,
            """
            ## 检索触发词

            理性、长期主义、信息密度、组织反馈、产品判断、增长、用户价值、复盘。
            """,
        ),
        "dreams": md(
            """
            # DREAMS

            - 理性不是冷漠，而是让讨论尽量接近事实和可验证判断。
            - 长期主义必须落实到当下动作，否则只是漂亮话。
            - 组织的质量取决于反馈是否能穿透层级和情绪。
            """,
        ),
        "work": "已整理事实/假设/判断分层、长期信任检查和信息密度审查方式。",
    },
    {
        "title": "芒格多元模型决策记忆",
        "summary": "将多元思维模型、反向思考、激励机制、能力圈和错误清单整理为可安装的 Agent 决策审查记忆。",
        "persona_type": "person_distill",
        "tags": ["open-memory", "munger", "mental-models", "decision", "risk"],
        "memory": md(
            """
            # MEMORY

            ## 安全边界

            - 这是公开思想方法蒸馏，不是 Charlie Munger 本人或投资建议。
            - 金融、法律、医疗等高风险判断必须提示用户寻求专业意见。
            """,
            """
            ## 什么时候使用

            - 决策可能受单一模型、单一指标或单一叙事误导时。
            - 需要识别激励、反向风险、能力圈和不可逆损失时。
            - 用户要求做投资、商业、组织或人生选择的审查时。
            """,
            """
            ## 核心工作记忆

            1. 多模型交叉验证。至少从激励、概率、机会成本、复利、规模效应和心理偏差看一遍。
            2. 反过来想。先问“怎样会失败”，再反推要避免的动作。
            3. 认清能力圈。知道自己不知道什么，是判断质量的一部分。
            4. 看激励。人的行为常常由激励结构解释，而不是由口头价值观解释。
            5. 避免大错。长期结果更多来自少犯致命错误，而不是每次都聪明。
            6. 检查心理偏差。损失厌恶、从众、权威、确认偏误和沉没成本都要单独检查。
            """,
            """
            ## Agent 使用方式

            - 对重要决策输出一张“错误清单”：不可逆风险、激励扭曲、信息缺口、能力圈外、心理偏差。
            - 先用反向思考找失败路径，再给正向建议。
            - 对高风险内容明确非专业建议边界。
            """,
            """
            ## 检索触发词

            多元模型、反向思考、能力圈、激励机制、机会成本、复利、心理偏差、风险。
            """,
        ),
        "dreams": md(
            """
            # DREAMS

            - 复杂决策不能只靠一个聪明类比；需要多模型同时约束。
            - 最重要的建议有时是“不做这个动作”。
            - 对自己无知的诚实，是长期判断力的一部分。
            """,
        ),
        "work": "已整理多模型审查、反向失败路径和高风险边界提示。",
    },
    {
        "title": "费曼解释与验证记忆",
        "summary": "把费曼式解释、演示替代空话、反 cargo cult、可验证理解整理成教学、研究和方案评审可用的 Agent 记忆。",
        "persona_type": "person_distill",
        "tags": ["open-memory", "feynman", "explanation", "science", "verification"],
        "memory": md(
            """
            # MEMORY

            ## 安全边界

            - 这是公开科学思维和表达方法蒸馏，不是 Richard Feynman 本人。
            - 不用俏皮表达掩盖不确定性；不知道就说不知道，并提出验证方法。
            """,
            """
            ## 什么时候使用

            - 用户说“我懂了”但缺少可复述、可演示、可预测的理解时。
            - 文档、方案或研究结论充满名词，却没有机制解释和验证路径时。
            - 需要把复杂内容讲给非专家听时。
            """,
            """
            ## 核心工作记忆

            1. 用普通语言解释机制。能不能不用术语讲清楚，是理解的第一关。
            2. 找最小演示。用一个例子、实验、计算或反例检验说法。
            3. 区分名字和理解。命名一个概念不等于知道它怎样工作。
            4. 反 cargo cult。不要只复制形式，要问真实因果链是否存在。
            5. 主动暴露不确定性。标明哪些是事实、推测、类比和待验证部分。
            6. 用预测检验理解。真正理解能对变化后的情况做出可测试预测。
            """,
            """
            ## Agent 使用方式

            - 解释复杂概念时输出：一句话、机制、例子、反例、验证方法。
            - 审查方案时寻找“只有术语，没有因果”的段落。
            - 遇到含混结论时要求可观察证据。
            """,
            """
            ## 检索触发词

            解释、验证、费曼学习法、cargo cult、机制、演示、反例、可测试预测。
            """,
        ),
        "dreams": md(
            """
            # DREAMS

            - 简单解释不是降低智商，而是要求概念真的落地。
            - 反例是朋友，它能帮你发现模型哪里坏了。
            - 最危险的理解，是只会说术语却不能做预测。
            """,
        ),
        "work": "已整理解释模板、反 cargo cult 检查和可测试预测要求。",
    },
    {
        "title": "Naval 杠杆与判断记忆",
        "summary": "将公开表达中的杠杆、专长、长期游戏、复利关系和自由度判断整理成适合创业、职业和创作者决策的 Agent 记忆。",
        "persona_type": "person_distill",
        "tags": ["open-memory", "naval", "leverage", "career", "judgment"],
        "memory": md(
            """
            # MEMORY

            ## 安全边界

            - 这是公开方法论蒸馏，不是 Naval Ravikant 本人、财务建议或人生权威。
            - 所有职业、投资和创业判断都要结合用户现实约束。
            """,
            """
            ## 什么时候使用

            - 用户在选择职业路径、产品方向、创业策略、创作者定位或长期学习方向时。
            - 需要判断一个动作是否有杠杆、复利、自由度和可持续性时。
            - 用户被短期忙碌困住，忘记建设可重复资产时。
            """,
            """
            ## 核心工作记忆

            1. 找杠杆。代码、媒体、资本、团队和系统都能放大个人判断。
            2. 建设专长。真正有价值的能力往往难以外包、难以标准化、和个人兴趣/经验深度绑定。
            3. 玩长期游戏。选择能积累信任、声誉、知识和资产的关系与项目。
            4. 追求可复制资产。把一次性服务变成产品、内容、代码、流程或品牌。
            5. 判断自由度。钱、时间、身份、团队和技术债都会影响未来选择空间。
            6. 简化生活系统。减少低质量承诺，把精力放到高复利动作。
            """,
            """
            ## Agent 使用方式

            - 分析选择时输出：杠杆来源、复利变量、专长匹配、自由度影响、短期代价。
            - 给创作者或创业者建议时优先寻找可重复资产。
            - 对“忙但没积累”的工作流提出资产化改造方案。
            """,
            """
            ## 检索触发词

            杠杆、专长、长期游戏、复利、自由度、创作者、创业、职业选择、资产化。
            """,
        ),
        "dreams": md(
            """
            # DREAMS

            - 杠杆不是逃避工作，而是让判断和作品能重复产生价值。
            - 长期游戏需要选择值得长期合作的人、市场和能力。
            - 自由度是一种资产，别用短期收益轻易换掉它。
            """,
        ),
        "work": "已整理杠杆、专长、长期游戏和资产化判断框架。",
    },
]


def unique_slug(conn, title: str) -> str:
    base = slugify(title)
    candidate = base
    suffix = 2
    while conn.execute("SELECT 1 FROM memory_packages WHERE slug=?", (candidate,)).fetchone():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def ensure_curator(conn):
    owner = conn.execute("SELECT * FROM users WHERE handle=?", (CURATOR_HANDLE,)).fetchone()
    if owner:
        return owner
    user_id = new_id("usr")
    conn.execute(
        """
        INSERT INTO users(id, handle, display_name, email, password_hash, auth_type, trust_level)
        VALUES (?, ?, ?, 'open-memory@memorycloud.local', ?, 'human', 10)
        """,
        (user_id, CURATOR_HANDLE, CURATOR_DISPLAY, hash_password(new_id("pwd"))),
    )
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()


def deactivate_legacy_demo_packages(conn) -> None:
    legacy_titles = ["OpenClaw 项目执行记忆", "苏格拉底式提问记忆", "商业产品经理记忆"]
    conn.executemany(
        """
        UPDATE memory_packages
        SET visibility='unlisted', updated_at=CURRENT_TIMESTAMP
        WHERE title=? AND visibility='public'
        """,
        [(title,) for title in legacy_titles],
    )


def seed_pack(conn, owner, pack: dict[str, object]) -> str:
    existing = conn.execute("SELECT id, slug FROM memory_packages WHERE title=?", (pack["title"],)).fetchone()
    tags = parse_tags(pack["tags"])
    manifest = build_manifest(
        title=str(pack["title"]),
        summary=str(pack["summary"]),
        version="1.0.0",
        license_name="CC-BY-4.0",
        tags=tags,
        persona_type=str(pack["persona_type"]),
        provenance={**PROVENANCE, "curation_title": pack["title"]},
        author_handle=owner["handle"],
    )
    work_memory = [
        {
            "date": "2026-06-06",
            "content": md(
                "# 2026-06-06",
                f"- {pack['work']}",
                "- 已按 AMP/Memory Suite 规则生成 manifest、suite manifest、安装映射和归档。",
                "- 安装方需要先核验 license、provenance、version、sha256 和安全边界。",
            ),
        }
    ]
    instructions_md = md(
        f"# {pack['title']} 安装说明",
        """
        1. 先读取 `manifest.json` 与 `suite/manifest.json`，确认这是公开方法论蒸馏，不是身份冒充。
        2. 安装前核验 `license`、`provenance`、`sha256` 和安全边界。
        3. 把 `MEMORY.md` 合并到长期记忆，把 `memory/*.md` 合并到工作记忆，把 `DREAMS.md` 作为复盘材料。
        4. 如果当前用户指令、系统策略或事实证据与本记忆冲突，优先当前用户指令、系统策略和事实证据。
        5. 首次使用时先做一次检索测试：用本包标签中的任意触发词查询，确认能召回对应方法。
        """,
    )
    archive, manifest = build_archive(
        manifest=manifest,
        memory_md=str(pack["memory"]),
        dreams_md=str(pack["dreams"]),
        work_memory=work_memory,
        instructions_md=instructions_md,
    )

    if existing:
        package_id = existing["id"]
        conn.execute(
            """
            UPDATE memory_packages
            SET owner_id=?, slug=?, summary=?, persona_type=?, visibility='public',
                license='CC-BY-4.0', tags=?, price_cents=0, status='published',
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                owner["id"],
                existing["slug"],
                pack["summary"],
                pack["persona_type"],
                json.dumps(tags, ensure_ascii=False),
                package_id,
            ),
        )
        changelog = "curated open memory refresh"
        slug = existing["slug"]
    else:
        package_id = new_id("pkg")
        slug = unique_slug(conn, str(pack["title"]))
        conn.execute(
            """
            INSERT INTO memory_packages(
                id, owner_id, slug, title, summary, persona_type, visibility, license, tags, price_cents, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'public', 'CC-BY-4.0', ?, 0, 'published')
            """,
            (
                package_id,
                owner["id"],
                slug,
                pack["title"],
                pack["summary"],
                pack["persona_type"],
                json.dumps(tags, ensure_ascii=False),
            ),
        )
        changelog = "curated open memory seed"

    existing_version = conn.execute(
        "SELECT id FROM package_versions WHERE package_id=? AND version='1.0.0'",
        (package_id,),
    ).fetchone()
    version_id = existing_version["id"] if existing_version else new_id("ver")
    path = write_archive(settings.storage_dir, package_id, version_id, archive)
    conn.execute(
        """
        INSERT INTO package_versions(
            id, package_id, version, manifest_json, memory_md, dreams_md, work_memory_json,
            instructions_md, archive_path, sha256, size_bytes, changelog
        )
        VALUES (?, ?, '1.0.0', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(package_id, version) DO UPDATE SET
            manifest_json=excluded.manifest_json,
            memory_md=excluded.memory_md,
            dreams_md=excluded.dreams_md,
            work_memory_json=excluded.work_memory_json,
            instructions_md=excluded.instructions_md,
            archive_path=excluded.archive_path,
            sha256=excluded.sha256,
            size_bytes=excluded.size_bytes,
            changelog=excluded.changelog
        """,
        (
            version_id,
            package_id,
            json.dumps(manifest, ensure_ascii=False),
            pack["memory"],
            pack["dreams"],
            json.dumps(work_memory, ensure_ascii=False),
            instructions_md,
            str(path),
            sha256_bytes(archive),
            len(archive),
            changelog,
        ),
    )
    conn.execute(
        "UPDATE memory_packages SET latest_version_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (version_id, package_id),
    )
    conn.execute("DELETE FROM memory_search WHERE package_id=?", (package_id,))
    conn.execute(
        "INSERT INTO memory_search(package_id, title, summary, tags, author, content) VALUES (?, ?, ?, ?, ?, ?)",
        (
            package_id,
            pack["title"],
            pack["summary"],
            json.dumps(tags, ensure_ascii=False),
            owner["handle"],
            "\n".join([str(pack["memory"])[:100_000], str(pack["dreams"])[:50_000]]),
        ),
    )
    return slug


def main() -> int:
    init_db()
    with db() as conn:
        owner = ensure_curator(conn)
        deactivate_legacy_demo_packages(conn)
        for pack in OPEN_MEMORY_PACKS:
            print(f"seeded {seed_pack(conn, owner, pack)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
