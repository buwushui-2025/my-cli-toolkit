#!/usr/bin/env python3
"""my-cli-toolkit — 多功能命令行工具箱

支持功能菜单选择：
  1. 待办清单
  2. 密码生成器
  3. 文件重命名工具
  0. 退出
"""

import json
import os
import random
import re
import shutil
import string
import sys
from pathlib import Path


# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────
TODO_FILE = Path(__file__).parent / "todo_data.json"


# ══════════════════════════════════════════════
#  主入口 & 菜单
# ══════════════════════════════════════════════

MENU_ITEMS = [
    ("1", "待办清单",     "管理待办事项：添加、查看、完成、删除"),
    ("2", "密码生成器",   "生成随机强密码，可自定义长度与字符集"),
    ("3", "文件重命名",   "批量重命名文件（按模式匹配替换）"),
    ("0", "退出",         "退出程序"),
]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_menu():
    """显示功能菜单"""
    clear_screen()
    print("╔══════════════════════════════════════════╗")
    print("║         🧰  my-cli-toolkit 工具箱         ║")
    print("╠══════════════════════════════════════════╣")
    for key, name, desc in MENU_ITEMS:
        print(f"║  [{key}] {name:<12} — {desc:<24} ║")
    print("╚══════════════════════════════════════════╝")


def main():
    """主循环：显示菜单 → 接收输入 → 调用对应工具"""
    tool_map = {
        "1": todo_tool,
        "2": password_tool,
        "3": rename_tool,
    }

    while True:
        show_menu()
        choice = input("\n请输入功能编号: ").strip()

        if choice == "0":
            print("👋 再见！")
            sys.exit(0)

        tool = tool_map.get(choice)
        if tool:
            clear_screen()
            tool()
            input("\n按 Enter 返回菜单...")
        else:
            print("⚠️  无效输入，请重新选择。")


# ══════════════════════════════════════════════
#  工具 1：待办清单
# ══════════════════════════════════════════════

