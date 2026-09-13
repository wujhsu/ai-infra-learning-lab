# AI Infra 学习实验室

以推理请求为主线的中文交互教材。面向会编程、刚接触 AI Infra 的读者。

**网站：** https://wujhsu.github.io/ai-infra-learning-lab/

24 个主线学习单元、5 个进阶专题、2 个背景专题、13 组工程实验；214 页会议讲义索引、53 张精选讲义页、6 个交互模型。所有正文静态生成；学习记录保存在浏览器，支持 JSON 预览导入、冲突处理及 JSON / Markdown 导出。

## 本地开发

需要 Node.js 24、npm、Python 3。`PUPPETEER_SKIP_DOWNLOAD=1 npm ci` 后运行 `npm run dev`。访问输出的 `/ai-infra-learning-lab/` 路径。

```bash
npm run check
npm test
python3 -m unittest discover -s tests -p 'test_*.py'
python3 labs/attention/attention.py
python3 scripts/package-labs.py
npm run build
npm run verify
npm run preview
```

Astro + MDX + TypeScript，React 只用于局部交互，Pagefind 在构建后生成中英文搜索，KaTeX / Shiki 展示数学与代码。Mermaid 已生成 SVG 并提交，阅读时无需 Mermaid 运行时；修改图源后设置 `CHROME_PATH` 并运行 `npm run diagrams`（脚本中提供 macOS Chrome 默认路径）。

## 内容与证据

- `src/content/lessons` / `topics` / `labs`：人工可编辑 MDX，稳定 ID 不能随标题变更。
- `src/data`：课程依赖、术语、官方来源和逐页讲义索引。
- `public/slides`：经过选择的普通与高清讲义图；公开构建不读取原始妙记。
- `public/diagrams`：可编辑 Mermaid 图源与渲染 SVG。
- `labs`：独立实验代码。CPU Attention 和流式客户端测试可以本机运行；GPU、Kubernetes 和多节点实验未在本机执行，不能把文中的示例作为实测。
- `docs`：编辑蓝图、证据策略、验证记录。

`scripts/import-materials.py` 仅供本地重新整理已有材料，不在 CI 中运行，也不打包原始妙记。`scripts/author-content.py` 是初始内容生成器；后续人工修订以 MDX 为准，不要用旧生成器覆盖修订。`scripts/check-sources.mjs` 检查可达性，不代替技术主张核验。

## 发布

GitHub Pages 使用 GitHub Actions 构建、测试并发布 `dist`。分支 `main` 推送触发部署，PR 只构建验证。若重命名仓库或使用自定义域名，同步修改 `astro.config.mjs` 的 `site` 与 `base`，以及验证脚本的路径基线。

## 权属与本地记录

本站原创代码按 MIT 许可，原创教程文字与自绘图按 CC BY 4.0 许可。会议 slide、商标、引用代码与第三方材料不在该再许可范围内，权利归原作者；每张讲义图标注场次、文件与页码。它们仅作为配合教学解读的引用，不能据此再许可完整讲义。本站不收集登录信息，不启用分析追踪，不上传个人学习记录。
