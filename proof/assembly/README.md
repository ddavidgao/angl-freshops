# Assembly Proof Snapshot

This directory is a checked-in proof snapshot from the generated edition.

Source of truth:

```text
specs/compute_promise_minutes.angl
```

Generated assembly snapshot:

```text
proof/assembly/compute_promise_minutes.s
```

Runtime generation still happens under `build/latest/` when `make build` or
`make proof` runs. This snapshot exists so GitHub and reviewers can see that the
Angl chapter has produced real ARM64 assembly.
