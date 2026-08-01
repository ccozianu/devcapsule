# NVIDIA CUDA Base Recipe Specialized Validation

Date: 2026-08-01

Status: open V1-blocking specialized validation task

## Purpose

DevCapsule exposes the WIP base recipe:

```text
devcapsule images build --type base --recipe nvidia-cuda-devel
```

The recipe starts from
`nvidia/cuda:12.8.1-devel-ubuntu24.04`, installs the same developer utilities
as the default `ubuntu-24.04` recipe, embeds the selected DevCapsule PEX, and
records NVIDIA, CUDA-version, recipe, and WIP metadata. Automated tests can
verify its generated build plan, but this agent session has no GPU access.
Specialized E2E evidence must therefore be collected later on one of the
maintainer's NVIDIA laptops before V1 release.

## Partial Validation Evidence

On 2026-08-01, the user reported that the first external test succeeded: the
`nvidia-cuda-devel` recipe built a local NVIDIA GPU base image on an NVIDIA
laptop. This accepts initial image formation only. The exact image inspection,
CUDA compiler check, positive and negative GPU-device authorization checks,
real CUDA workload, and materialized-environment launch remain outstanding.

## Safety Contract

Image formation and runtime device authorization are independent. Building or
selecting the CUDA recipe must not expose a GPU to a container. A GPU is
available only after an explicit developer-owned authorization is resolved
into the launch plan.

AMD ROCm and other GPU families are not covered by this task. They require
partner or cloud test infrastructure and are outside required V1 scope.

## Prerequisites

- An NVIDIA laptop supported by CUDA 12.8.1.
- A current NVIDIA host driver.
- Docker with NVIDIA Container Toolkit integration.
- The PEX and source revision intended for the V1 candidate.
- The implemented `images build --type environment` and explicit runtime GPU
  authorization path for the final positive/negative launch checks.

## Validation Procedure

1. Run the full repository gate and build the release-candidate PEX.
2. Build the default recipe as a regression control.
3. Build the CUDA recipe through the PEX, without overriding its root:

   ```bash
   python3.12 dist/devcapsule.pex images build \
     --type base \
     --recipe nvidia-cuda-devel \
     --tag devcapsule-base:cuda-v019 \
     --source-revision "$(git rev-parse HEAD)"
   ```

4. Inspect the image and confirm its managed-image, base-kind, recipe, WIP,
   NVIDIA vendor, CUDA 12.8.1, PEX digest, source revision, entrypoint, and
   command metadata.
5. Override the entrypoint for diagnostic checks and confirm `nvcc --version`
   reports CUDA 12.8.1.
6. Launch without GPU authorization and prove the workload cannot use the host
   GPU.
7. Launch with explicit GPU authorization, run `nvidia-smi`, and confirm the
   expected laptop GPU is visible.
8. Compile and execute a small CUDA program or an equivalent deterministic
   CUDA smoke workload inside the image.
9. Materialize the dogfood environment from this base and repeat the negative
   and positive checks through DevCapsule's resolved launch path.
10. Record the host GPU, driver, Docker, NVIDIA Container Toolkit, image ID,
    PEX digest, commands, and sanitized results in this task.

## Closure Criteria

This V1 blocker is complete only when:

- the full automated gate passes;
- both base recipes build from the release-candidate PEX;
- CUDA compilation and execution succeed on an NVIDIA laptop;
- absence of runtime GPU authorization denies GPU use;
- explicit runtime GPU authorization enables the intended GPU use;
- a CUDA-based materialized dogfood environment retains the generic runtime
  entrypoint and launches successfully; and
- the WIP warning/status is either removed after acceptance or replaced with
  an accurately documented remaining limitation.

Successful completion should update D-0004, current user documentation,
`CURRENT-STATUS.md`, and this record with the validation evidence.
