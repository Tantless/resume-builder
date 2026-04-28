from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "resume_options.py"

sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import resume_options  # noqa: E402


class ResumeOptionsTests(unittest.TestCase):
    def test_discovers_current_templates_with_default(self) -> None:
        options = resume_options.build_options()
        templates = options["templates"]

        self.assertEqual([item["id"] for item in templates], ["dev", "fallback"])
        self.assertEqual(options["defaults"]["template"], "dev")
        self.assertEqual(
            [item["id"] for item in templates if item["default"]],
            ["dev"],
        )
        self.assertTrue(all(item["supports_photo"] for item in templates))

    def test_candidate_presets_expose_profile_defaults(self) -> None:
        options = resume_options.build_options()
        presets = {item["id"]: item for item in options["candidate_presets"]}

        self.assertEqual(options["defaults"]["candidate_preset"], "auto")
        self.assertIn("auto", presets)
        self.assertEqual(presets["new_grad"]["profile_defaults"]["target"]["seniority"], "new_grad")
        self.assertEqual(presets["intern"]["profile_defaults"]["layout"]["emphasis"], "projects")
        self.assertEqual(presets["job_switch"]["profile_defaults"]["layout"]["emphasis"], "experience")
        self.assertEqual(presets["career_change"]["profile_defaults"]["target"]["seniority"], "career_change")
        self.assertEqual(presets["senior"]["profile_defaults"]["layout"]["emphasis"], "experience")

    def test_photo_modes_have_safe_default(self) -> None:
        options = resume_options.build_options()

        self.assertEqual(options["defaults"]["photo_mode"], "no_photo")
        self.assertEqual(
            [item["id"] for item in options["photo_modes"] if item["default"]],
            ["no_photo"],
        )

    def test_cli_outputs_json(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["defaults"]["template"], "dev")
        self.assertIn("templates", payload)
        self.assertIn("candidate_presets", payload)


if __name__ == "__main__":
    unittest.main()
