#!/usr/bin/env python3
"""Render a Career Profile YAML file into a Chinese technical resume."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only without PyYAML
    yaml = None


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "templates" / "modern_chinese_technical.tex"

LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def load_profile(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise SystemExit(
            "PyYAML is required to read Career Profile YAML files.\n"
            "Install it with: python -m pip install PyYAML"
        )

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise SystemExit(f"Profile must be a YAML mapping: {path}")

    return data


def latex_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return "".join(LATEX_REPLACEMENTS.get(char, char) for char in text)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def clean_join(items: list[Any], sep: str = " | ") -> str:
    values = [latex_escape(item).strip() for item in items if str(item or "").strip()]
    return sep.join(values)


def date_range(item: dict[str, Any]) -> str:
    start = item.get("start")
    end = item.get("end")
    if start and end:
        return f"{start} -- {end}"
    return str(start or end or "")


def latex_section(title: str, body: str) -> str:
    body = body.strip()
    if not body:
        return ""
    return f"\\section*{{{latex_escape(title)}}}\n{body}\n"


def itemize(items: list[Any], limit: int | None = None) -> str:
    filtered = [item for item in items if str(item or "").strip()]
    if limit is not None:
        filtered = filtered[:limit]
    if not filtered:
        return ""
    lines = ["\\begin{itemize}"]
    lines.extend(f"  \\item {latex_escape(item)}" for item in filtered)
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def render_summary(profile: dict[str, Any], _emphasis: str) -> str:
    return latex_section("个人优势", itemize(as_list(profile.get("summary")), limit=4))


def render_education(profile: dict[str, Any], emphasis: str) -> str:
    entries: list[str] = []
    for edu in as_list(profile.get("education")):
        if not isinstance(edu, dict):
            continue
        school = latex_escape(edu.get("school", ""))
        date = latex_escape(date_range(edu))
        degree_parts = [edu.get("degree"), edu.get("major")]
        degree = clean_join(degree_parts, sep=" / ")
        location = latex_escape(edu.get("location", ""))
        entry = [f"\\resumeSubheading{{{school}}}{{{date}}}{{{degree}}}{{{location}}}"]
        details: list[str] = []
        if edu.get("gpa"):
            details.append(f"GPA: {edu.get('gpa')}")
        if edu.get("honors"):
            details.append("荣誉: " + "、".join(str(item) for item in as_list(edu.get("honors"))))
        if edu.get("courses") and emphasis in {"education", "projects", "balanced"}:
            details.append("相关课程: " + "、".join(str(item) for item in as_list(edu.get("courses"))[:6]))
        if details:
            entry.append(itemize(details, limit=3))
        entries.append("\n".join(entry))
    return latex_section("教育背景", "\n\n".join(entries))


def render_experience(profile: dict[str, Any], emphasis: str) -> str:
    limit = 4 if emphasis == "experience" else 2 if emphasis == "projects" else 3
    entries: list[str] = []
    for exp in as_list(profile.get("experience")):
        if not isinstance(exp, dict):
            continue
        company = latex_escape(exp.get("company", ""))
        date = latex_escape(date_range(exp))
        role = clean_join([exp.get("role"), "、".join(str(item) for item in as_list(exp.get("tech"))[:5])], sep=" | ")
        location = latex_escape(exp.get("location", ""))
        entry = [f"\\resumeSubheading{{{company}}}{{{date}}}{{{role}}}{{{location}}}"]
        entry.append(itemize(as_list(exp.get("highlights")), limit=limit))
        entries.append("\n".join(part for part in entry if part))
    return latex_section("工作与实习经历", "\n\n".join(entries))


def render_projects(profile: dict[str, Any], emphasis: str) -> str:
    limit = 4 if emphasis == "projects" else 2 if emphasis == "experience" else 3
    entries: list[str] = []
    for project in as_list(profile.get("projects")):
        if not isinstance(project, dict):
            continue
        name = latex_escape(project.get("name", ""))
        date = latex_escape(date_range(project))
        role = clean_join([project.get("role"), "、".join(str(item) for item in as_list(project.get("tech"))[:6])], sep=" | ")
        entry = [f"\\resumeProjectHeading{{{name}}}{{{date}}}{{{role}}}"]
        if project.get("description"):
            entry.append(latex_escape(project.get("description")))
        entry.append(itemize(as_list(project.get("highlights")), limit=limit))
        if project.get("link"):
            entry.append(f"{{\\small 项目链接: {latex_escape(project.get('link'))}}}")
        entries.append("\n".join(part for part in entry if part))
    return latex_section("项目经历", "\n\n".join(entries))


def render_skills(profile: dict[str, Any], _emphasis: str) -> str:
    rows: list[str] = []
    for group in as_list(profile.get("skills")):
        if isinstance(group, dict):
            category = latex_escape(group.get("category", "技能"))
            items = clean_join(as_list(group.get("items")), sep="、")
        else:
            category = "技能"
            items = latex_escape(group)
        if items:
            rows.append(f"\\textbf{{{category}}} & {items} \\\\")
    if not rows:
        return ""
    body = "\\begin{tabularx}{\\textwidth}{@{}p{2.8cm}X@{}}\n"
    body += "\n".join(rows)
    body += "\n\\end{tabularx}"
    return latex_section("专业技能", body)


def render_achievements(profile: dict[str, Any], _emphasis: str) -> str:
    return latex_section("奖项与成果", itemize(as_list(profile.get("achievements")), limit=5))


def render_certifications(profile: dict[str, Any], _emphasis: str) -> str:
    return latex_section("证书", itemize(as_list(profile.get("certifications")), limit=4))


RENDERERS = {
    "summary": render_summary,
    "skills": render_skills,
    "experience": render_experience,
    "projects": render_projects,
    "education": render_education,
    "achievements": render_achievements,
    "certifications": render_certifications,
}

SECTION_ORDERS = {
    "experience": ["summary", "skills", "experience", "projects", "education", "achievements", "certifications"],
    "projects": ["summary", "skills", "projects", "experience", "education", "achievements", "certifications"],
    "education": ["summary", "education", "projects", "skills", "experience", "achievements", "certifications"],
    "balanced": ["summary", "skills", "experience", "projects", "education", "achievements", "certifications"],
}


def infer_emphasis(profile: dict[str, Any]) -> str:
    layout = profile.get("layout") if isinstance(profile.get("layout"), dict) else {}
    requested = str(layout.get("emphasis", "auto")).lower()
    if requested in SECTION_ORDERS:
        return requested

    target = profile.get("target") if isinstance(profile.get("target"), dict) else {}
    seniority = str(target.get("seniority", "")).lower()
    experience = [item for item in as_list(profile.get("experience")) if isinstance(item, dict)]
    projects = [item for item in as_list(profile.get("projects")) if isinstance(item, dict)]
    fulltime_count = sum(1 for item in experience if str(item.get("type", "")).lower() == "fulltime")

    if seniority in {"experienced", "senior"} or fulltime_count >= 2:
        return "experience"
    if seniority in {"new_grad", "new-graduate", "graduate", "intern"} or len(projects) >= len(experience):
        return "projects"
    if profile.get("education") and not experience and not projects:
        return "education"
    return "balanced"


def render_sections(profile: dict[str, Any], emphasis: str) -> str:
    sections: list[str] = []
    for key in SECTION_ORDERS[emphasis]:
        rendered = RENDERERS[key](profile, emphasis)
        if rendered:
            sections.append(rendered)
    return "\n".join(sections)


def contact_line(profile: dict[str, Any]) -> str:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    contact_fields = [
        basics.get("phone"),
        basics.get("email"),
        basics.get("location"),
        basics.get("github"),
        basics.get("website"),
        basics.get("linkedin"),
    ]
    return clean_join(contact_fields)


def title_line(profile: dict[str, Any]) -> str:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    target = profile.get("target") if isinstance(profile.get("target"), dict) else {}
    parts = [basics.get("title") or target.get("role")]
    if target.get("city"):
        parts.append(f"目标城市: {target.get('city')}")
    if target.get("direction"):
        parts.append("方向: " + "、".join(str(item) for item in as_list(target.get("direction"))[:4]))
    return clean_join(parts)


def render_tex(profile: dict[str, Any], template_path: Path) -> tuple[str, str]:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    name = basics.get("name") or "TODO: 姓名"
    emphasis = infer_emphasis(profile)
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{NAME}}": latex_escape(name),
        "{{TITLE_LINE}}": title_line(profile),
        "{{CONTACT_LINE}}": contact_line(profile),
        "{{SECTIONS}}": render_sections(profile, emphasis),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template, emphasis


def safe_output_stem(profile_path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", profile_path.stem).strip("-")
    return stem or "resume"


def compile_pdf(tex_path: Path, engine: str) -> Path | None:
    executable = shutil.which(engine)
    if executable is None:
        print(f"[WARN] LaTeX engine not found: {engine}. Generated .tex only.", file=sys.stderr)
        return None

    command = [executable, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    result = subprocess.run(
        command,
        cwd=tex_path.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        log_path = tex_path.with_suffix(".latex.log")
        log_path.write_text(result.stdout, encoding="utf-8")
        print(f"[WARN] PDF compilation failed. LaTeX log: {log_path}", file=sys.stderr)
        return None

    pdf_path = tex_path.with_suffix(".pdf")
    return pdf_path if pdf_path.exists() else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Career Profile YAML resume.")
    parser.add_argument("profile", type=Path, help="Path to Career Profile YAML.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="LaTeX template path.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory. Defaults to profile directory.")
    parser.add_argument("--pdf", action="store_true", help="Attempt PDF compilation after writing .tex.")
    parser.add_argument("--latex-engine", default="xelatex", help="LaTeX engine for PDF compilation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_path = args.profile.resolve()
    template_path = args.template.resolve()
    out_dir = (args.out_dir or profile_path.parent).resolve()

    if not profile_path.exists():
        raise SystemExit(f"Profile not found: {profile_path}")
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    profile = load_profile(profile_path)
    tex, emphasis = render_tex(profile, template_path)

    tex_path = out_dir / f"{safe_output_stem(profile_path)}.tex"
    tex_path.write_text(tex, encoding="utf-8", newline="\n")
    print(f"[OK] Wrote LaTeX: {tex_path}")
    print(f"[OK] Section emphasis: {emphasis}")

    if args.pdf:
        pdf_path = compile_pdf(tex_path, args.latex_engine)
        if pdf_path:
            print(f"[OK] Wrote PDF: {pdf_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
