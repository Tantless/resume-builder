# 中文技术简历构建器

## 是什么

`resume-builder` 是给 agent CLI 使用的中文技术简历 skill。它会根据用户的自由描述、已有简历、项目经历或求职目标，追问缺失信息，整理中文简历画像 YAML，并渲染为 LaTeX 或 PDF 简历。

适合人群：

- 应届生、实习生、转岗候选人。
- 后端、前端、AI 应用、全栈、数据等技术岗位候选人。
- 想让 Codex、Claude Code、OpenClaw 等 agent CLI 协助整理中文技术简历的人。

## 放到哪里

把整个 `resume-builder/` 文件夹放进当前 agent CLI 能发现的 skills 根目录下。不要只复制 `SKILL.md`，模板、脚本、参考文档和示例文件也要一起保留。

可移植目录形状：

```text
skills-root/
└── resume-builder/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    ├── assets/
    └── examples/
```

不同 agent CLI 的全局或项目级 skills 根目录名称可能不同。安装时遵循该 CLI 的约定即可；skill 内部命令只假设自己位于 `resume-builder/` 根目录，不假设任何固定绝对路径。

## 怎么调用

Codex 示例：

```text
$resume-builder 帮我生成一版中文技术简历，模板用 dev。下面是我的背景：...
```

Claude Code 示例：

```text
/resume-builder 帮我生成一版中文技术简历，模板用 dev。下面是我的背景：...
```

OpenClaw 示例：

```text
/skill resume-builder 帮我生成一版中文技术简历，模板用 dev。下面是我的背景：...
```

也可以不用命令，直接说明要使用这个 skill：

```text
请使用 resume-builder skill，根据下面经历整理中文技术简历。目标岗位是后端工程师，模板用 fallback。...
```

## 调用时说什么

可以直接贴自然语言，不需要先整理成表格。建议包含：

- 目标岗位和投递场景。
- 教育背景、工作或实习经历、项目经历。
- 技术栈、成果数据、获奖或证书。
- 是否需要照片版。
- 求职类型，例如应届生、找实习、社招跳槽、转岗、项目型、高年限。
- 想用哪个模板。

## 语言规则

- agent 的回复语言跟随用户输入语言；没有明确偏好时默认中文。
- 本 skill 生成的简历画像 YAML、简历正文、待补充说明和渲染文件中的自然语言默认中文。
- 技术名词、字段名、模板名、枚举值和链接保持原样，例如 `Python`、`profile_version`、`dev`、`new_grad`。

## 可选模板

- `dev`：默认模板，简洁清爽，适合主要精进和日常使用。
- `fallback`：保守模板，朴素稳定，适合需要更低风险版式时使用。

不指定模板时默认使用 `dev`。

## 本地命令

以下命令都在 `resume-builder/` 根目录内执行，路径都是相对路径：

```bash
python scripts/resume_options.py --json
python scripts/render_resume.py --check-env
python scripts/render_resume.py profiles/zhangsan.yaml --out-dir output/zhangsan
python scripts/render_resume.py profiles/zhangsan.yaml --out-dir output/zhangsan --pdf
```

如果缺少 PyYAML，征得用户同意后执行：

```bash
python -m pip install -r scripts/requirements.txt
```
