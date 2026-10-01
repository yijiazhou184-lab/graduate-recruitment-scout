# Graduate Recruitment Scout

[中文](#中文) · [English](#english)

## 中文

一个可配置的 Codex Skill：从公开招聘页面发现、核验、去重和追踪校招、graduate 与 new-grad 全职岗位，并生成带来源证据的岗位库和增量简报。

它不会登录招聘网站、绕过验证码或代替用户投递。搜索覆盖取决于可用的联网工具、公开页面和用户配置，因此不会声称“穷尽全网”。

### 特点

- 官网和官方 ATS 优先，社区与聚合站只作为发现线索。
- 个人目标、毕业年份、地点、公司名单、评分权重和展示配额均可配置。
- URL 规范化、稳定 ID、去重、pending 合并和结果校验由确定性脚本完成。
- 支持中文和英文岗位查询，并可通过 preset 保存地区或行业策略。
- 默认只在新增、重要变化、临近截止或采集失败时产生行动提醒。

### 安装

把整个目录复制到个人或项目的 Skills 目录中：

```text
.agents/skills/graduate-recruitment-scout/
```

也可以将仓库克隆后，把本目录作为一个完整 Skill 使用。Skill 入口是 `SKILL.md`。

### 快速开始

```bash
python scripts/init_workspace.py --root ./job-search
python scripts/validate_profile.py ./job-search/profile.json
```

随后调用：

```text
Use $graduate-recruitment-scout to scan current graduate jobs using ./job-search/profile.json.
```

如需复用本项目最初的“中国大陆 AI 产品 + 香港科技分析岗”策略，可复制：

```text
presets/china-2027-ai-product-hk-tech.json
```

到工作区并按需修改。示例和 preset 都不是对用户背景的推断。

### 数据文件

默认工作区包含：

```text
job-search/
├── profile.json
├── graduate-jobs.csv
├── daily/
└── pending/
```

不要提交真实个人配置、岗位历史或报告。仓库内的 `.gitignore` 已覆盖常见本地输出，但提交前仍应人工检查。

### 测试

```bash
python -m unittest discover -s tests -v
python scripts/validate_profile.py assets/profile.example.json
```

## English

Graduate Recruitment Scout is a configurable Codex Skill for discovering, verifying, deduplicating, ranking, and tracking public graduate and new-grad jobs. It produces a source-backed CSV database and concise change reports.

The skill separates reusable workflow rules from personal preferences. Graduation years, locations, role families, employer watchlists, source policy, ranking weights, quotas, and notification behavior live in a profile rather than in the core prompt.

### Quick start

```bash
python scripts/init_workspace.py --root ./job-search
python scripts/validate_profile.py ./job-search/profile.json
python -m unittest discover -s tests -v
```

Use the Skill with a prompt such as:

```text
Use $graduate-recruitment-scout to find current full-time graduate product and technology roles matching ./job-search/profile.json.
```

### Privacy

Do not commit real profiles, application histories, notes, or generated reports. Examples in this repository are synthetic. The Skill never authorizes login, CAPTCHA bypass, application submission, or disclosure of personal information.

### Limitations

- Availability and coverage depend on public pages and the browsing tools available to the agent.
- Source layouts and recruiting terminology change over time.
- Classification and ranking support human review; they are not guarantees of eligibility or hiring outcomes.

## License

MIT. See [LICENSE](LICENSE).
