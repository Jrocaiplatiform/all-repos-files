from importlib import import_module
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

kernel_module = import_module("layer-01-kernel.kernel_core")


def test_kernel_boots_and_authenticates(tmp_path):
    kernel = kernel_module.JrocKernel(root_dir=tmp_path)
    result = kernel.boot()
    assert result["status"] == "online"
    assert kernel.verify_token(kernel.kernel_token) is True
    assert kernel.verify_token("not-a-token") is False


def test_kernel_secret_survives_restart(tmp_path):
    first = kernel_module.JrocKernel(root_dir=tmp_path)
    token = first.issue_token("test-service", "system")
    second = kernel_module.JrocKernel(root_dir=tmp_path)
    assert second.verify_token(token) is True
