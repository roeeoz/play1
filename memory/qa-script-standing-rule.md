---
sourceRef: 5d498d2d-7fb7-4797-af30-580adc409835
updatedAt: 2026-11-22T21:17:26Z
---

Every script the project ships lives under qa/ and prints only to stdout on success, with no extra text. It answers --help with exactly one summary line on stdout and exit code 0; any other unknown argument is refused with a short one-line error on stderr, nothing on stdout, and exit code 2. The product owner set this as a standing rule for all future epics and stories, including the --help part.
