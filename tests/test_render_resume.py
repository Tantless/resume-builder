from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "render_resume.py"
EXAMPLES_DIR = SKILL_ROOT / "examples"
TEMPLATES_DIR = SKILL_ROOT / "assets" / "templates"

sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import render_resume  # noqa: E402


class RenderResumeTests(unittest.TestCase):
    def test_environment_check_reports_missing_pdf_engine_as_warning(self) -> None:
        with mock.patch("render_resume.shutil.which", return_value=None):
            issues = render_resume.check_environment(
                render_resume.DEFAULT_TEMPLATE,
                latex_engine="xelatex",
                check_pdf=True,
            )

        issue_map = {(issue.severity, issue.component) for issue in issues}

        self.assertIn(("ok", "python"), issue_map)
        self.assertIn(("ok", "PyYAML"), issue_map)
        self.assertIn(("ok", "template"), issue_map)
        self.assertIn(("warn", "xelatex"), issue_map)
        self.assertFalse(render_resume.has_environment_errors(issues))

    def test_cli_check_env_does_not_require_profile_path(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--check-env",
                "--latex-engine",
                "definitely_missing_xelatex_for_test",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[ENV OK] python:", result.stdout)
        self.assertIn("[ENV OK] PyYAML:", result.stdout)
        self.assertIn("[ENV WARN] definitely_missing_xelatex_for_test:", result.stdout)

    def test_latex_escape_handles_special_characters(self) -> None:
        escaped = render_resume.latex_escape(r"A&B_50%#{}~^\path")

        self.assertIn(r"A\&B\_50\%\#\{\}", escaped)
        self.assertIn(r"\textasciitilde{}", escaped)
        self.assertIn(r"\textasciicircum{}", escaped)
        self.assertIn(r"\textbackslash{}", escaped)

    def test_examples_render_without_profile_errors(self) -> None:
        expected_emphasis = {
            "new_graduate.yaml": "projects",
            "project_heavy_intern.yaml": "projects",
            "experienced_engineer.yaml": "experience",
        }

        for filename, emphasis in expected_emphasis.items():
            with self.subTest(filename=filename):
                profile = render_resume.load_profile(EXAMPLES_DIR / filename)
                issues = render_resume.validate_profile(profile)
                errors = [issue for issue in issues if issue.severity == "error"]
                tex, actual_emphasis = render_resume.render_tex(profile, render_resume.DEFAULT_TEMPLATE)

                self.assertEqual(errors, [])
                self.assertEqual(actual_emphasis, emphasis)
                self.assertIn(r"\begin{document}", tex)
                self.assertIn(r"\section*{", tex)

    def test_candidate_preset_seniority_aliases_infer_emphasis(self) -> None:
        cases = {
            "job_switch": "experience",
            "career_change": "projects",
            "project_based": "projects",
            "senior": "experience",
        }

        for seniority, expected in cases.items():
            with self.subTest(seniority=seniority):
                profile = {
                    "target": {"seniority": seniority},
                    "experience": [],
                    "projects": [],
                }

                self.assertEqual(render_resume.infer_emphasis(profile), expected)

    def test_all_templates_render_all_examples(self) -> None:
        template_paths = sorted(TEMPLATES_DIR.glob("*.tex"))
        example_paths = sorted(EXAMPLES_DIR.glob("*.yaml"))

        self.assertEqual(
            [path.name for path in template_paths],
            ["dev.tex", "fallback.tex"],
        )

        for template_path in template_paths:
            for example_path in example_paths:
                with self.subTest(template=template_path.name, example=example_path.name):
                    profile = render_resume.load_profile(example_path)
                    tex, _emphasis = render_resume.render_tex(profile, template_path)

                    self.assertIn(r"\begin{document}", tex)
                    self.assertIn(r"\section*{", tex)
                    self.assertNotIn("{{NAME}}", tex)
                    self.assertNotIn("{{TITLE_LINE}}", tex)
                    self.assertNotIn("{{CONTACT_LINE}}", tex)
                    self.assertNotIn("{{PHOTO_FLAG}}", tex)
                    self.assertNotIn("{{PHOTO_PATH}}", tex)
                    self.assertNotIn("{{SECTIONS}}", tex)

    def test_photo_path_sets_optional_photo_flag(self) -> None:
        profile = render_resume.load_profile(EXAMPLES_DIR / "new_graduate.yaml")
        profile["basics"]["photo"] = "assets/photo.jpg"

        tex, _emphasis = render_resume.render_tex(profile, render_resume.DEFAULT_TEMPLATE, EXAMPLES_DIR)

        self.assertIn(r"\hasphototrue", tex)
        self.assertIn((EXAMPLES_DIR / "assets" / "photo.jpg").resolve(strict=False).as_posix(), tex)
        self.assertNotIn("{{PHOTO_FLAG}}", tex)
        self.assertNotIn("{{PHOTO_PATH}}", tex)

    def test_validate_profile_reports_required_empty_todo_and_thin_bullets(self) -> None:
        profile = {
            "profile_version": 1,
            "target": {"role": "TODO: 目标岗位"},
            "basics": {"name": "", "email": "TODO: 邮箱"},
            "education": [],
            "projects": [
                {
                    "name": "简历生成系统",
                    "start": "",
                    "end": "",
                    "highlights": ["负责后端开发"],
                }
            ],
            "skills": [{"category": "编程语言", "items": []}],
        }

        issues = render_resume.validate_profile(profile)
        issue_map = {(issue.severity, issue.path, issue.message) for issue in issues}

        self.assertIn(("error", "basics.name", "candidate name is required"), issue_map)
        self.assertIn(("error", "target.role", "target role is required"), issue_map)
        self.assertIn(("error", "basics", "provide at least one reliable contact method"), issue_map)
        self.assertIn(("error", "skills", "provide at least one skills category with usable items"), issue_map)
        self.assertIn(("warn", "education", "section is present but has no usable content"), issue_map)
        self.assertIn(("warn", "target.role", "contains unresolved TODO content"), issue_map)
        self.assertIn(("warn", "basics.email", "contains unresolved TODO content"), issue_map)
        self.assertIn(("warn", "projects[0]", "dates are missing or unresolved"), issue_map)
        self.assertIn(
            ("warn", "projects[0].highlights", "expected at least 2 usable bullets for a major item"),
            issue_map,
        )

    def test_cli_reports_profile_issues_and_still_writes_tex(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            profile_path = temp_path / "incomplete.yaml"
            out_dir = temp_path / "out"
            profile_path.write_text(
                """
profile_version: 1
target:
  role: "TODO: 目标岗位"
basics:
  name: ""
projects:
  - name: 测试项目
    highlights:
      - 做了接口
skills: []
""".strip(),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(profile_path), "--out-dir", str(out_dir)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[OK] Wrote LaTeX:", result.stdout)
            self.assertIn("[PROFILE ERROR] basics.name: candidate name is required", result.stderr)
            self.assertIn("[PROFILE WARN] target.role: contains unresolved TODO content", result.stderr)
            self.assertTrue((out_dir / "incomplete.tex").exists())


if __name__ == "__main__":
    unittest.main()
