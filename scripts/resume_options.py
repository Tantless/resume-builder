#!/usr/bin/env python3
"""列出 resume-builder skill 的首次运行选项。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = SKILL_ROOT / "assets" / "templates"
DEFAULT_TEMPLATE_ID = "dev"


TEMPLATE_METADATA = {
    "dev": {
        "label": "dev",
        "description": "默认模板，简洁清爽，适合主要精进和日常使用。",
        "style": "clean",
    },
    "fallback": {
        "label": "fallback",
        "description": "保守模板，朴素稳定，适合需要更低风险版式时使用。",
        "style": "conservative",
    },
}


PHOTO_MODES: list[dict[str, Any]] = [
    {
        "id": "no_photo",
        "label": "无照片",
        "description": "默认选择，适合技术岗、互联网、外企和 ATS 投递场景。",
        "default": True,
        "profile_defaults": {"basics": {"photo": None}},
    },
    {
        "id": "with_photo",
        "label": "有照片",
        "description": "适合明确要求证件照的中文简历场景；渲染前需要用户提供本地图片路径。",
        "default": False,
        "profile_defaults": {"basics": {"photo": "待补充：本地照片路径"}},
    },
]


CANDIDATE_PRESETS: list[dict[str, Any]] = [
    {
        "id": "auto",
        "label": "不确定/自动判断",
        "description": "默认选择；先收集背景，再由 agent 根据经历自动判断突出方向。",
        "default": True,
        "profile_defaults": {"layout": {"emphasis": "auto"}},
        "follow_up_focus": ["目标岗位", "最有含金量的经历", "是否有可量化成果"],
    },
    {
        "id": "new_grad",
        "label": "应届生/校招生",
        "description": "突出教育、项目、实习、竞赛和基础技术栈。",
        "default": False,
        "profile_defaults": {
            "target": {"seniority": "new_grad"},
            "layout": {"emphasis": "projects"},
        },
        "follow_up_focus": ["毕业时间", "项目贡献", "实习/竞赛/课程亮点"],
    },
    {
        "id": "intern",
        "label": "找实习",
        "description": "突出项目、课程、竞赛和可验证的技术栈掌握情况。",
        "default": False,
        "profile_defaults": {
            "target": {"seniority": "intern"},
            "layout": {"emphasis": "projects"},
        },
        "follow_up_focus": ["可到岗时间", "项目深度", "基础能力证明"],
    },
    {
        "id": "job_switch",
        "label": "社招跳槽",
        "description": "突出工作经历、业务结果、稳定交付和岗位匹配度。",
        "default": False,
        "profile_defaults": {
            "target": {"seniority": "experienced"},
            "layout": {"emphasis": "experience"},
        },
        "follow_up_focus": ["最近两段工作", "业务指标", "个人贡献边界"],
    },
    {
        "id": "career_change",
        "label": "转岗",
        "description": "突出目标岗位相关项目、可迁移能力和补足短板的证据。",
        "default": False,
        "profile_defaults": {
            "target": {"seniority": "career_change"},
            "layout": {"emphasis": "projects"},
        },
        "follow_up_focus": ["转岗目标", "相关项目", "原经历中的可迁移能力"],
    },
    {
        "id": "project_based",
        "label": "项目型/作品集导向",
        "description": "突出项目复杂度、技术决策、作品链接和可演示成果。",
        "default": False,
        "profile_defaults": {
            "target": {"seniority": "project_based"},
            "layout": {"emphasis": "projects"},
        },
        "follow_up_focus": ["核心项目", "技术难点", "作品链接或演示结果"],
    },
    {
        "id": "senior",
        "label": "高年限/负责人",
        "description": "突出影响范围、架构决策、团队协作和业务结果。",
        "default": False,
        "profile_defaults": {
            "target": {"seniority": "senior"},
            "layout": {"emphasis": "experience"},
        },
        "follow_up_focus": ["负责范围", "架构/团队影响", "关键业务结果"],
    },
]


def relative_to_skill(path: Path) -> str:
    return path.relative_to(SKILL_ROOT).as_posix()


def discover_templates() -> list[dict[str, Any]]:
    templates: list[dict[str, Any]] = []
    for template_path in sorted(TEMPLATES_DIR.glob("*.tex")):
        template_id = template_path.stem
        metadata = TEMPLATE_METADATA.get(
            template_id,
            {
                "label": template_id,
                "description": "自定义内置模板。",
                "style": "custom",
            },
        )
        templates.append(
            {
                "id": template_id,
                "label": metadata["label"],
                "filename": template_path.name,
                "path": relative_to_skill(template_path),
                "description": metadata["description"],
                "style": metadata["style"],
                "supports_photo": True,
                "default": template_id == DEFAULT_TEMPLATE_ID,
            }
        )
    return templates


def build_options() -> dict[str, Any]:
    return {
        "version": 1,
        "defaults": {
            "photo_mode": "no_photo",
            "template": DEFAULT_TEMPLATE_ID,
            "candidate_preset": "auto",
        },
        "photo_modes": PHOTO_MODES,
        "templates": discover_templates(),
        "candidate_presets": CANDIDATE_PRESETS,
    }


def print_human(options: dict[str, Any]) -> None:
    print("照片模式：")
    for item in options["photo_modes"]:
        marker = "（默认）" if item.get("default") else ""
        print(f"- {item['id']}: {item['label']}{marker}")

    print("\n模板：")
    for item in options["templates"]:
        marker = "（默认）" if item.get("default") else ""
        print(f"- {item['id']}: {item['description']}{marker}")

    print("\n候选人预设：")
    for item in options["candidate_presets"]:
        marker = "（默认）" if item.get("default") else ""
        print(f"- {item['id']}: {item['label']}{marker}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="列出 resume-builder 首次运行选项。")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出选项。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    options = build_options()
    if args.json:
        print(json.dumps(options, ensure_ascii=False, indent=2))
    else:
        print_human(options)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
