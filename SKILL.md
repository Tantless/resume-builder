---
name: resume-builder
description: "Create adaptive Chinese technical resumes from a user's free-form background, career profile YAML, or existing resume notes. Use when Codex or Claude Code should interview the user, extract a structured Career Profile, improve resume bullets, and render LaTeX/PDF resumes with the bundled template and renderer."
---

# Resume Builder

Build a modern Chinese technical resume from a user's background. Start by choosing compact defaults, then prefer a draft-first flow: ask the user to self-describe freely, extract a structured Career Profile, and ask only the follow-up questions needed to make the resume complete and persuasive.

## Workflow

1. Offer first-run mode selection before the detailed resume interview.
   - If the user already provided explicit photo mode, template, and candidate type, acknowledge those choices and continue without repeating the selector.
   - Otherwise run `python .agents/skills/resume-builder/scripts/resume_options.py --json` to get the current photo modes, templates, candidate presets, and defaults.
   - Present a compact selector in one message: photo mode, template, and candidate type. The user should be able to answer all three at once.
   - Make clear that "默认", "随便", or "不确定" is acceptable. Use `no_photo`, `dev`, and `auto` unless the user's background clearly implies a better candidate preset.
   - Map the selected candidate preset into the draft profile using the tool's `profile_defaults`, especially `target.seniority` and `layout.emphasis`.
   - For `with_photo`, ask for a local image path before final rendering. Do not invent a `basics.photo` value.

2. Check the local environment before rendering.
   - Run `python .agents/skills/resume-builder/scripts/render_resume.py --check-env` before the first render in a session.
   - If the user wants PDF output, confirm whether `xelatex` is available from the environment check.
   - If `PyYAML` is missing, ask the user before installing it into the active Python environment.
   - If `xelatex` is missing, explain that it comes from a TeX distribution such as MiKTeX or TeX Live, not from `pip install xelatex`; ask before helping install system-level tooling.
   - If the user does not want to install LaTeX tooling, render `.tex` only.

3. Ask for a free-form self-introduction.
   - Ask the user to include any known basics, target role, city, education, internships, work, projects, skills, awards, links, and constraints.
   - Do not start with a long fixed questionnaire.

4. Extract a draft Career Profile.
   - Read `references/career_profile_schema.md` before creating or editing profile YAML.
   - Save the profile as YAML when the user asks for a file or when rendering is needed.
   - Preserve uncertain fields with `TODO:` text rather than inventing facts.

5. Run adaptive follow-up.
   - Read `references/interview_flow.md` for question priorities.
   - Ask targeted questions for missing basics, unclear timelines, vague project contribution, missing metrics, skill depth, and target-role relevance.
   - Ask one focused question at a time unless the user explicitly wants a batch questionnaire.

6. Polish resume content.
   - Convert experience into action-result bullets.
   - Prefer quantified outcomes when evidence exists.
   - Keep claims defensible; do not exaggerate skill depth or responsibilities.
   - For Chinese resumes, keep bullets concise and information-dense.

7. Render the resume.
   - Use `scripts/render_resume.py` to convert profile YAML into LaTeX.
   - Use the bundled default template at `assets/templates/dev.tex` unless the user provides another template.
   - Review any `[PROFILE ERROR]` or `[PROFILE WARN]` output and report remaining content gaps to the user.
   - Generate PDF only when requested or useful; the script reports clearly if LaTeX tooling is missing.

## First-Run Selector Shape

After reading `resume_options.py --json`, present choices in this compact shape:

```text
我先帮你设定简历默认模式，直接回复编号或关键词即可，也可以说“默认”。

1. 照片：无照片 / 有照片
2. 模板：dev / fallback
3. 求职类型：不确定自动判断 / 应届生 / 找实习 / 社招跳槽 / 转岗 / 项目型 / 高年限

默认：无照片 + dev + 自动判断。选完后请直接贴你的背景，我会继续整理简历。
```

Use the actual template and preset names returned by the options tool if they differ from this example.

## Environment Check

```bash
python .agents/skills/resume-builder/scripts/render_resume.py --check-env
```

The command reports:

- `[ENV OK]` for available runtime pieces.
- `[ENV ERROR]` for required `.tex` rendering dependencies that must be fixed before rendering.
- `[ENV WARN]` for optional PDF tooling gaps such as missing `xelatex`.

## Render Command

```bash
python .agents/skills/resume-builder/scripts/render_resume.py path/to/profile.yaml --out-dir path/to/output
```

Generate PDF with XeLaTeX if available:

```bash
python .agents/skills/resume-builder/scripts/render_resume.py path/to/profile.yaml --out-dir path/to/output --pdf
```

If `PyYAML` is missing, install it in the active Python environment:

```bash
python -m pip install -r .agents/skills/resume-builder/scripts/requirements.txt
```

Do not use `pip install xelatex`. Install MiKTeX, TeX Live, or another TeX distribution if PDF compilation is required.

## Output Expectations

For each resume build, provide:

- The profile YAML path used.
- The generated `.tex` path.
- The generated `.pdf` path when compilation succeeds.
- Any missing profile fields or content risks still worth improving.
- Any renderer-reported profile errors or warnings that need user follow-up.
- Any environment warnings and whether the user chose `.tex` only or PDF setup.

## Resource Map

- `references/career_profile_schema.md`: canonical YAML schema and completeness rules.
- `references/interview_flow.md`: self-description prompt, follow-up priorities, and bullet-improvement rules.
- `scripts/resume_options.py`: deterministic first-run options provider for templates, photo modes, candidate presets, and defaults.
- `scripts/render_resume.py`: deterministic YAML-to-LaTeX renderer with optional PDF compilation.
- `assets/templates/dev.tex`: actively refined clean Chinese technical resume template.
- `assets/templates/fallback.tex`: conservative fallback template.
- `examples/*.yaml`: sample profiles for student, project-heavy intern, and experienced engineer cases.
