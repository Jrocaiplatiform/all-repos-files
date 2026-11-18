import json
import sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

kernel_module = import_module("layer-01-kernel.kernel_core")
router_module = import_module("layer-02-failover-router.router_engine")
vault_module = import_module("layer-03-memory-vault.vault_manager")
execution_module = import_module("layer-04-execution-tools.execution_engine")
security_module = import_module("layer-05-security-sandbox.security_service")
swarm_module = import_module("layer-06-worker-swarms.swarm_orchestrator")
jbot_module = import_module("layer-07-jbot-core.jbot_service")
workspace_module = import_module("layer-08-division-workspaces.workspace_manager")
hud_module = import_module("layer-09-industrial-hud.hud_bridge")
revenue_module = import_module("layer-10-revenue-sync.revenue_service")
evolution_module = import_module("layer-11-self-evolution.evolution_service")
mesh_module = import_module("layer-12-device-mesh.device_mesh_service")


def boot_os(root_dir: Path = ROOT):
    root_dir = Path(root_dir)
    kernel = kernel_module.JrocKernel(root_dir)
    router = router_module.FailoverRouterService(root_dir, kernel)
    vault = vault_module.MemoryVaultService(root_dir, kernel.secret)
    security = security_module.SecuritySandboxService(root_dir, kernel)
    execution = execution_module.ExecutionToolsService(root_dir, kernel)
    swarms = swarm_module.WorkerSwarmService(root_dir, kernel)
    jbot = jbot_module.JBotCoreService(root_dir, router, vault, swarms, kernel)
    workspaces = workspace_module.DivisionWorkspaceService(root_dir, kernel)
    hud = hud_module.IndustrialHUDService(root_dir, kernel)
    revenue = revenue_module.RevenueSyncService(root_dir, kernel.secret, kernel)
    evolution = evolution_module.SelfEvolutionService(root_dir, kernel)
    mesh = mesh_module.DeviceMeshService(root_dir, kernel.secret, kernel)

    for service in (
        router, vault, security, execution, swarms, jbot, workspaces,
        hud, revenue, evolution, mesh,
    ):
        kernel.attach_service(service)
    return kernel


if __name__ == "__main__":
    operating_system = boot_os()
    try:
        print(json.dumps(operating_system.boot(), indent=2))
        print(json.dumps(operating_system.health(), indent=2))
    finally:
        operating_system.shutdown()
