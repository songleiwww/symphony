# Symphony Task Panel Ui
# 开发者: 赵心怡 (UI设计师)
# 生成时间: 2026-03-08T01:57:37.905609
# 版本: 1.5.1

这是一个使用 Python 和 `rich` 库构建的完整终端 UI 代码。

这个设计采用了 **Dashboard（仪表盘）** 风格，包含了所有要求的类，并且通过 `rich.live` 模块实现了动态实时更新，以展示进度条和时间的变化。

### 前置准备

你需要安装 `rich` 库：

```bash
pip install rich
```

### 完整代码 (symphony_ui.py)

```python
import time
import random
import datetime
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, SpinnerColumn
from rich.live import Live
from rich.style import Style
from rich.box import Box

# --- 配置控制台主题 ---
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "title": "bold magenta"
})
console = Console(theme=custom_theme)

# --- 1. ModelSelector 类 (模型选择器) ---
class ModelSelector:
    def __init__(self):
        self.models = [
            {"name": "Symphony-Base-v1", "id": "base", "selected": True},
            {"name": "Symphony-Plus-v2", "id": "plus", "selected": False},
            {"name": "Symphony-Lite", "id": "lite", "selected": False},
            {"name": "Symphony-Finance", "id": "fin", "selected": True},
        ]
        self.status = "Ready" # Ready, Busy, Error

    def render(self) -> Panel:
        table = Table(box=None, show_header=False, padding=(0, 2))
        table.add_column("Check", width=4)
        table.add_column("Model Name", style="cyan")
        table.add_column("Status", justify="right")

        for model in self.models:
            check_mark = "[bold green]✓[/bold green]" if model["selected"] else "[dim]·[/dim]"
            row_style = "on dark_blue" if model["selected"] else ""
            
            # 模拟状态指示
            status_icon = "🟢" if model["selected"] else "⚪"
            
            table.add_row(
                Text(check_mark, justify="center"),
                Text(model["name"], style="bold white" if model["selected"] else "dim"),
                Text(status_icon),
                style=row_style
            )

        # 模拟下拉框的标题
        title = Text("Model Selection (Multi-Select)", style="bold white on blue")
        return Panel(
            table, 
            title=title, 
            border