# Resume Builder Skill

这是一个项目内追踪的单一 agent skill，用于帮助 Codex、Claude Code 等编码代理基于用户画像生成中文技术简历。

当前 MVP 聚焦一件事：通过用户自述和自适应追问整理 Career Profile，并把 YAML 画像稳定渲染为 LaTeX 简历，可选编译为 PDF。

## 功能范围

- 先让用户自由描述求职背景，而不是填写长表单。
- 从自述中提取结构化 `Career Profile` YAML。
- 针对缺失、模糊、缺少量化结果的内容继续追问。
- 根据用户画像调整简历中项目、实习/工作、教育、技能的比重。
- 使用现代中文技术简历模板生成 `.tex`。
- 在本机有 XeLaTeX 时可生成 `.pdf`。
- 提供多个示例画像用于验证不同候选人类型。

暂不包含：

- 实时岗位 JD 拉取
- 成功率评估
- 能力差距分析
- 自动投递
- 多模板家族
- 完整 CLI 套件

## 目录结构

```text
.agents/skills/resume-builder/
├── SKILL.md
├── assets/
│   └── templates/
│       └── modern_chinese_technical.tex
├── examples/
│   ├── experienced_engineer.yaml
│   ├── new_graduate.yaml
│   └── project_heavy_intern.yaml
├── references/
│   ├── career_profile_schema.md
│   └── interview_flow.md
└── scripts/
    ├── render_resume.py
    └── requirements.txt
```

## 使用方式

在 agent 中触发或指定使用 `resume-builder` skill，让用户先自由描述背景。skill 会根据 `references/interview_flow.md` 的流程提取画像、追问缺失信息，并按 `references/career_profile_schema.md` 生成 YAML。

也可以直接用示例画像测试渲染：

```bash
python -m pip install -r .agents/skills/resume-builder/scripts/requirements.txt
python .agents/skills/resume-builder/scripts/render_resume.py .agents/skills/resume-builder/examples/new_graduate.yaml --out-dir out
```

生成 PDF：

```bash
python .agents/skills/resume-builder/scripts/render_resume.py .agents/skills/resume-builder/examples/new_graduate.yaml --out-dir out --pdf
```

PDF 编译默认使用 `xelatex`。如果本机没有 LaTeX 工具链，脚本会保留 `.tex` 并输出明确提示。

## 示例画像

- `new_graduate.yaml`：应届生，项目和教育背景权重更高。
- `project_heavy_intern.yaml`：AI 应用实习/项目型候选人，项目经历权重更高。
- `experienced_engineer.yaml`：有经验后端工程师，工作经历权重更高。

## 渲染逻辑

`render_resume.py` 会根据 profile 中的 `layout.emphasis` 和候选人经历自动决定 section 顺序：

- `experience`：突出工作/实习经历。
- `projects`：突出项目经历。
- `education`：突出教育背景。
- `balanced`：平衡展示。
- `auto`：根据 `target.seniority`、工作经历和项目数量推断。

渲染器负责 LaTeX 转义、section 排序、bullet 数量控制和 PDF 编译检查。agent 负责访谈、事实核对、内容补全和简历质量把关。
# resume-builder
