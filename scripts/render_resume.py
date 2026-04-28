#!/usr/bin/env python3
"""Render a Career Profile YAML file into a Chinese technical resume."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only without PyYAML
    yaml = None


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "templates" / "dev.tex"

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

TODO_PATTERN = re.compile(r"\bTODO\b\s*:?", re.IGNORECASE)


@dataclass(frozen=True)
class ProfileIssue:
    severity: str
    path: str
    message: str


@dataclass(frozen=True)
class EnvironmentIssue:
    severity: str
    component: str
    message: str
    install_hint: str = ""


def check_environment(template_path: Path, latex_engine: str = "xelatex", check_pdf: bool = True) -> list[EnvironmentIssue]:
    issues: list[EnvironmentIssue] = []

    def add(severity: str, component: str, message: str, install_hint: str = "") -> None:
        issues.append(
            EnvironmentIssue(
                severity=severity,
                component=component,
                message=message,
                install_hint=install_hint,
            )
        )

    if sys.version_info < (3, 10):
        add(
            "error",
            "python",
            f"Python 3.10+ is required; current version is {sys.version.split()[0]}",
            "Install Python 3.10 or newer, then rerun the command.",
        )
    else:
        add("ok", "python", f"Python {sys.version.split()[0]} is available")

    if yaml is None:
        add(
            "error",
            "PyYAML",
            "PyYAML is required to read Career Profile YAML files",
            "Ask before installing, then run: python -m pip install -r .agents/skills/resume-builder/scripts/requirements.txt",
        )
    else:
        version = getattr(yaml, "__version__", "available")
        add("ok", "PyYAML", f"PyYAML {version} is available")

    if template_path.exists():
        add("ok", "template", f"Template found: {template_path}")
    else:
        add("error", "template", f"Template not found: {template_path}")

    if check_pdf:
        executable = shutil.which(latex_engine)
        if executable:
            add("ok", latex_engine, f"LaTeX engine found: {executable}")
        else:
            add(
                "warn",
                latex_engine,
                f"LaTeX engine not found on PATH: {latex_engine}. PDF compilation will be unavailable.",
                "XeLaTeX is installed through a TeX distribution such as MiKTeX or TeX Live, not through pip.",
            )

    return issues


def report_environment_issues(issues: list[EnvironmentIssue]) -> None:
    for issue in issues:
        prefix = {
            "ok": "[ENV OK]",
            "warn": "[ENV WARN]",
            "error": "[ENV ERROR]",
        }.get(issue.severity, "[ENV WARN]")
        print(f"{prefix} {issue.component}: {issue.message}")
        if issue.install_hint:
            print(f"{prefix} {issue.component}: {issue.install_hint}")


def has_environment_errors(issues: list[EnvironmentIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


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


def is_todo_text(value: Any) -> bool:
    return isinstance(value, str) and bool(TODO_PATTERN.search(value))


def has_text(value: Any) -> bool:
    return bool(str(value or "").strip())


def has_usable_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return has_text(value)
    if isinstance(value, dict):
        return any(has_usable_content(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_usable_content(item) for item in value)
    return has_text(value)


def has_meaningful_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return has_text(value) and not is_todo_text(value)
    if isinstance(value, dict):
        return any(has_meaningful_content(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_meaningful_content(item) for item in value)
    return has_text(value)


def is_missing(value: Any) -> bool:
    return not has_meaningful_content(value)


def child_path(parent: str, key: str | int) -> str:
    if isinstance(key, int):
        return f"{parent}[{key}]" if parent else f"[{key}]"
    return f"{parent}.{key}" if parent else key


def todo_paths(value: Any, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        if is_todo_text(value):
            paths.append(path or "<root>")
    elif isinstance(value, dict):
        for key, item in value.items():
            paths.extend(todo_paths(item, child_path(path, str(key))))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            paths.extend(todo_paths(item, child_path(path, index)))
    return paths


def contact_values(profile: dict[str, Any]) -> list[Any]:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    return [
        basics.get("phone"),
        basics.get("email"),
        basics.get("location"),
        basics.get("github"),
        basics.get("website"),
        basics.get("linkedin"),
    ]


def usable_highlight_count(item: dict[str, Any]) -> int:
    return sum(1 for highlight in as_list(item.get("highlights")) if has_meaningful_content(highlight))


def validate_profile(profile: dict[str, Any]) -> list[ProfileIssue]:
    issues: list[ProfileIssue] = []

    def add(severity: str, path: str, message: str) -> None:
        issues.append(ProfileIssue(severity=severity, path=path, message=message))

    if profile.get("profile_version") != 1:
        add("error", "profile_version", "expected profile_version: 1")

    basics = profile.get("basics")
    if not isinstance(basics, dict):
        add("error", "basics", "expected a mapping with name and contact fields")
        basics = {}

    target = profile.get("target")
    if not isinstance(target, dict):
        add("error", "target", "expected a mapping with the target role")
        target = {}

    if is_missing(basics.get("name")):
        add("error", "basics.name", "candidate name is required")
    if is_missing(target.get("role")):
        add("error", "target.role", "target role is required")
    if not any(has_meaningful_content(value) for value in contact_values(profile)):
        add("error", "basics", "provide at least one reliable contact method")

    if not any(has_meaningful_content(profile.get(key)) for key in ("education", "experience", "projects")):
        add("error", "education|experience|projects", "provide at least one substantive section")

    skills = as_list(profile.get("skills"))
    usable_skill_groups = 0
    for index, group in enumerate(skills):
        path = child_path("skills", index)
        if not isinstance(group, dict):
            if has_meaningful_content(group):
                add("warn", path, "skill entries should be grouped by category")
                usable_skill_groups += 1
            continue
        if is_missing(group.get("category")):
            add("warn", child_path(path, "category"), "skill category is missing")
        if is_missing(group.get("items")):
            add("warn", child_path(path, "items"), "skill category has no usable items")
        elif has_meaningful_content(group.get("category")):
            usable_skill_groups += 1
    if usable_skill_groups == 0:
        add("error", "skills", "provide at least one skills category with usable items")

    for section in ("summary", "education", "experience", "projects", "skills", "achievements", "certifications"):
        if section in profile and not has_usable_content(profile.get(section)):
            add("warn", section, "section is present but has no usable content")

    for path in todo_paths(profile):
        add("warn", path, "contains unresolved TODO content")

    for section in ("education", "experience", "projects"):
        for index, item in enumerate(as_list(profile.get(section))):
            if not isinstance(item, dict):
                continue
            path = child_path(section, index)
            if not has_meaningful_content(item.get("start")) and not has_meaningful_content(item.get("end")):
                add("warn", path, "dates are missing or unresolved")

    for section in ("experience", "projects"):
        for index, item in enumerate(as_list(profile.get(section))):
            if not isinstance(item, dict):
                continue
            path = child_path(section, index)
            count = usable_highlight_count(item)
            if count < 2:
                add("warn", child_path(path, "highlights"), "expected at least 2 usable bullets for a major item")

    return issues


def report_profile_issues(issues: list[ProfileIssue]) -> None:
    for issue in issues:
        prefix = "[PROFILE ERROR]" if issue.severity == "error" else "[PROFILE WARN]"
        print(f"{prefix} {issue.path}: {issue.message}", file=sys.stderr)


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

    if seniority in {"experienced", "senior", "job_switch", "job-switch"} or fulltime_count >= 2:
        return "experience"
    if seniority in {
        "new_grad",
        "new-graduate",
        "graduate",
        "intern",
        "career_change",
        "career-change",
        "project_based",
        "project-based",
    } or len(projects) >= len(experience):
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
    return clean_join(contact_values(profile))


def title_line(profile: dict[str, Any]) -> str:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    target = profile.get("target") if isinstance(profile.get("target"), dict) else {}
    parts = [basics.get("title") or target.get("role")]
    if target.get("city"):
        parts.append(f"目标城市: {target.get('city')}")
    if target.get("direction"):
        parts.append("方向: " + "、".join(str(item) for item in as_list(target.get("direction"))[:4]))
    return clean_join(parts)


def photo_path(profile: dict[str, Any], profile_dir: Path | None = None) -> str:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    raw_path = basics.get("photo")
    if is_missing(raw_path):
        return ""

    path = Path(str(raw_path)).expanduser()
    if not path.is_absolute() and profile_dir is not None:
        path = profile_dir / path
    return path.resolve(strict=False).as_posix()


def render_tex(profile: dict[str, Any], template_path: Path, profile_dir: Path | None = None) -> tuple[str, str]:
    basics = profile.get("basics") if isinstance(profile.get("basics"), dict) else {}
    name = basics.get("name") or "TODO: 姓名"
    emphasis = infer_emphasis(profile)
    resolved_photo_path = photo_path(profile, profile_dir)
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{NAME}}": latex_escape(name),
        "{{TITLE_LINE}}": title_line(profile),
        "{{CONTACT_LINE}}": contact_line(profile),
        "{{PHOTO_FLAG}}": r"\hasphototrue" if resolved_photo_path else r"\hasphotofalse",
        "{{PHOTO_PATH}}": resolved_photo_path,
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

    command = [executable, "--disable-installer", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
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
    parser.add_argument("profile", type=Path, nargs="?", help="Path to Career Profile YAML.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="LaTeX template path.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory. Defaults to profile directory.")
    parser.add_argument("--pdf", action="store_true", help="Attempt PDF compilation after writing .tex.")
    parser.add_argument("--latex-engine", default="xelatex", help="LaTeX engine for PDF compilation.")
    parser.add_argument("--check-env", action="store_true", help="Check local rendering dependencies and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    template_path = args.template.resolve()

    if args.check_env:
        issues = check_environment(template_path, args.latex_engine, check_pdf=True)
        report_environment_issues(issues)
        return 1 if has_environment_errors(issues) else 0

    if args.profile is None:
        raise SystemExit("Profile path is required unless --check-env is used.")

    env_issues = check_environment(template_path, args.latex_engine, check_pdf=args.pdf)
    blocking_env_issues = [issue for issue in env_issues if issue.severity == "error"]
    if blocking_env_issues:
        report_environment_issues(blocking_env_issues)
        return 1

    profile_path = args.profile.resolve()
    out_dir = (args.out_dir or profile_path.parent).resolve()

    if not profile_path.exists():
        raise SystemExit(f"Profile not found: {profile_path}")
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    profile = load_profile(profile_path)
    issues = validate_profile(profile)
    report_profile_issues(issues)
    tex, emphasis = render_tex(profile, template_path, profile_path.parent)

    tex_path = out_dir / f"{safe_output_stem(profile_path)}.tex"
    tex_path.write_text(tex, encoding="utf-8", newline="\n")
    print(f"[OK] Wrote LaTeX: {tex_path}")
    print(f"[OK] Section emphasis: {emphasis}")

    if args.pdf:
        pdf_warnings = [
            issue
            for issue in env_issues
            if issue.severity == "warn" and issue.component == args.latex_engine
        ]
        if pdf_warnings:
            report_environment_issues(pdf_warnings)
        else:
            pdf_path = compile_pdf(tex_path, args.latex_engine)
            if pdf_path:
                print(f"[OK] Wrote PDF: {pdf_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
