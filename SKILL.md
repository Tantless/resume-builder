---
name: resume-builder
description: "为 Codex、Claude Code、OpenClaw 等 agent CLI 创建中文技术简历。用户提供自由背景、已有简历、项目经历或求职目标时使用：先做模式选择，再访谈补全信息，抽取中文简历画像 YAML，优化经历表述，并用随包模板渲染 LaTeX/PDF。"
---

# 中文技术简历构建器

根据用户背景生成中文技术简历。优先采用“默认配置 + 先出草稿 + 自适应追问”的流程：让用户自由描述经历，抽取结构化简历画像，只追问影响简历完整度和说服力的缺口。

## 语言规则

- 交互语言跟随用户输入语言；如果用户没有明确语言偏好，默认使用中文。
- 本 skill 的目标产物是中文技术简历。简历画像 YAML、简历正文、待补充标记、渲染输出中的自然语言默认使用中文。
- 保留必要的技术标识、字段名、模板名和枚举值，例如 `profile_version`、`target.seniority`、`dev`、`new_grad`、`Python`。
- 不确定信息使用中文标记 `待补充：...`。

## 路径规则

- 本文件所在目录就是 skill 根目录。所有资源路径说明都以 skill 根目录为基准。
- 不要在命令中写死用户主目录、项目根目录或某个 agent CLI 的安装目录。
- 执行随包脚本前，先进入 skill 根目录，再使用相对路径：

```bash
python scripts/resume_options.py --json
python scripts/render_resume.py --check-env
```

- 用户画像和输出目录也使用相对路径示例，例如 `profiles/zhangsan.yaml`、`output/zhangsan/`。

## 工作流

1. 先做首次模式选择。
   - 如果用户已经明确照片模式、模板和候选人类型，确认这些选择后继续，不重复展示选择器。
   - 否则在 skill 根目录运行 `python scripts/resume_options.py --json`，读取当前照片模式、模板、候选人预设和默认值。
   - 用一条消息给出紧凑选择器：照片模式、模板、候选人类型。让用户可以一次性回答三项。
   - 明确说明“默认”“随便”“不确定”都可以。除非用户背景明显更适合其他预设，否则使用 `no_photo`、`dev`、`auto`。
   - 把候选人预设的 `profile_defaults` 应用到草稿画像，尤其是 `target.seniority` 和 `layout.emphasis`。
   - 如果选择 `with_photo`，最终渲染前向用户索要本地照片相对路径；不要编造 `basics.photo`。

2. 渲染前检查本地环境。
   - 每个会话第一次渲染前，在 skill 根目录运行 `python scripts/render_resume.py --check-env`。
   - 如果用户需要 PDF，确认环境检查中是否存在 `xelatex`。
   - 如果缺少 `PyYAML`，先征得用户同意，再在当前 Python 环境安装。
   - 如果缺少 `xelatex`，说明它来自 MiKTeX、TeX Live 等 TeX 发行版，不是通过 `pip install xelatex` 安装；协助安装系统级工具前先询问用户。
   - 如果用户不想安装 LaTeX 工具，只生成 `.tex`。

3. 让用户自由介绍背景。
   - 请用户尽量包含：基本信息、目标岗位、城市、教育、实习、工作、项目、技术栈、奖项、链接和约束。
   - 不要一开始就发长问卷。

4. 抽取简历画像。
   - 创建或编辑画像 YAML 前，先读 `references/career_profile_schema.md`。
   - 用户要求保存文件或需要渲染时，把画像保存为 YAML。
   - 不编造事实；未知或不确定字段写 `待补充：...`。
   - 画像中的自然语言内容默认中文，包括摘要、经历要点、备注和待补充说明。

5. 自适应追问。
   - 追问前读 `references/interview_flow.md`。
   - 优先追问缺失基本信息、时间线、项目贡献、量化指标、技术深度和目标岗位匹配度。
   - 默认一次只问一个聚焦问题；用户明确想要批量问卷时再合并问题。

6. 打磨简历内容。
   - 把经历整理为“动作 + 方法/技术 + 难点/规模 + 结果”的要点。
   - 有证据时优先量化成果。
   - 保持主张可证实，不夸大技能深度或职责边界。
   - 中文简历要点保持精炼、信息密度高。

7. 渲染简历。
   - 在 skill 根目录使用 `scripts/render_resume.py` 把画像 YAML 转为 LaTeX。
   - 默认模板是 `assets/templates/dev.tex`，除非用户选择其他模板。
   - 检查 `[PROFILE ERROR]` 和 `[PROFILE WARN]` 输出，并把剩余内容缺口告诉用户。
   - 仅在用户要求或确实有用时生成 PDF；缺少 LaTeX 工具时脚本会保留 `.tex`。

## 首次选择器形状

读取 `resume_options.py --json` 后，按这个紧凑形状展示选项：

```text
我先帮你设定简历默认模式，直接回复编号或关键词即可，也可以说“默认”。

1. 照片：无照片 / 有照片
2. 模板：dev / fallback
3. 求职类型：不确定自动判断 / 应届生 / 找实习 / 社招跳槽 / 转岗 / 项目型 / 高年限

默认：无照片 + dev + 自动判断。选完后请直接贴你的背景，我会继续整理简历。
```

如果选项工具返回的模板名或预设名不同，使用工具返回的真实名称。

## 环境检查

在 skill 根目录执行：

```bash
python scripts/render_resume.py --check-env
```

命令会报告：

- `[ENV OK]`：运行时组件可用。
- `[ENV ERROR]`：生成 `.tex` 必需的依赖缺失，需要修复后再渲染。
- `[ENV WARN]`：可选 PDF 工具缺失，例如没有 `xelatex`。

## 渲染命令

在 skill 根目录执行，所有路径都写相对路径：

```bash
python scripts/render_resume.py profiles/zhangsan.yaml --out-dir output/zhangsan
```

如果环境中有 XeLaTeX，可以生成 PDF：

```bash
python scripts/render_resume.py profiles/zhangsan.yaml --out-dir output/zhangsan --pdf
```

如果缺少 `PyYAML`，征得用户同意后，在 skill 根目录执行：

```bash
python -m pip install -r scripts/requirements.txt
```

不要使用 `pip install xelatex`。需要 PDF 编译时，安装 MiKTeX、TeX Live 或其他 TeX 发行版。

## 输出汇报

每次构建简历后，向用户汇报：

- 使用的画像 YAML 相对路径。
- 生成的 `.tex` 相对路径。
- PDF 编译成功时，生成的 `.pdf` 相对路径。
- 仍值得补充的画像字段或内容风险。
- 渲染器报告的画像错误或警告，以及后续追问建议。
- 环境警告，以及当前选择是只生成 `.tex` 还是继续配置 PDF。

## 资源地图

- `references/career_profile_schema.md`：简历画像 YAML 的权威结构、完整性规则和中文内容要求。
- `references/interview_flow.md`：自由描述提示、追问优先级和经历要点打磨规则。
- `scripts/resume_options.py`：首次模式选择的确定性选项来源。
- `scripts/render_resume.py`：确定性的 YAML 到 LaTeX 渲染器，支持可选 PDF 编译。
- `assets/templates/dev.tex`：默认中文技术简历模板。
- `assets/templates/fallback.tex`：更保守的中文技术简历模板。
- `examples/*.yaml`：不同候选人类型的中文画像示例。
