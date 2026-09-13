# AI Infra 系统学习库

面向熟悉后端、刚学习模型与 GPU 的读者。以可解释、可实现、可测量、可恢复的能力组织内容；会议材料是可选参考。

- 38 章连续课程：模型与学习 → 硬件 → 单机训练 → 算子编译 → 通信 → 分布式训练 → 推理 → 优化 → 平台 → 生产。
- 5 个递进项目、6 个固定版本源码任务、7 个进阶研究专题。
- 正文术语卡片、共享数值图解、7 类交互演示、可放大 slide、搜索与本地学习记录。
- 全部正文为静态 HTML；学习体验待真实试读。GPU/集群实验未在本次环境运行。

## 开发

Node 24：`npm ci`，`npm run dev`。生产检查：`npm run check`、`npm test`、`python3 scripts/package-labs.py`、`npm run build`、`npm run verify`。

Python 3.12 独立环境：`pip install -r labs/requirements.txt`，然后 `python -m unittest discover -s tests -p 'test_*.py'`。两个分布式 CPU 对照命令见项目三。

## 内容接口

`src/data/reading.json` 管理独立章节顺序；`stages.json` 管理能力阶段；`concepts.json` 与 `glossary.json` 管理首次讲解、别名和术语定义。`chapters/projects/code/advanced` 四个 MDX 集合有稳定 ID、修订版本、前置概念与验证状态。数值图与演示共享 `toy-model.json` 和纯函数。

## 发布与数据

GitHub Actions 干净构建并部署 GitHub Pages，所有路径兼容 `/ai-infra-learning-lab/`。旧教程正文、目录、路由及归档映射已删除；旧 URL 正常 404，无迁移。新版记录键为 `ai-infra-library:v2`，不读取旧进度。

只发布精选讲义页与整理后的索引；完整妙记及个人元数据留在外部原始资料目录。讲义权利属于原作者。CPU 实测记录见 `docs/runs/`，内容与工程验收边界见 `docs/validation.md`。
