# UCI 作业自动化代理 — 总计划

**优先级：当前 repo 最高优先任务**
**目标：全自动拉取、分析、完成、提交 UCI Canvas 作业**

---

## 总体架构

Orchestrator Skill（总指挥）+ 子 Skills：

1. 定时拉取 Canvas 作业 → 解析类型和要求
2. 本地文档类（Google Doc / Word / Markdown）→ 自动生成内容并保存
3. 浏览器可验证类（填空、选择、短答）→ 自动完成并提交
4. Quiz 类（计时、防作弊）→ 暂停，通知献之手动操控
5. 长期记忆：每门课维护"语言风格"（从过往作业样本学习）

---

## 需要的 Skills

### 现成 Skills（直接装）

| Skill | 用途 | 安装方式 |
|-------|------|----------|
| canvas-lms | 拉课程、assignments、to-do、截止日期、submission 状态 | `clawhub install pranavkarthik10/canvas-lms` |
| playwright-mcp / agent-browser | 浏览器自动化：打开 Canvas、填答案、Submit、截图 | `clawhub install playwright-mcp` |
| file handler | 文件读写增强（Markdown、Word、Google Doc 同步） | OpenClaw 原生 + 按需补充 |

### 自建 Custom Skills（核心）

| Skill | 功能 |
|-------|------|
| **uci-assignment-analyzer** | 读 canvas-lms 返回的作业描述 → 判断类型（本地 doc / 浏览器题 / Quiz / Discussion）→ 输出结构化 JSON 决定下一步 |
| **uci-course-persona** | 每门课存 Persona 文件（过往作业样本 + 偏好：语气、长度、引用风格）。写作业前自动加载，保证风格一致。支持 `/update-persona [course]` |
| **uci-doc-writer** | 本地文档自动写 → 生成内容 → 保存到指定路径（可接 Google Drive） |
| **uci-browser-submitter** | 结合 Playwright，自动完成"能验证答案"的题（不碰 Quiz） |
| **uci-quiz-notifier** | 发现 Quiz → 通知献之 → 等回复后交接浏览器控制 |
| **uci-homework-orchestrator** | 总指挥 Meta Skill，串联所有子 skill，支持 cron 定时 + 手动 "check my assignments" |

---

## 执行路线图

### Phase 0: 基础设施（今天）
- [ ] 生成 UCI Canvas API Token（https://canvas.eee.uci.edu → Account → Settings）
- [ ] 装 canvas-lms skill
- [ ] 装 playwright-mcp / browser skill
- [ ] 测试拉作业数据

### Phase 1: 作业分析器（1-2 小时）
- [ ] 创建 uci-assignment-analyzer skill（SKILL.md）
- [ ] 测试：拉作业 → 分类 → 输出 JSON

### Phase 2: 课程风格守护（1 小时）
- [ ] 创建 uci-course-persona skill
- [ ] 为每门课初始化 Persona（从过往作业样本学习）
- [ ] 支持 /update-persona 命令

### Phase 3: 自动完成能力（2-3 小时）
- [ ] 创建 uci-doc-writer（本地文档自动写）
- [ ] 创建 uci-browser-submitter（浏览器自动提交简单题）
- [ ] 创建 uci-quiz-notifier（Quiz 暂停交接）

### Phase 4: 总指挥编排（1-2 小时）
- [ ] 创建 uci-homework-orchestrator（串联所有 skill）
- [ ] 加 cron：每天早上 8 点自动 check
- [ ] 手动触发：`check my assignments`

### Phase 5: 测试 & 迭代
- [ ] 先测试"自动看作业 + 分析类型 + 告诉我"
- [ ] 逐步开放 auto-write（从简单本地 doc 开始）
- [ ] 记录每次执行结果，优化 prompt

### Phase 6: 进阶
- [ ] 长期记忆（作业历史向量数据库）
- [ ] 安全 gating：`safe mode` 才允许提交
- [ ] 每门课独立 persona 持续进化

---

## 关键配置

```
CANVAS_URL=https://canvas.eee.uci.edu
CANVAS_TOKEN=<待生成>
```

## 文件存放

- Custom Skills: `.claude/claudeclaw/skills/uci-*` 或 OpenClaw workspace skills 目录
- Course Personas: `.claude/claudeclaw/personas/<course_id>.md`
- 作业输出: `C:\Users\32247\Documents\UCI\<course>\<assignment>.md`

---

## 注意事项

- Quiz 类**绝对不能**自动提交 — 有防作弊检测，必须通知献之手动操控
- 每门课的语言风格必须从献之过往提交的作业样本学习，不能用通用 AI 腔
- Canvas Token 有权限范围，生成时注意勾选足够权限
- 浏览器提交前必须截图存证，方便回查
