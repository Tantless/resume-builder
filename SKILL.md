---
name: resume-builder
description: "Create adaptive Chinese technical resumes from a user's free-form background, career profile YAML, or existing resume notes. Use when Codex or Claude Code should interview the user, extract a structured Career Profile, improve resume bullets, and render LaTeX/PDF resumes with the bundled template and renderer."
---

# Resume Builder

Build a modern Chinese technical resume from a user's background. Prefer a draft-first flow: ask the user to self-describe freely, extract a structured Career Profile, then ask only the follow-up questions needed to make the resume complete and persuasive.

## Workflow

1. Ask for a free-form self-introduction first.
   - Ask the user to include any known basics, target role, city, education, internships, work, projects, skills, awards, links, and constraints.
   - Do not start with a long fixed questionnaire.

2. Extract a draft Career Profile.
   - Read `references/career_profile_schema.md` before creating or editing profile YAML.
   - Save the profile as YAML when the user asks for a file or when rendering is needed.
   - Preserve uncertain fields with `TODO:` text rather than inventing facts.

3. Run adaptive follow-up.
   - Read `references/interview_flow.md` for question priorities.
   - Ask targeted questions for missing basics, unclear timelines, vague project contribution, missing metrics, skill depth, and target-role relevance.
   - Ask one focused question at a time unless the user explicitly wants a batch questionnaire.

4. Polish resume content.
   - Convert experience into action-result bullets.
   - Prefer quantified outcomes when evidence exists.
   - Keep claims defensible; do not exaggerate skill depth or responsibilities.
   - For Chinese resumes, keep bullets concise and information-dense.

5. Render the resume.
   - Use `scripts/render_resume.py` to convert profile YAML into LaTeX.
   - Use the bundled template at `assets/templates/modern_chinese_technical.tex` unless the user provides another template.
   - Generate PDF only when requested or useful; the script reports clearly if LaTeX tooling is missing.

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

## Output Expectations

For each resume build, provide:

- The profile YAML path used.
- The generated `.tex` path.
- The generated `.pdf` path when compilation succeeds.
- Any missing profile fields or content risks still worth improving.

## Resource Map

- `references/career_profile_schema.md`: canonical YAML schema and completeness rules.
- `references/interview_flow.md`: self-description prompt, follow-up priorities, and bullet-improvement rules.
- `scripts/render_resume.py`: deterministic YAML-to-LaTeX renderer with optional PDF compilation.
- `assets/templates/modern_chinese_technical.tex`: adaptive Chinese technical resume template.
- `examples/*.yaml`: sample profiles for student, project-heavy intern, and experienced engineer cases.
