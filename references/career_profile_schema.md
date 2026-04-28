# Career Profile Schema

Use YAML as the source of truth. Keep the profile factual, editable, and reusable. Do not invent facts; use `TODO:` markers for unknown values.

## Top-Level Shape

```yaml
profile_version: 1
language: zh-CN
target:
  role: 后端开发工程师
  city: 上海
  seniority: new_grad
  direction:
    - Python
    - 云原生
layout:
  emphasis: auto
  max_pages: 1
basics:
  name: 张三
  title: 后端开发工程师
  phone: "13800000000"
  email: zhangsan@example.com
  location: 上海
  github: https://github.com/example
  photo: assets/photo.jpg
summary:
  - 具备 Python 后端、数据库和云原生项目经验。
education:
  - school: 示例大学
    degree: 本科
    major: 计算机科学与技术
    location: 杭州
    start: "2021.09"
    end: "2025.06"
    gpa: "3.7/4.0"
    honors:
      - 校级一等奖学金
    courses:
      - 数据结构
      - 操作系统
experience:
  - company: 示例科技
    role: 后端开发实习生
    location: 上海
    start: "2024.06"
    end: "2024.09"
    type: internship
    tech:
      - Python
      - PostgreSQL
    highlights:
      - 负责订单查询接口优化，将 P95 延迟从 420ms 降至 180ms。
projects:
  - name: 智能简历生成系统
    role: 后端负责人
    start: "2024.03"
    end: "2024.05"
    tech:
      - FastAPI
      - Redis
    link: https://github.com/example/resume
    description: 面向求职者的结构化简历生成工具。
    highlights:
      - 设计画像 YAML schema，支持 20+ 字段的简历数据复用。
skills:
  - category: 编程语言
    items:
      - Python
      - TypeScript
  - category: 后端与数据库
    items:
      - FastAPI
      - PostgreSQL
achievements:
  - ACM 校赛二等奖
certifications:
  - CET-6
metadata:
  notes:
    - TODO: 补充期望城市和薪资。
```

## Required Fields

- `profile_version`: Use `1`.
- `basics.name`: Candidate name.
- `target.role`: Target role or role family.
- At least one of `education`, `experience`, or `projects`.
- At least one `skills` category.

## Recommended Fields

- `basics.title`: Short professional title shown under the name.
- `basics.phone`, `basics.email`, `basics.location`.
- `basics.photo`: Optional local photo path for Chinese resume scenarios that require an ID-style photo. Omit it for ATS-friendly technical resumes.
- `summary`: 2-4 concise positioning bullets.
- `experience[].highlights` and `projects[].highlights`: concrete contributions and outcomes.
- `tech`: technologies used in each role/project.
- `target.seniority`: common values are `new_grad`, `intern`, `experienced`, `career_change`, `project_based`, or `senior`.
- `layout.emphasis`: `auto`, `projects`, `experience`, `education`, or `balanced`.

## Section Emphasis Rules

Use `layout.emphasis` when the user has a clear preference. Otherwise let the renderer infer:

- `experience`: at least two full-time roles, or seniority is `experienced`.
- `projects`: project count is greater than work experience count, or seniority is `new_grad` / `intern`.
- `education`: education is strong and practical experience is thin.
- `balanced`: mixed profile without a dominant strength.

The renderer may change section order and bullet budgets, but it should not hide factual content unless the profile explicitly marks it optional.

## Quality Rules

- Prefer action + method + result bullets.
- Quantify results when available: latency, cost, conversion, users, revenue, reliability, accuracy, ranking, scale.
- Keep each bullet to one clear claim.
- Separate individual contribution from team/project result.
- Mark uncertain content with `TODO:` instead of filling it creatively.
- Avoid unverifiable claims such as "精通" unless the user provides strong evidence.

## Renderer Gap Report

`scripts/render_resume.py` reports profile gaps without blocking `.tex` generation:

- `[PROFILE ERROR]`: missing `profile_version: 1`, `basics.name`, `target.role`, a reliable contact method, at least one substantive `education` / `experience` / `projects` section, or at least one usable skills category.
- `[PROFILE WARN]`: empty sections, unresolved `TODO:` values, missing dates on education/experience/project entries, non-categorized skills, or fewer than two usable bullets on a major experience/project.

Use these messages as the next follow-up checklist during resume interviews.