def load_todos():
    """从 JSON 加载待办列表"""
    if TODO_FILE.exists():
        try:
            return json.loads(TODO_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_todos(todos):
    """保存待办列表到 JSON"""
    TODO_FILE.write_text(
        json.dumps(todos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def todo_print_list(todos):
    """打印待办列表"""
    if not todos:
        print("📭 待办清单为空。")
        return

    print("┌────┬────────────────────────────────────────────┬──────────┐")
    print("│ #  │ 事项                                       │ 状态     │")
    print("├────┼────────────────────────────────────────────┼──────────┤")
    for i, item in enumerate(todos, 1):
        status = "✅ 已完成" if item.get("done") else "⬜ 待办"
        title = item.get("title", "")
        display = title[:40] + ("…" if len(title) > 40 else "")
        print(f"│ {i:<2} │ {display:<42} │ {status:<8} │")
    print("└────┴────────────────────────────────────────────┴──────────┘")


def todo_tool():
    """待办清单工具主界面"""
    todos = load_todos()

    while True:
        clear_screen()
        print("📋  待办清单")
        print("=" * 50)
        todo_print_list(todos)
        print()
        print("[a] 添加  [d] 完成  [c] 撤销完成  [x] 删除  [q] 返回")

        choice = input("\n操作: ").strip().lower()

        if choice == "q":
            break
        elif choice == "a":
            title = input("事项内容: ").strip()
            if title:
                todos.append({"title": title, "done": False})
                save_todos(todos)
                print(f"✅ 已添加: {title}")
            else:
                print("⚠️ 内容不能为空。")
        elif choice == "d":
            try:
                idx = int(input("完成第几项？ ")) - 1
                if 0 <= idx < len(todos):
                    todos[idx]["done"] = True
                    save_todos(todos)
                    print(f"✅ 已完成: {todos[idx]['title']}")
                else:
                    print("⚠️ 编号无效。")
            except ValueError:
                print("⚠️ 请输入数字编号。")
        elif choice == "c":
            try:
                idx = int(input("撤销第几项？ ")) - 1
                if 0 <= idx < len(todos):
                    todos[idx]["done"] = False
                    save_todos(todos)
                    print(f"🔄 已撤销: {todos[idx]['title']}")
                else:
                    print("⚠️ 编号无效。")
            except ValueError:
                print("⚠️ 请输入数字编号。")
        elif choice == "x":
            try:
                idx = int(input("删除第几项？ ")) - 1
                if 0 <= idx < len(todos):
                    removed = todos.pop(idx)
                    save_todos(todos)
                    print(f"🗑️  已删除: {removed['title']}")
                else:
                    print("⚠️ 编号无效。")
            except ValueError:
                print("⚠️ 请输入数字编号。")
        else:
            print("⚠️ 无效操作。")

        input("\n按 Enter 继续...")


# ══════════════════════════════════════════════
#  工具 2：密码生成器
# ══════════════════════════════════════════════

CHAR_SETS = {
    "lower":   string.ascii_lowercase,
    "upper":   string.ascii_uppercase,
    "digits":  string.digits,
    "special": "!@#$%^&*()-_=+[]{};:,.<>?",
}


def password_tool():
    """密码生成器工具主界面"""
    while True:
        clear_screen()
        print("🔐  密码生成器")
        print("=" * 50)

        try:
            length_str = input("密码长度 (默认 16): ").strip()
            length = int(length_str) if length_str else 16
            if length < 4:
                print("⚠️ 长度至少为 4。")
                input("\n按 Enter 继续...")
                continue
        except ValueError:
            print("⚠️ 请输入有效数字。")
            input("\n按 Enter 继续...")
            continue

        print()
        print("选择字符集（默认全部启用）:")
        use_lower = input("  启用小写字母? (Y/n): ").strip().lower() != "n"
        use_upper = input("  启用大写字母? (Y/n): ").strip().lower() != "n"
        use_digits = input("  启用数字?    (Y/n): ").strip().lower() != "n"
        use_special = input("  启用特殊字符? (Y/n): ").strip().lower() != "n"

        selected = []
        if use_lower:
            selected.append(CHAR_SETS["lower"])
        if use_upper:
            selected.append(CHAR_SETS["upper"])
        if use_digits:
            selected.append(CHAR_SETS["digits"])
        if use_special:
            selected.append(CHAR_SETS["special"])

        if not selected:
            print("⚠️ 至少选择一种字符集。")
            input("\n按 Enter 继续...")
            continue

        charset = "".join(selected)

        # 确保至少包含每种选中的字符
        password_chars = [random.choice(s) for s in selected]
        password_chars += [random.choice(charset) for _ in range(length - len(password_chars))]
        random.shuffle(password_chars)
        password = "".join(password_chars)

        print()
        print("━" * 50)
        print(f"🔑 生成的密码:  {password}")
        print(f"📏 长度: {len(password)}")
        print("━" * 50)

        again = input("\n再生成一个? (Y/n): ").strip().lower()
        if again == "n":
            break


# ══════════════════════════════════════════════
#  工具 3：文件重命名工具
# ══════════════════════════════════════════════

def rename_tool():
    """批量文件重命名工具主界面"""
    while True:
        clear_screen()
        print("📝  文件批量重命名")
        print("=" * 50)

        target_dir = input("目标文件夹路径: ").strip().strip('"')
        if not target_dir:
            print("⚠️ 路径不能为空。")
            input("\n按 Enter 继续...")
            continue

        target_path = Path(target_dir)
        if not target_path.exists():
            print(f"⚠️ 路径不存在: {target_dir}")
            input("\n按 Enter 继续...")
            continue
        if not target_path.is_dir():
            print(f"⚠️ 不是文件夹: {target_dir}")
            input("\n按 Enter 继续...")
            continue

        # 获取文件列表
        files = sorted([f for f in target_path.iterdir() if f.is_file()])
        if not files:
            print("📭 文件夹内没有文件。")
            input("\n按 Enter 继续...")
            continue

        # 预览当前文件
        print(f"\n📂 {target_path}")
        print(f"共 {len(files)} 个文件:\n")
        for i, f in enumerate(files, 1):
            print(f"  {i:>3}. {f.name}")

        # 选择重命名模式
        print("\n" + "─" * 50)
        print("重命名方式:")
        print("  [1] 查找替换 — 替换文件名中的指定文本")
        print("  [2] 添加前缀")
        print("  [3] 添加后缀")
        print("  [4] 序号重命名 — 统一名称 + 序号")
        print("  [q] 返回菜单")
        print()

        mode = input("选择方式: ").strip().lower()

        if mode == "q":
            break

        if mode not in ("1", "2", "3", "4"):
            print("⚠️ 无效选择。")
            input("\n按 Enter 继续...")
            continue

        # 构建新旧名称映射
        rename_map = []

        if mode == "1":
            old_text = input("要替换的文本: ")
            new_text = input("替换为: ")
            for f in files:
                new_name = f.name.replace(old_text, new_text)
                if new_name != f.name:
                    rename_map.append((f, f.with_name(new_name)))

        elif mode == "2":
            prefix = input("前缀: ")
            for f in files:
                rename_map.append((f, f.with_name(prefix + f.name)))

        elif mode == "3":
            suffix = input("后缀 (加在扩展名前): ")
            for f in files:
                stem, ext = os.path.splitext(f.name)
                rename_map.append((f, f.with_name(stem + suffix + ext)))

        elif mode == "4":
            base_name = input("基础名称 (如 photo): ").strip()
            start_num_str = input("起始序号 (默认 1): ").strip()
            try:
                start_num = int(start_num_str) if start_num_str else 1
            except ValueError:
                start_num = 1
            padding = len(str(len(files) + start_num - 1))

            for i, f in enumerate(files):
                ext = f.suffix
                new_name = f"{base_name}_{str(start_num + i).zfill(padding)}{ext}"
                rename_map.append((f, f.with_name(new_name)))

        if not rename_map:
            print("⚠️ 没有文件需要重命名。")
            input("\n按 Enter 继续...")
            continue

        # 预览变更
        print("\n📋 重命名预览:")
        print("─" * 60)
        for old, new in rename_map:
            print(f"  {old.name}")
            print(f"    → {new.name}")
        print("─" * 60)
        print(f"共 {len(rename_map)} 个文件将被重命名")

        confirm = input("\n确认执行? (y/N): ").strip().lower()
        if confirm != "y":
            print("🚫 已取消。")
            input("\n按 Enter 继续...")
            continue

        # 执行重命名（支持撤销）
        done = []
        errors = 0
        for old, new in rename_map:
            try:
                old.rename(new)
                done.append((old, new))
            except OSError as e:
                print(f"⚠️ 重命名失败: {old.name} — {e}")
                errors += 1

        print(f"\n✅ 完成！成功 {len(done)} 个，失败 {errors} 个。")

        if done and errors == 0:
            undo = input("\n要撤销吗? (y/N): ").strip().lower()
            if undo == "y":
                undone = 0
                for old, new in reversed(done):
                    try:
                        new.rename(old)
                        undone += 1
                    except OSError:
                        pass
                print(f"🔄 已撤销 {undone} 个文件。")

        input("\n按 Enter 继续...")


# ══════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
