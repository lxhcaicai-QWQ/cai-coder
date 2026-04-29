
Agent 记忆，结构如下：
典型三层结构：
- 会话原始日志（每次对话存一个或一天一个文件）。
- 当期/滚动记忆（当前活跃背景、进行中的任务、近期经验）。
- 长期知识与人设（偏好、规则、领域知识、词汇表）。

**L1——会话原始日志（按时间）**
- memory/2026-03-11-0207.md
- memory/2026-03-11-1435.md
内容：保留完整的对话、工具调用、错误，当作“流水账”。

**L2——当期/滚动记忆（起点文件）**
- 根目录 MEMORY.md：放“跨会话都需要记住的东西”，比如用户名、时区、当前目标、近期踩过的坑、近期经验教训。每次主会话启动时读它。
- 用定期（例如每周/每日）精炼任务，把 L1 的原始日志提炼成 L2 并剔除过时条目。

**L3——长期知识与人设（知识库式目录）**
用目录结构+索引文件
- long-term/Memory/：持久化的人设、长期偏好、常用设定。
- long-term//Knowledge/：技术指南、领域文档。
- long-term//Journal/：值得保留的日报/周报。
- long-term//Notes/：临时研究、草稿。
- 入口：obsidian/AGENT.md 作为索引，告诉 Agent “有哪些主题/文件，什么时候该去读”。


```text
memory/
  logs/          # L1 原始会话日志（按日或按次）
    YYYY-MM-DD.md
    YYYY-MM-DD.md
  this-week.md   # L2-1 当周滚动记忆（本周在做什么、最近变更）
  this-month.md  # L2-2 当月记忆（大目标、重大决策与经验教训）

long-term/       # L3 长期记忆/知识库
  AGENT.md       # 总入口：告诉 Agent 有什么、怎么查（含目录索引）
  profile.md     # 人设、偏好、约定（用户侧 + Agent 侧）
  preferences.md # 细粒度偏好（语言风格、格式要求、不要做什么）
  rules.md       # 强规则/红线
  glossary.md    # 术语/词汇表（保证回答一致性）
  projects/
    my-project-a.md
  knowledge/
    topic-1.md
    topic-2.md
  decisions/
    YYYY-MM-DD-decision-topic.md
  lessons/
    YYYY-MM-DD-lesson-learned.md
  journal/
    YYYY-MM-DD.md

```

## 每层大概放什么
### L1 memory/logs/YYYY-MM-DD.md
- 建议：只在根写一条元信息标题（方便 grep/LLM 理解），然后分段记录：
1. 时间戳 + 会话 ID 
2. 对话摘要 
3. 关键决策/任务/结果 
4. 踩坑/异常
- 用法：Agent 每次会话结束写/追加；可设置“按天轮转”。

### L2 memory/this-week.md / this-month.md
- 建议格式（便于 Agent 自动“压缩与摘要”）：
- 顶部写元信息：更新时间、覆盖区间、上次清理时间。
- 用一级标题分区：## 本周目标 | ## 进行中 | ## 关键决策 | ## 经验教训 |## 待办。
- 维护方式：
- 每日/每周由 Agent 批量读 L1，把“仍然重要”的东西提炼到 L2，并删掉过时项；也可以人工偶尔审阅。
- 文件长度要有上限（比如 800–1500 词），超了就进一步压缩或归档。

### L3 长期知识与人设
- profile.md：放“跨月都不变”的东西（用户角色、工作场景、常用工具、联系方式等）。
- preferences.md：可被更新，但变动少（语言、风格、格式约定）。
- rules.md：硬性规则、约束（不要泄露、不要执行危险命令等）。
- glossary.md：统一术语表。
- projects/*.md：项目背景、约束、进度；用“上次更新时间”做判断依据。
- knowledge/*.md：领域知识、FAQ、模板。
- decisions/*.md：记录“为什么这样做”以及当前状态。
- lessons/*.md：跨项目可复用的经验教训。
- journal/*.md：可作为“周报/月报”精炼来源，也是 L1→L3 的长期沉淀。



# 需要开发的
Agent 如何按照规定的方式去“存储”记忆？
- 核心原则：不要让 Agent 直接写文件！而是让 Agent 调用“特定用途的存储工具”，由你的代码决定存到哪里。

如果你直接给 Agent 一个 write_file(path, content) 的工具，它一定会乱写路径、乱起文件名、破坏你的 Markdown 格式。

- 正确的做法是：把“分层逻辑”封装在工具的底层代码里，对 Agent 隐藏物理细节。

## 例子
**工具 1：保存用户偏好/事实**


Agent 看到的定义： save_user_fact(key: str, value: str) -> “用于记住用户的个人习惯、基本信息。”

代码底层实现：
```python
    def save_user_fact(key, value):
        # 代码决定：这属于 L3 长期记忆，写进 profile.md
        file_path = "global/profile.md"
        # 代码负责追加或更新这行配置，保证 MD 格式不错乱
        append_or_update_md(file_path, key, value)
    
```

**工具 2：保存经验教训**
Agent 看到的定义： save_lesson_learned(task: str, mistake: str, solution: str) -> “当遇到报错、踩坑并解决后，调用此工具记录教训，避免以后重犯。”

代码底层实现：
```python
    def save_lesson_learned(task, mistake, solution):
        # 代码决定：这属于 L3 长期记忆，按日期生成独立文件
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = f"global/lessons/{today}-{task[:10]}.md"
        content = f"## 任务\n{task}\n## 踩坑\n{mistake}\n## 解决\n{solution}"
        write_file(file_path, content)
        # （进阶：顺便去更新一下 global/AGENT.md 的索引）
    
```