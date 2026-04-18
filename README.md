# CoDesk

一个给双 Agent 协作准备的轻量文件层。

它不做消息中转，不做数据库，也不假装有“共享大脑”。它做的事很简单：

- 建一个清晰可读的共享工作区
- 把协作配置写进文件
- 生成两段可直接发给两个 Agent 的启动提示词
- 用 blackboard / reports 这些文件把协作状态留在磁盘上

如果你想要的是“先跑起来，再慢慢加能力”，CoDesk 就是干这个的。

---

## 现在能做什么

当前版本已经支持：

- 一条命令创建协作工作区：`setup`
- 生成持久化配置：`assistant-sync/config.yaml`
- 为两个 Agent 生成启动 prompt
- 生成初始报告文件
- 内建 `hermes` / `openclaw` 的基础识别与本地路径探测
- 重新打印 prompt：`print-prompts`
- 查看当前配置：`show-config`
- 保留原来的底层手工命令：`init / new-project / new-weekly / new-handoff / new-decision / validate / status / weekly-digest / sync-packet / generate-reports`

---

## 快速开始

### 先说最重要的一点

如果你现在是直接在仓库里试用，**请先进入 CoDesk 仓库根目录再运行命令**。

比如：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
```

这里的 `PYTHONPATH=src` 是相对当前目录解析的。
如果你不在仓库根目录，Python 找不到 `codesk` 包。

### 一键创建协作空间

最简单的用法：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
```

这条命令会在当前目录下创建：

```text
assistant-sync/
```

同时完成这些事：

- 写入配置文件 `assistant-sync/config.yaml`
- 生成初始报告文件
- 打印两段可直接复制给两个 Agent 的 prompt

### 带参数的初始化示例

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup . \
  --project-name "Alpha rollout" \
  --objective "Keep two agents aligned on implementation" \
  --agent-a hermes \
  --agent-b openclaw \
  --sync-frequency daily \
  --notes "Use the shared blackboard for handoffs" \
  --seed-project-id proj-alpha
```

适合你已经知道项目名、协作目标和初始 project id 的情况。

---

## setup 后会生成什么

### 配置文件

```text
assistant-sync/config.yaml
```

这里面会保存：

- 项目名
- 目标描述
- 两个 Agent 的身份
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

如果你换了 agent 名，sync packet 的文件名也会跟着变。

### 共享工作区结构

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

---

## setup 的输出长什么样

命令执行成功后，终端会先看到这样的结构：

```text
CoDesk workspace created at:
/path/to/project/assistant-sync

Config written to:
/path/to/project/assistant-sync/config.yaml

Next step:
1. Copy PROMPT A into Agent 1
2. Copy PROMPT B into Agent 2
3. Ask each agent to confirm its first sync run

===== PROMPT FOR AGENT 1 =====
...

===== PROMPT FOR AGENT 2 =====
...
```

你要做的事很简单：

1. 复制 `PROMPT FOR AGENT 1`
2. 发给第一个 Agent
3. 复制 `PROMPT FOR AGENT 2`
4. 发给第二个 Agent

---

## 后续最常用的两个命令

### 重新打印 prompt

如果你关掉终端了，或者想重新发一遍：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli print-prompts .
```

### 查看当前配置

```bash
cd /Users/starsama/Code/CoDesk
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

## 如果你不想把工作区建在当前目录

可以显式给一个路径：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup /tmp/codesk-test
```

这样它会创建：

```text
/tmp/codesk-test/assistant-sync
```

---

## 底层手工命令还在

如果你不想走 `setup`，也可以继续用原来的文件级命令。

### 只初始化目录树

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli init .
```

### 新建 project 记录

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-project . \
  --project-id proj-alpha \
  --title "Alpha rollout" \
  --owner hermes \
  --status active
```

### 新建 weekly 记录

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-weekly . \
  --week 2026-W16 \
  --assistant hermes
```

### 新建 handoff 记录

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-handoff . \
  --handoff-id handoff-001 \
  --from-assistant hermes \
  --to-assistant openclaw \
  --project proj-alpha
```

### 新建 decision 记录

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli new-decision . \
  --decision-id decision-001 \
  --topic "Weekly sync cadence"
```

### 校验工作区

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli validate .
```

### 查看当前摘要

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

## 适合什么，不适合什么

### 适合

- 两个 Agent 需要围绕同一个项目持续协作
- 你想把协作状态留在文件里，而不是全靠对话上下文
- 你想先把工作流跑通，再考虑更复杂的自动化

### 不适合

- 你需要实时消息中转
- 你要多 Agent 编排平台
- 你要数据库 / 向量库 / Web UI
- 你想把 scheduler 也交给 CoDesk 统一托管

---

## 当前内建的 agent 支持

目前内建了两类默认项：

- `hermes`
- `openclaw`

CoDesk 会优先尝试探测这些常见本地路径：

- `~/.hermes`
- `~/.openclaw`

也支持环境变量覆盖：

- `HERMES_HOME`
- `OPENCLAW_HOME`

---

## 当前项目状态

这轮 bootstrap milestone 已经落地：

- config layer
- agent detection
- prompt rendering
- setup service
- CLI product surface
- README onboarding

如果你现在只是想手动试一遍，最稳妥的起手式就是：

```bash
cd /Users/starsama/Code/CoDesk
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup .
```

跑完以后，再接：

```bash
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli show-config .
PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli print-prompts .
```

基本就够了。
