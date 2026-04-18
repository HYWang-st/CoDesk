# CoDesk

> 一个给双 Agent 协作准备的轻量文件层。先把协作跑起来，再慢慢加能力。

CoDesk 不是消息中转站，也不是数据库，更不是“共享大脑”。
它做的事很直接：

- 建一个清晰的共享工作区
- 把协作配置写进文件
- 生成两段可直接发给两个 Agent 的启动 prompt
- 把 blackboard、handoff、report 这些协作痕迹留在磁盘上

如果你想要的是 **一条命令起盘、文件可读、流程可查、后面还能继续扩**，它就是干这个的。

---

## 目录

- [它解决什么问题](#它解决什么问题)
- [现在能做什么](#现在能做什么)
- [30 秒上手](#30-秒上手)
- [你会得到什么](#你会得到什么)
- [推荐工作方式](#推荐工作方式)
- [常用命令](#常用命令)
- [手工工作流](#手工工作流)
- [目录结构](#目录结构)
- [当前内建支持](#当前内建支持)
- [faq](#faq)
- [适合什么，不适合什么](#适合什么不适合什么)
- [roadmap](#roadmap)

---

## 它解决什么问题

很多双 Agent 协作最后会卡在两个地方：

1. 状态只活在上下文里，窗口一换就断
2. 没有稳定的交接面，所有 handoff 都靠人手转述

CoDesk 的想法很朴素：

- **共享状态放文件里**
- **Agent 各自保持独立**
- **交接靠 blackboard 和 reports**
- **启动靠 setup 一次性拉起**

这样你不用先搭一个大系统，先有一个能落地、能检查、能继续迭代的版本就够了。

---

## 现在能做什么

当前版本已经支持：

- `setup`：一条命令创建协作空间
- `assistant-sync/config.yaml`：持久化协作配置
- 双 Agent 启动 prompt 自动生成
- 初始报告文件自动生成
- `print-prompts`：随时重打两段 prompt
- `show-config`：查看当前配置摘要
- 内建 `hermes` / `openclaw` 的基础识别和本地路径探测
- 保留原来的底层手工命令：
  - `init`
  - `new-project`
  - `new-weekly`
  - `new-handoff`
  - `new-decision`
  - `validate`
  - `status`
  - `weekly-digest`
  - `sync-packet`
  - `generate-reports`

---

## 30 秒上手

### 第一步：进入仓库根目录

如果你是直接在仓库里试用，**先进入 CoDesk 仓库根目录再运行命令**。

```bash
cd /Users/path/to/CoDesk
```

原因很简单：当前用法里有一段 `PYTHONPATH=src`，它是按**当前目录**解释的。
如果你不在仓库根目录，Python 找不到 `codesk` 包。

### 第二步：执行 setup

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
```

这条命令会在当前目录下创建：

```text
assistant-sync/
```

然后它会同时做完这几件事：

- 写入 `assistant-sync/config.yaml`
- 生成初始 reports
- 打印两段可直接复制给两个 Agent 的 prompt

### 第三步：把两段 prompt 分别发给两个 Agent

终端输出里会出现：

```text
===== PROMPT FOR AGENT 1 =====
...

===== PROMPT FOR AGENT 2 =====
...
```

你只需要把两段内容分别发给两个 Agent 就行。

---

## 你会得到什么

### 配置文件

```text
assistant-sync/config.yaml
```

这里会保存：

- 项目名
- 协作目标
- agent 身份
- sync 频率
- 工作区路径
- 探测到的本地 agent 路径（如果有）
- setup 时使用的默认值信息

### 初始报告

```text
assistant-sync/shared/reports/weekly-digest.md
assistant-sync/shared/reports/sync-packet-hermes-to-openclaw.md
assistant-sync/shared/reports/sync-packet-openclaw-to-hermes.md
```

如果你换了 agent 名，sync packet 文件名也会跟着变。

### 一份可读的共享空间

```text
assistant-sync/
  blackboard/
    projects/
    weekly/
    handoffs/
    decisions/
  hermes_to_openclaw/
  openclaw_to_hermes/
  shared/
    reports/
  references/
    source-pointers/
  config.yaml
```

它不复杂，但够清楚。

---

## 推荐工作方式

最推荐的用法其实就三条命令：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli show-config .
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli print-prompts .
```

- `setup`：第一次拉起
- `show-config`：确认配置是不是你想要的
- `print-prompts`：需要重发 prompt 时再打一次

如果你已经知道项目名、目标和初始 project id，可以直接这样：

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup . \
  --project-name "Alpha rollout" \
  --objective "Keep two agents aligned on implementation" \
  --agent-a hermes \
  --agent-b openclaw \
  --sync-frequency daily \
  --notes "Use the shared blackboard for handoffs" \
  --seed-project-id proj-alpha
```

---

## 常用命令

### setup

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
```

如果你不想把工作区建在当前目录，也可以显式给路径：

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup /tmp/codesk-test
```

那它会创建：

```text
/tmp/codesk-test/assistant-sync
```

### print-prompts

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli print-prompts .
```

适合终端关掉以后重新打印 prompt。

### show-config

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli show-config .
```

示例输出：

```text
Project: Alpha rollout
Objective: Keep two agents aligned on implementation
Sync frequency: daily
Agent A: hermes
Agent B: openclaw
Workspace: /path/to/project/assistant-sync
```

---

## 手工工作流

如果你不想走 `setup`，原来的底层文件命令也都还在。

### 只初始化目录树

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli init .
```

### 新建 project

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-project . \
  --project-id proj-alpha \
  --title "Alpha rollout" \
  --owner hermes \
  --status active
```

### 新建 weekly

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-weekly . \
  --week 2026-W16 \
  --assistant hermes
```

### 新建 handoff

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-handoff . \
  --handoff-id handoff-001 \
  --from-assistant hermes \
  --to-assistant openclaw \
  --project proj-alpha
```

### 新建 decision

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-decision . \
  --decision-id decision-001 \
  --topic "Weekly sync cadence"
```

### 校验工作区

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli validate .
```

### 查看摘要

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli status .
```

### 生成 weekly digest

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli weekly-digest .
```

### 生成 sync packet

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli sync-packet . \
  --from-assistant hermes \
  --to-assistant openclaw
```

### 一次性写出全部报告

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli generate-reports . \
  --assistant-a hermes \
  --assistant-b openclaw
```

---

## 目录结构

如果你直接用 `setup`，最后拿到的大致就是这套结构：

```text
assistant-sync/
  blackboard/
    projects/
    weekly/
    handoffs/
    decisions/
  hermes_to_openclaw/
  openclaw_to_hermes/
  shared/
    reports/
      weekly-digest.md
      sync-packet-hermes-to-openclaw.md
      sync-packet-openclaw-to-hermes.md
  references/
    source-pointers/
  config.yaml
```

---

## 当前内建支持

当前内建了两类默认项：

- `hermes`
- `openclaw`

CoDesk 会优先尝试探测这些常见本地路径：

- `~/.hermes`
- `~/.openclaw`

也支持环境变量覆盖：

- `HERMES_HOME`
- `OPENCLAW_HOME`

---

## faq

### 为什么我运行 `PYTHONPATH=src ...` 会报 `ModuleNotFoundError: No module named 'codesk'`？

因为你不在仓库根目录。

正确姿势是先：

```bash
cd /Users/starsama/Code/CoDesk
```

再执行：

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
```

### `setup .` 会把工作区建在哪里？

会建在你当前目录下面的：

```text
assistant-sync/
```

比如你当前目录是：

```text
/Users/starsama/Code/CoDesk
```

那它会创建到：

```text
/Users/starsama/Code/CoDesk/assistant-sync
```

### 我关掉终端了，还能重新拿到 prompt 吗？

可以：

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli print-prompts .
```

### 我只想看配置，不想重跑 setup，怎么办？

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli show-config .
```

---

## 适合什么，不适合什么

### 适合

- 两个 Agent 围绕同一个项目持续协作
- 你想把协作状态落在文件里，而不是只活在上下文里
- 你想先把最小工作流跑通，再逐步加自动化

### 不适合

- 你需要实时消息中转
- 你要多 Agent 编排平台
- 你要数据库 / 向量库 / Web UI
- 你想把 scheduler 也交给 CoDesk 托管

---

## roadmap

这轮 bootstrap milestone 已经落地：

- config layer
- agent detection
- prompt rendering
- setup service
- CLI product surface
- README onboarding

下一步更自然的方向大概是：

- `detect-agents` 调试命令
- 更细的 interactive setup 体验
- 更严格的 config 校验和错误提示
- 打包与发布整理

---

## 最后一条建议

如果你现在只是想亲手试一遍，最稳妥的起手式还是这三条：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli show-config .
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli print-prompts .
```

跑完你基本就能知道这个项目现在是不是你想要的那种手感了。
