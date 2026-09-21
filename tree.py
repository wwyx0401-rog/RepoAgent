from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
#跳过的目录名单，一些非代码的文件，世界跳过遍历
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode",
    ".venv", "venv", "env",
    "__pycache__", "node_modules", "dist", "build", ".next",
}

# 扩展名 → 语言名
EXT_TO_LANG = {
    ".py": "Python", ".pyi": "Python",
    ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".kt": "Kotlin", ".go": "Go", ".rs": "Rust",
    ".c": "C", ".h": "C", ".cc": "C++", ".cpp": "C++", ".hpp": "C++",
    ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".sh": "Shell",
    ".sql": "SQL", ".html": "HTML", ".css": "CSS", ".scss": "CSS",
    ".md": "Markdown", ".json": "JSON", ".yaml": "YAML",
    ".yml": "YAML", ".toml": "TOML",
}

MAX_FILE_BYTES = 1_000_000  # 超过 1MB 直接跳过，防止卡在某个大文件上
#判断文件是不是二进制类型文件
def is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return b"\x00" in f.read(8192)
    except OSError:
        return True

#统计文件的行数，用逐行迭代而不用f.read(),f.split
def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8",errors="ignore") as f:
         return sum(1 for _ in f)
    except OSError:
        return 0

#绘制树
def print_tree(directory: Path,prefix: str = "") -> None:
    entries = [p for p in directory.iterdir() if  p.name  not in SKIP_DIRS]
    entries.sort(key=lambda  p :(p.is_file(), p.name.lower()))
    #这两行看不懂####
    for i,entry in enumerate(entries):#枚举目录，遍历序列的同时拿到索引下标和元素值
        is_last = i == len(entries) - 1#是不是最后一个目录
        connector = " └── " if is_last else " ├── "#如果是最后的用└──来链接，否则用兄弟结点
        suffix = "/" if entry.is_dir() else ""#如果是目录则补充一个/，不是就用“”
        print(f"{prefix}{connector}{entry.name}{suffix}")#前缀＋连接符＋目录名+目录的/
        #如果还有，继续画兄弟节点
        if entry.is_dir():
            print_tree(entry, prefix + ("    " if is_last else "|    "))

def collect_stats(root: Path) -> tuple[dict[str, int], dict[str, int]]:#返回函数的类型是元组【字典】用来只读
    lines : dict[str, int] = defaultdict(int)#字典的计数器，语言，数量
    files : dict[str, int] = defaultdict(int)#文件，数量
    for path in root.rglob("*"):#root.rglob表示从root根节点遍历每一个
        if not path.is_file:#如果不是文件
            continue
        if any(part in SKIP_DIRS for part in path.parts):#是跳过类型的文件
            continue
        try:
           if path.stat().st_size > MAX_FILE_BYTES:#超过最大文件1mb
               continue
        except OSError:
            continue
        if is_binary(path):#是不是二进制文件
            continue
        lang = EXT_TO_LANG.get(path.suffix.lower())#lang表示取文件的扩展名
        if lang is None:#如果lang不是上面的文件类型，跳过
            continue

        lines[lang] += count_lines(path)
        files[lang] += 1#计数
    return lines, files


def print_stats(lines: dict[str, int], files: dict[str, int]) -> None:
    if not lines:
        print("\n没有找到可统计的源代码文件.")
        return
    width = max(len(lang)for lang in lines)
    rule = "-" * width
    print(f"\n{'语言':<{width}}  {'文件数':>6} {'行数':>8}")
    print(rule)
    for lang in sorted(lines , key = lambda k: -lines[k]):
        print(f"{lang:<{width}}  {files[lang]:>6} {lines[lang]:>8}")
    print(rule)
    print(f"{'总计':<{width}} {sum(files.values()):>6} {sum(lines.values()):>8}")


def main() -> None:
    if len(sys.argv) != 2 :#argv[0]表示的是传入的脚本的名称，argv[2]表示传入的路径
        print("用法:python tree.py <目标路径>")
        raise SystemExit(1)

    root = Path(sys.argv[1])#将用户传入的路径变成path
    if not root.is_dir():
        print(f"错误:{root} 不是一个目录")
        raise SystemExit(1)

    print(f"{root.resolve()}/")#resolve将用户传入的路径变成根目录
    print_tree(root)#打印根目录
    print_stats(*collect_stats(root))#打印统计的数量

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()



