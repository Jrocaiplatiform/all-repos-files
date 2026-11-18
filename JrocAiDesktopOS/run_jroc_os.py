import json, sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

k1 = import_module("layer-01-kernel.kernel_core")
k2 = import_module("layer-02-failover-router.router_engine")
k3 = import_module("layer-03-memory-vault.vault_manager")
k4 = import_module("layer-04-execution-tools.execution_engine")
k5 = import_module("layer-05-security-sandbox.security_service")
k6 = import_module("layer-06-worker-swarms.swarm_orchestrator")
k7 = import_module("layer-07-jbot-core.jbot_service")
k8 = import_module("layer-08-division-workspaces.workspace_manager")
k9 = import_module("layer-09-industrial-hud.hud_bridge")
k10 = import_module("layer-10-revenue-sync.revenue_service")
k11 = import_module("layer-11-self-evolution.evolution_service")
k12 = import_module("layer-12-device-mesh.device_mesh_service")

def boot_os():
    kernel = k1.JrocKernel(ROOT)
    r = k2.FailoverRouterService(ROOT, kernel)
    v = k3.MemoryVaultService(ROOT, kernel.secret)
    e = k4.ExecutionToolsService(ROOT, kernel)
    s = k5.SecuritySandboxService(ROOT, kernel)
    w = k6.WorkerSwarmService(ROOT, kernel)
    j = k7.JBotCoreService(ROOT, r, v, w, kernel)
    ws = k8.DivisionWorkspaceService(ROOT, kernel)
    h = k9.IndustrialHUDService(ROOT, kernel)
    rev = k10.RevenueSyncService(ROOT, kernel.secret, kernel)
    ev = k11.SelfEvolutionService(ROOT, kernel)
    m = k12.DeviceMeshService(ROOT, kernel.secret, kernel)
    for svc in (r, v, e, s, w, j, ws, h, rev, ev, m): kernel.attach_service(svc)
    return kernel

if __name__ == "__main__":
    os_k = boot_os()
    print(json.dumps(os_k.boot(), indent=2))
    os_k.shutdown()
