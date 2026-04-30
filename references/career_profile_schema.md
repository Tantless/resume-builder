# 简历画像结构

画像 YAML 是简历数据的唯一事实来源。它要事实清晰、可编辑、可复用。不要编造信息；缺失或不确定的内容使用 `待补充：...` 标记。

## 语言约定

- 本 skill 面向中文技术简历，画像中的自然语言内容默认中文。
- 如果用户用英文或其他语言触发 skill，agent 的交互语言跟随用户；但画像 YAML、简历正文和待补充说明仍默认中文，除非用户明确要求生成非中文简历。
- YAML 字段名、枚举值、技术名词、链接和邮箱保持原样，例如 `profile_version`、`new_grad`、`Python`、`https://...`。

## 顶层结构

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
      - 设计画像 YAML 结构，支持 20+ 字段的简历数据复用。
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
    - 待补充：期望城市和薪资。
```

## 必填字段

- `profile_version`：固定为 `1`。
- `basics.name`：候选人姓名。
- `target.role`：目标岗位或岗位族。
- `education`、`experience`、`projects` 至少有一个包含实质内容。
- `skills` 至少有一个可用技能分类。

## 推荐字段

- `basics.title`：展示在姓名下方的职业标题。
- `basics.phone`、`basics.email`、`basics.location`：联系方式和所在地。
- `basics.photo`：可选本地照片相对路径，适合明确要求证件照的中文简历场景；技术岗或 ATS 投递场景默认省略。相对路径以画像 YAML 所在目录为基准，例如 `assets/photo.jpg`。
- `summary`：2-4 条简洁定位。
- `experience[].highlights` 和 `projects[].highlights`：具体贡献和结果。
- `tech`：每段经历或项目使用的技术。
- `target.seniority`：常用值为 `new_grad`、`intern`、`experienced`、`career_change`、`project_based`、`senior`。
- `layout.emphasis`：可选 `auto`、`projects`、`experience`、`education`、`balanced`。

## 版块侧重规则

用户有明确偏好时使用 `layout.emphasis`。没有偏好时由渲染器推断：

- `experience`：至少两段全职经历，或 `target.seniority` 为 `experienced` / `senior`。
- `projects`：项目数量多于工作经历，或 `target.seniority` 为 `new_grad` / `intern` / `career_change` / `project_based`。
- `education`：教育背景较强，实践经历较少。
- `balanced`：经历较均衡，没有明显单一优势。

渲染器可以调整版块顺序和要点数量预算，但不应隐藏事实内容，除非画像明确把该内容标为可选。

## 质量规则

- 优先写成“动作 + 方法/技术 + 难点/规模 + 结果”的要点。
- 有证据时量化结果：延迟、成本、转化、用户量、收入、稳定性、准确率、排名、规模等。
- 每条要点只表达一个清晰主张。
- 区分个人贡献和团队/项目结果。
- 不确定内容写 `待补充：...`，不要创造性补全。
- 避免无证据的“精通”等表述，除非用户提供了足够强的证明。

## 渲染器缺口报告

`scripts/render_resume.py` 会报告画像缺口，但不会因为可修复的内容问题阻止 `.tex` 生成：

- `[PROFILE ERROR]`：缺少 `profile_version: 1`、`basics.name`、`target.role`、可靠联系方式、至少一个实质性的 `education` / `experience` / `projects` 版块，或至少一个可用技能分类。
- `[PROFILE WARN]`：空版块、未解决的 `待补充：...`、教育/经历/项目缺少日期、技能没有分类，或主要经历/项目少于两条可用要点。

访谈时把这些消息作为下一轮追问清单。
