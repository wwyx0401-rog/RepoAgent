"""第 2 周：接收一个仓库链接，clone 到 data/repos/，然后打印文件树 + 语言统计。

用法:
    python main.py https://github.com/psf/requests

设计上只有一件事要记住：**main.py 只负责"拿到一个本地目录"，打印的部分全部复用 tree.py**。
不要把 print_tree / collect_stats 的代码抄过来。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# 从 tree.py 借用第 1 周已经写好的三个函数。
# 能直接 import 是因为 tree.py 里的 main() 被 if __name__ == "__main__" 保护住了 —— 导入它不会触发执行。
from tree import collect_stats, print_stats, print_tree

REPOS_DIR = Path("data/repos")
CLONE_TIMEOUT_SECONDS = 120  # 网络卡住时的兜底，别让它无限挂着


def repo_name_from_url(url: str) -> str:
    """从仓库链接里取出仓库名，用作本地目录名。

        https://github.com/psf/requests.git   ->  requests
        https://github.com/psf/requests       ->  requests
        git@github.com:psf/requests.git       ->  requests

    提示: 三步 —— 去掉结尾的 "/"、去掉结尾的 ".git"、按 "/" 切开取最后一段。
         （SSH 那种 git@github.com:psf/requests 的链接也可以顺手处理，作为加分项）
    """

    name = url.rstrip("/")
    name = name.removesuffix(".git")
    return name.split("/")[-1]



def clone_repo(url: str, repos_dir: Path) -> Path | None:
    """把 url clone 到 repos_dir/<仓库名>/，返回 clone 出来的本地路径。

    失败时打印人话错误并 raise SystemExit(1)，不要抛出裸的异常堆栈。

    要处理的坑:
      1. 目标目录已经存在 -> git 会以退出码 128 失败（实测），
         这种情况应该直接复用已有的目录，而不是报错退出。
         （第 4 周会反复索引同一个仓库，每次都重新 clone 太慢）
      2. 命令要用列表形式传参: ["git", "clone", "--depth", "1", url, str(target)]
         不要用 shell=True，也不要自己拼字符串。
      3. subprocess.run(...) 必须加 capture_output=True，否则 git 的错误信息
         直接打到屏幕上，你既拿不到文本、也没法在日志里记录失败原因。
         再加 text=True 让输出直接是 str 而不是 bytes。
      4. 传 timeout=CLONE_TIMEOUT_SECONDS，捕获 subprocess.TimeoutExpired。
         超时后要给出"看下网络"之类的提示，别只说一句失败。
      5. 用 result.returncode 判断成败，**不要用 check=True**
         （check=True 会抛 CalledProcessError，你还得再包一层 try）。
         失败时把 result.stderr 的前几行打出来 —— 这是定位问题唯一的信息来源。
      6. git 本身不存在（FileNotFoundError）也要捕获，提示"没装 git 或不在 PATH 里"。
      7. --depth 1 表示只拉最新一次提交。我们只读代码、不需要历史，能快很多。
    """
    # TODO 2
    url_name = repo_name_from_url(url)
    target = repos_dir / url_name
    if target.exists():
        return target


    try:
      process = subprocess.run(["git", "clone", "--depth", "1", url, str(target)],
                               capture_output=True, timeout=CLONE_TIMEOUT_SECONDS,text=True)
    except subprocess.TimeoutExpired:
        print("网络超时了")
        raise SystemExit(1)
    except FileNotFoundError:
        print("未找到git")
        raise SystemExit(1)

    if process.returncode != 0:
        print(process.stderr)
        raise SystemExit(1)

    return target



def is_empty_repo(repo_path: Path) -> bool:
    """判断是不是空仓库。

    空仓库的特征（实测）: git clone 的退出码是 0、stderr 只有一行 "done."，
    但目录里除了 .git 以外什么都没有。所以**没法和失败区分开，必须单独判断**。

    提示: 遍历 repo_path 下面的一级内容，看有没有"名字不是 .git"的东西。
         一行表达式就能写完。注意第 3 周会用到这个函数来决定要不要跳过索引。
    """
    return not any(p.name != ".git" for p in repo_path.iterdir())


def main() -> None:
    if len(sys.argv) != 2:
        print("用法: python main.py <仓库链接>")
        print("例如: python main.py https://github.com/psf/requests")
        raise SystemExit(1)

    url = sys.argv[1]
    repo_path = clone_repo(url, REPOS_DIR)
    if is_empty_repo(repo_path):
        print("这是空仓库")
        return

        # TODO 4: 用 is_empty_repo 判断一下。空仓库不要走下面的打印流程，
    #         直接给一句人话提示（比如"这是个空仓库，没有可索引的代码"）然后正常退出。
    #         注意退出码要是 0 —— 空仓库不是错误，验收标准里的要求是"不崩溃"。

    print(f"{repo_path.resolve()}/")
    print_tree(repo_path)
    print_stats(*collect_stats(repo_path))


if __name__ == "__main__":
    # tree.py 是在自己的 __main__ 里做的这行，这里 import 它并不会帮我们执行，
    # 所以 main.py 得自己来一遍：Windows 中文环境 stdout 默认 gbk，直接打印 ├── 会乱码。
    sys.stdout.reconfigure(encoding="utf-8")
    main()
