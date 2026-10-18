# Work-item breakdown — 20261018-202402Z Hello world bash script in a dedicated folder

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add hello-world bash script in dedicated folder | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[{"ref":"t1","repoId":"1c3b71d2-d42c-4255-8320-84033af4e805","title":"Add hello-world bash script in dedicated folder","summary":"**Intent**: Create the `hello-world/` directory at the repository root containing a single executable bash script `hello.sh` that prints exactly \"hello world\" to standard output. This delivers the complete feature in one independently shippable change.\n\n**Owns**: `hello-world/hello.sh` (creates)\n**Consumes**: nothing\n\n**Acceptance criteria**:\n1. A folder named `hello-world` exists at the repository root.\n2. The folder contains exactly one file: `hello.sh`.\n3. `hello.sh` starts with the shebang line `#!/bin/bash`.\n4. `hello.sh` has executable permissions set.\n5. Running `./hello-world/hello.sh` prints exactly the lowercase string `hello world` to standard output with no leading or trailing whitespace and no additional lines.\n6. The script exits with code 0.","dependsOn":[],"complexity":{"scores":{"scope_clarity":0,"technical_design_decisions":0,"system_impact":0,"async_distributed_complexity":0,"validation_complexity":0,"risk_unknowns":0},"justifications":{"scope_clarity":"","technical_design_decisions":"","system_impact":"","async_distributed_complexity":"","validation_complexity":"","risk_unknowns":""},"total_score":0,"tier":"T1","engineer_level":"","reasoning_effort":"","token_budget":"Small","human_decision_required":false}}]
```
