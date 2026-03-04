import argparse
import sys
import io
from typing import Optional
from .manager import TaskManager
from .task import Task

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    # 设置标准输出为UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class CLI:
    """命令行接口类"""

    def __init__(self, manager: TaskManager = None):
        self.manager = manager or TaskManager()

    def run(self):
        """运行CLI"""
        parser = self._create_parser()
        args = parser.parse_args()

        if hasattr(args, 'func'):
            try:
                args.func(args)
            except Exception as e:
                print(f"❌ 错误: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            parser.print_help()

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行解析器"""
        parser = argparse.ArgumentParser(
            description="待办事项管理工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  todo add "购买 groceries" --desc "买牛奶和面包" --priority high --due 2026-03-10
  todo list
  todo list --filter pending
  todo edit 1 --title "新标题"
  todo done 1
  todo delete 1
  todo stats
            """
        )

        subparsers = parser.add_subparsers(title="可用命令", dest="command")

        # 添加任务命令
        add_parser = subparsers.add_parser("add", help="添加新任务")
        add_parser.add_argument("title", help="任务标题")
        add_parser.add_argument("--desc", default="", help="任务描述")
        add_parser.add_argument(
            "--priority",
            choices=Task.PRIORITIES,
            default=Task.PRIORITY_MEDIUM,
            help=f"任务优先级 (默认: {Task.PRIORITY_MEDIUM})"
        )
        add_parser.add_argument("--due", help="截止日期 (格式: YYYY-MM-DD)")
        add_parser.set_defaults(func=self.handle_add)

        # 列出任务命令
        list_parser = subparsers.add_parser("list", help="列出所有任务")
        list_parser.add_argument(
            "--filter",
            choices=["all", "pending", "in_progress", "done", "overdue", "high"],
            default="all",
            help="筛选任务 (默认: all)"
        )
        list_parser.set_defaults(func=self.handle_list)

        # 编辑任务命令
        edit_parser = subparsers.add_parser("edit", help="编辑任务")
        edit_parser.add_argument("id", type=int, help="任务ID")
        edit_parser.add_argument("--title", help="新标题")
        edit_parser.add_argument("--desc", help="新描述")
        edit_parser.add_argument(
            "--priority",
            choices=Task.PRIORITIES,
            help="新优先级"
        )
        edit_parser.add_argument(
            "--status",
            choices=Task.STATUSES,
            help="新状态"
        )
        edit_parser.add_argument("--due", help="新截止日期 (格式: YYYY-MM-DD)")
        edit_parser.set_defaults(func=self.handle_edit)

        # 标记完成命令
        done_parser = subparsers.add_parser("done", help="标记任务为已完成")
        done_parser.add_argument("id", type=int, help="任务ID")
        done_parser.set_defaults(func=self.handle_done)

        # 删除任务命令
        delete_parser = subparsers.add_parser("delete", help="删除任务")
        delete_parser.add_argument("id", type=int, help="任务ID")
        delete_parser.set_defaults(func=self.handle_delete)

        # 统计命令
        stats_parser = subparsers.add_parser("stats", help="显示任务统计")
        stats_parser.set_defaults(func=self.handle_stats)

        return parser

    def handle_add(self, args):
        """处理添加任务"""
        task = self.manager.add_task(
            title=args.title,
            description=args.desc,
            priority=args.priority,
            due_date_str=args.due,
        )
        print(f"✅ 任务已添加:")
        print(task)

    def handle_list(self, args):
        """处理列出任务"""
        filter_str = args.filter if args.filter != "all" else None
        tasks = self.manager.list_tasks(filter_str)

        if not tasks:
            print("📭 没有找到任务")
            return

        print(f"📋 任务列表 ({len(tasks)} 个任务):")
        print("-" * 60)
        for task in tasks:
            print(task)
            print("-" * 60)

    def handle_edit(self, args):
        """处理编辑任务"""
        # 构建更新参数
        update_kwargs = {}
        if args.title is not None:
            update_kwargs["title"] = args.title
        if args.desc is not None:
            update_kwargs["description"] = args.desc
        if args.priority is not None:
            update_kwargs["priority"] = args.priority
        if args.status is not None:
            update_kwargs["status"] = args.status
        if args.due is not None:
            update_kwargs["due_date_str"] = args.due

        if not update_kwargs:
            print("⚠️ 没有提供要更新的字段")
            return

        success = self.manager.update_task(args.id, **update_kwargs)
        if success:
            task = self.manager.get_task(args.id)
            print(f"✅ 任务已更新:")
            print(task)
        else:
            print(f"❌ 未找到ID为 {args.id} 的任务")

    def handle_done(self, args):
        """处理标记完成"""
        success = self.manager.mark_done(args.id)
        if success:
            task = self.manager.get_task(args.id)
            print(f"✅ 任务已标记为完成:")
            print(task)
        else:
            print(f"❌ 未找到ID为 {args.id} 的任务")

    def handle_delete(self, args):
        """处理删除任务"""
        task = self.manager.get_task(args.id)
        if task:
            print(f"⚠️  即将删除任务:")
            print(task)
            confirm = input("确认删除? (y/N): ")
            if confirm.lower() == 'y':
                success = self.manager.delete_task(args.id)
                if success:
                    print(f"✅ 任务已删除")
            else:
                print("取消删除")
        else:
            print(f"❌ 未找到ID为 {args.id} 的任务")

    def handle_stats(self, args):
        """处理统计"""
        stats = self.manager.get_stats()
        print("📊 任务统计:")
        print(f"   总计: {stats['total']}")
        print(f"   📋 待办: {stats['pending']}")
        print(f"   🔄 进行中: {stats['in_progress']}")
        print(f"   ✅ 已完成: {stats['done']}")
        print(f"   ⚠️  已过期: {stats['overdue']}")
