#!/usr/bin/env python3

import sys
from pathlib import Path

from rich.console import Console

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

console = Console()
