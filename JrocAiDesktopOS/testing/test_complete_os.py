import json, sys, urllib.request
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

run_mod = import_module("run_jroc_os")
tools_mod = import_module("global-tools.tools_suite")
q_mod = import_module("quantum-enterprise.quantum_studio")
web_mod = import_module("layer-09-industrial-hud.web_command_center")

def test_full_jroc_os_suite(tmp_path):
    k = run_mod.boot_os()
    tools = tools_mod.GlobalToolsSuite(tmp_path)
    tid = tools.add_task("Verify full suite")
    assert tid >= 1
    snap = tools.create_snapshot("test")
    assert snap.exists()

    rev = k.services["revenue-sync"]
    lic = rev.issue_license("chairman", "premium")
    assert rev.activate_license("chairman", "premium", lic) is True
    studio = q_mod.QuantumEnterpriseStudio(rev)
    bell = studio.run_bell_state(128)
    assert bell["ok"] is True and bell["probabilities"]["00"] == 0.5

    web = web_mod.CommandCenterWebServer(k, studio, port=0)
    info = web.start()
    try:
        req = urllib.request.Request(f"http://{info['host']}:{info['port']}/api/health", headers={"X-JROC-Token": k.kernel_token})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
    finally:
        web.stop()
        k.shutdown()
