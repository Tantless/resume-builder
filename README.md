# Resume Builder Skill

## 是什么

`resume-builder` 是一个给 AI 编码代理使用的中文技术简历 skill。它会根据你的自由描述、已有简历、项目经历或求职目标，追问缺失信息，并帮你整理成可生成简历的内容。

适合人群：

- 应届生、实习生、转岗候选人。
- 后端、前端、AI 应用、全栈、数据等技术岗位候选人。
- 想让 Codex、Claude Code、OpenClaw 等代理协助整理中文技术简历的人。

## 放到哪里

把整个 `resume-builder` 文件夹放进你使用的 agent 的 skills 目录。不要只复制 `SKILL.md`，模板和配套文件也要一起保留。

常见目录：

- Codex：`~/.codex/skills/resume-builder/`，或项目内 `.agents/skills/resume-builder/`
- Claude Code：`~/.claude/skills/resume-builder/`，或项目内 `.claude/skills/resume-builder/`
- OpenClaw：`<workspace>/skills/resume-builder/`、`<workspace>/.agents/skills/resume-builder/`、`~/.agents/skills/resume-builder/`、`~/.openclaw/skills/resume-builder/`

## 怎么调用

Codex：

```text
$resume-builder 帮我生成一版中文技术简历，模板用 dev。下面是我的背景：...
```

Claude Code：

```text
/resume-builder 帮我生成一版中文技术简历，模板用 dev。下面是我的背景：...
```

OpenClaw：

```text
/skill resume-builder 帮我生成一版中文技术简历，模板用 dev。下面是我的背景：...
```

也可以不用命令，直接说：

```text
请使用 resume-builder skill，根据下面经历整理中文技术简历。目标岗位是后端工程师，模板用 fallback。...
```

## 调用时说什么

你可以直接贴自然语言，不需要先整理成表格。建议包含：

- 目标岗位和投递场景。
- 教育背景、工作/实习经历、项目经历。
- 技术栈、成果数据、获奖或证书。
- 是否需要照片版。
- 求职类型，例如应届生、找实习、社招跳槽、转岗、项目型、高年限。
- 想用哪个模板。

## 可选模板

- `dev`：默认模板，简洁清爽，适合主要精进和日常使用。
- `fallback`：保守模板，朴素稳定，适合需要更低风险版式时使用。

不指定模板时默认使用 `dev`。
