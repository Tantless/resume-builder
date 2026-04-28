# Interview Flow

Use a compact-defaults, draft-first interview. The goal is to minimize form-filling while still producing enough structure for a strong resume.

## First-Run Mode Selection

Before asking for a full background paragraph, run:

```bash
python .agents/skills/resume-builder/scripts/resume_options.py --json
```

Use the returned options to present one compact selector covering:

- Photo mode: default to no-photo unless the user needs a Chinese photo resume.
- Template: default to `dev` unless the user asks for a conservative fallback.
- Candidate preset: default to auto when the user is unsure.

Do not show a selector if the user's first message already gives clear choices for photo mode, template, and candidate type.

If the user says "默认", "随便", or "不确定", continue with:

- `photo_mode: no_photo`
- `template: dev`
- `candidate_preset: auto`

When a non-auto candidate preset is selected, apply its `profile_defaults` while drafting the Career Profile. For `with_photo`, ask for the local image path before final rendering.

## Opening Prompt

After mode selection, ask the user:

```text
请先用一段话自由介绍你的求职背景。能想到什么就写什么：目标岗位/城市/薪资期望、学校和专业、实习或工作经历、项目经历、技术栈、奖项证书、Github/作品链接、你想突出的优势，以及你不想放进简历的内容。先不用整理格式，我会按刚才的默认模式提取成简历画像，并继续追问缺失信息。
```

## Extraction Pass

After the self-description:

1. Extract a draft Career Profile using `career_profile_schema.md`.
2. Keep facts in the user's wording when precision matters.
3. Normalize dates only when obvious.
4. Use `TODO:` for missing or uncertain fields.
5. Summarize what was extracted before asking follow-up.

## Follow-Up Priorities

Ask one focused question at a time. Prioritize:

1. Contact and target basics needed to render the header.
2. Timeline gaps: school dates, role dates, project dates.
3. Role contribution: "你具体负责哪部分？"
4. Quantified impact: "有没有延迟、准确率、用户量、成本、排名、收入、效率等指标？"
5. Technical depth: "这个技术你是调用、配置、二次开发，还是自己实现核心逻辑？"
6. Resume positioning: "这段经历更想突出工程能力、业务结果、算法能力，还是协作推进？"
7. Sensitive or optional content: salary, age, photo, political status, GPA, weak grades.

## Bullet Improvement Pattern

Transform rough notes into bullets using:

```text
动作 + 技术/方法 + 规模/难点 + 结果/影响
```

Examples:

- Rough: 做了缓存优化。
- Better: 基于 Redis 为商品详情接口增加多级缓存，将高峰期 P95 延迟从 380ms 降至 140ms。

- Rough: 负责模型训练。
- Better: 清洗 12 万条标注样本并调优 LightGBM 特征组合，使简历岗位匹配 AUC 从 0.78 提升至 0.86。

## Completeness Check

Before rendering, check:

- Header has name plus at least one reliable contact method.
- Target role is known.
- At least one substantive section exists: education, experience, or projects.
- Skills are grouped by category.
- Each major experience/project has at least two usable bullets or a clear TODO.
- Dates are present or intentionally omitted.
- Claims are not overstated relative to user evidence.

## When to Render

Render when:

- The user asks for a resume file.
- The core profile is complete enough for a useful first draft.
- The user wants to review layout before continuing content refinement.

After rendering, report remaining content gaps separately from renderer success.
