import sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

kernel_mod = import_module("layer-01-kernel.kernel_core")

def test_kernel_boots_and_authenticates(tmp_path):
    k = kernel_mod.JrocKernel(root_dir=tmp_path)
    res = k.boot()
    assert res["status"] == "online"
    claims = k.auth.verify_token(k.kernel_token)
    assert claims is not None
    assert claims["role"] == "kernel"