from importlib import import_module
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    hud_module = import_module("layer-09-industrial-hud.jroc_desktop_hud")
    hud_module.JrocDesktopHUD().mainloop()


if __name__ == "__main__":
    main()
