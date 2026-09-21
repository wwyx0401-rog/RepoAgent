# RepoAgent

  一个能读懂代码仓库的 Agent。**当前进度：第 1 周 —— 仓库遍历工具。**

  ## 现在能做什么

  `tree.py` 接收一个本地仓库路径，打印它的文件树，并按语言统计文件数和代码行数。

  ## 用法

  需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

  ```bash
  git clone git@github.com:wwyx0401-rog/RepoAgent.git
  cd RepoAgent
  uv sync
  python tree.py <仓库路径>
  ```

  Windows 下用 `.venv\Scripts\python.exe`，macOS/Linux 下用 `.venv/bin/python`。

  ### 示例输出

  ```console
  $ python tree.py D:/javaweb/helloweb
  D:\javaweb\helloweb/
   ├── src/
   |     └── main/
   |         ├── java/
   |        |     └── com/
   |        |         └── example/
   |        |             └── web/
   |        |                 └── HelloServlet.java
   |         └── webapp/
   |             ├── css/
   |            |     └── style.css
   |             ├── WEB-INF/
   |            |     └── web.xml
   |             └── index.html
   ├── .gitignore
   ├── build.bat
   ├── deploy.bat
   ├── pom.xml
   └── README.md

  语言           文件数       行数
  --------
  Markdown       1      192
  CSS            1      132
  Java           1       78
  HTML           1       44
  --------
  总计            4      446
  ```

  ## 已处理的边界情况

  - 跳过 `.git`、`.venv`、`node_modules`、`target` 等非源码目录
  - 跳过二进制文件（读前 8KB，含 `\x00` 即判定为二进制）
  - 跳过超过 1MB 的大文件，避免卡死
  - 用 `rglob` 递归遍历，用 `defaultdict` 累计各语言行数

  ## 路线图

  - [x] 第 1 周：Git 工作流 + 仓库遍历工具
  - [ ] 第 2 周：用 `subprocess` 调 `git clone`，支持直接传仓库链接
  - [ ] 第 3-4 周：最简 RAG（Embedding + Chroma）
  - [ ] 第 5-6 周：Agent 化（LangGraph + 工具调用）
  - [ ] 第 7-8 周：AST 切片 + BM25 混合检索
  - [ ] 第 9-10 周：FastAPI + Docker + 部署
  - [ ] 第 11-12 周：MCP Server
  - [ ] 第 13-14 周：评测体系 + 技术博客

  ## 技术栈

  Python 3.11 · uv（后续引入 LangGraph、tree-sitter、Chroma、FastAPI、Docker）

  ## License

  [MIT](LICENSE)