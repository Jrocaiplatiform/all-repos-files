# J-ROC Desktop OS repair notes

This branch is a repair candidate, not a production release.

## Corrected
- Kernel boot now returns the hardware object it actually builds.
- Kernel signing/encryption secret is persisted under `data/kernel.secret` so restart-created tokens and Vault keys remain stable.
- Memory Vault imports the standard SQLite module and stores/retrieves encrypted values.
- Added the missing local-only Ollama router; J-BOT now calls local Ollama and reports an offline state instead of fabricating an answer.
- Removed hosted model routing and the embedded placeholder router key from the Desktop OS inference configuration and legacy HUD engine.
- Corrected syntax and indentation faults in the swarm, workspace, HUD bridge, device mesh, and global tools modules.
- Corrected the desktop launch entry point and replaced unverified HUD status claims.
- Replaced invalid imports in the previous test with service boot, Vault persistence, and security-policy checks.

## Deliberately disabled
- Shell/process execution remains disabled until caller identity, Owner approval, and command policy are authenticated end-to-end.
- High-risk approval remains fail-closed until the Owner identity system exists. A caller-provided role string is not proof of Owner authority.

## Still required before production
- Run CI and fix any remaining failures.
- Verify the existing committed Vault database can be migrated; records encrypted with an older ephemeral key may not be recoverable without that old key.
- Test on supported Windows hardware with local Ollama and the selected model installed.
- Complete authenticated Owner identity, policy enforcement, secrets protection, backup/restore, and installer validation.
- Review the remaining Quantum installers and generated files for external inference references and unsafe defaults.
