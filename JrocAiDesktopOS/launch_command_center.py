import json, time, webbrowser
from importlib import import_module

run_mod = import_module("run_jroc_os")
q_mod = import_module("quantum-enterprise.quantum_studio")
web_mod = import_module("layer-09-industrial-hud.web_command_center")

if __name__ == "__main__":
    k = run_mod.boot_os()
    rev = k.services["revenue-sync"]
    rev.activate_license("chairman", "premium", rev.issue_license("chairman", "premium"))
    studio = q_mod.QuantumEnterpriseStudio(rev)
    web = web_mod.CommandCenterWebServer(k, studio, port=8765)
    info = web.start()
    print(json.dumps(info, indent=2))
    webbrowser.open(info["url"])
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        web.stop()
        k.shutdown()
