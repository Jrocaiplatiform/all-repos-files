from importlib import import_module
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

run_module = import_module("run_jroc_os")


def test_all_desktop_os_services_boot_and_stop(tmp_path):
    kernel = run_module.boot_os(tmp_path)
    result = kernel.boot()
    assert result["status"] == "online"
    assert len(result["services"]) == 11
    health = kernel.health()
    assert health["kernel"] == "online"
    assert health["services"]["memory-vault"]["records"] == 0
    assert health["services"]["worker-swarms"]["workers"] == 2
    assert kernel.shutdown()["status"] == "offline"


def test_vault_encrypts_and_persists_across_restart(tmp_path):
    first = run_module.boot_os(tmp_path)
    first.boot()
    vault = first.services["memory-vault"]
    vault.put("test.key", "private test value", namespace="tests")
    assert vault.get("test.key") == "private test value"
    first.shutdown()

    second = run_module.boot_os(tmp_path)
    second.boot()
    assert second.services["memory-vault"].get("test.key") == "private test value"
    second.shutdown()


def test_high_risk_actions_fail_closed_without_owner_identity(tmp_path):
    kernel = run_module.boot_os(tmp_path)
    kernel.boot()
    security = kernel.services["security-sandbox"]
    request = security.authorize_action("system", "fs.delete_tree")
    assert request["allowed"] is False
    assert request["requires_owner_approval"] is True
    request_id = request["request_id"]
    assert security.approve_request(request_id, True, approved_by="owner")["ok"] is False
    assert security.health_check()["pending"] == 1
    execution = kernel.services["execution-tools"]
    assert execution.run_command("owner", ["python", "--version"])["ok"] is False
    kernel.shutdown()
