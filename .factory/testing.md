test-gate: pytest

<!-- halo:test-layers -->
{"layers": [
  {"id": "unit", "class": "surrogate", "command": "pytest", "required": true,
   "runBy": "canonical-gate"}
],
"productionPathNotApplicable": "The shipped artifact for this feature (scripts/hello-world/README.md) is a static documentation file with no executable component. The pytest suite validates the Python package in this repository but cannot execute a markdown file. A production-path layer will apply when F2 (hello_world.sh) lands.",
"policyNotApplicable": "The repository has no licence, compliance, or dependency-policy check step in its canonical gate."
}
