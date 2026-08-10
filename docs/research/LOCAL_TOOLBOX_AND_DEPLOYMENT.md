# Local Toolbox and Deployment — Research Notes

**Status:** ACTIVE RESEARCH NOTES  
**Purpose:** Preserve deployment principles discovered during Survey V2. This is not yet an installer specification.

---

## 1. Deployment principle

Do not assume the user has a GPU.

Do assume the product can:

- inspect the machine;
- explain missing software prerequisites;
- install or guide installation of ordinary runtime dependencies where appropriate;
- offer CPU, GPU-accelerated, or cloud capability paths based on actual runtime probes.

The key distinction is:

```text
Hardware capability
≠
Software capability
```

Hardware such as GPU/VRAM cannot be created by installation.

Software such as FFmpeg, runtime libraries, Python/model packages, and optional analysis components can be
installed or repaired.

---

## 2. Capability tiers

Current conceptual tiers:

```text
Tier 0 — Core local runtime
- project runtime
- SQLite
- FFmpeg / ffprobe
- CPU deterministic media tools

Tier 1 — Optional local enhancement
- CPU-capable ASR
- music analysis models/tools
- optional Python/PyTorch components

Tier 2 — Hardware accelerated
- CUDA / GPU-enabled local models
- QSV / AMF / NVENC/NVDEC
- heavier temporal/vision/audio providers

Tier 3 — Cloud intelligence
- text reasoning providers
- multimodal visual providers
- optional high-end review/escalation providers
```

GPU availability should improve speed or unlock optional local capabilities, not determine whether the
product fundamentally works.

---

## 3. Environment Doctor

A future Windows product should include an Environment/Capability Doctor rather than expose low-level
errors directly to ordinary users.

Potential checks:

- Windows version;
- CPU / RAM / free disk space;
- GPU vendor / device / VRAM;
- FFmpeg / ffprobe runtime;
- available codecs / filters actually required by the approved build;
- Media Foundation;
- D3D11 video capability;
- QSV / AMF / NVENC/NVDEC runtime viability;
- GStreamer preview runtime if adopted;
- local ASR capability;
- local music-analysis capability;
- optional model/runtime installations;
- proxy-generation and render micro-benchmarks.

Do not trust only a declared feature list. Important capabilities should execute a tiny runtime probe before
being marked `ready`.

Candidate status vocabulary:

```text
ready
available_after_install
available_but_slow
hardware_blocked
cloud_fallback
unavailable
```

---

## 4. User installation assistance

The product should not require the user to understand Python/CUDA/FFmpeg terminology before they can use it.

When a prerequisite is missing, preferred UX order is:

1. install/repair it automatically when safe and practical;
2. provide a guided terminal command/workflow when user action is required;
3. generate a copyable environment-repair report/prompt the user can give to an AI assistant of their choice;
4. clearly explain what feature remains unavailable until the prerequisite is fixed.

The product should not bind this workflow to a single external assistant brand. User-facing copy may give
familiar examples such as DeepSeek, Qwen, Doubao, ChatGPT, Claude or Gemini, but the durable feature is:

> **Use an AI assistant you trust to follow the generated environment-repair instructions.**

A generated repair prompt might contain:

```text
I am installing video-editing-agent on Windows.

Environment Doctor found these missing prerequisites:
...

Please guide me step by step.
Requirements:
- prefer official installers/sources;
- do not disable security protections;
- explain each command before running it;
- give a verification command after every installation step.
```

The software itself should still remain the source of truth for *what is required* and should re-run its
own probes after the user finishes external assistance.

---

## 5. Local toolbox philosophy

The AI should behave as if it carries a prepared local toolbox.

```text
AI
- understands
- plans
- judges
- reviews

Local tools
- probe
- decode
- measure
- index
- trim
- render
- persist
```

API calls are reserved for information/judgment that benefits from model intelligence.

Preferred flow:

```text
cheap local preprocessing
→ small relevant evidence package
→ AI decision
→ structured plan
→ local deterministic execution
```

Network loss may stop new cloud inference, but should not invalidate already persisted structured decisions
or prevent local EDL execution/rendering where dependencies are already installed.

---

## 6. Media working-set layers

Do not conflate original media, edit-friendly media, proxies, and timeline preview cache.

Conceptual hierarchy:

```text
User Original Asset
      │
      ├─ directly editable
      │
      └─ VFR / difficult codec / unstable seek
             ↓
       Edit-Friendly Artifact

Original / Edit-Friendly
             ↓
         Proxy Artifact
             ↓
        interactive preview

Timeline + effects
             ↓
      Preview Render Chunks
```

Derived media artifacts do not become new authoritative Domain Assets.

Final render must use the appropriate original/high-quality source chain, not low-resolution proxies.

---

## 7. Durable state vs rebuildable cache

Rebuildable cache examples:

- proxies;
- thumbnails;
- waveform caches;
- extracted temporary frames;
- preview render chunks.

Durable project state examples:

- Script/Shooting revisions;
- Asset/Shot identity;
- paid/cloud ShotAnalysis results tied to revisions;
- ASR results that would be expensive/non-deterministic to reproduce;
- BeatMap revisions;
- EditPlan;
- ResolutionDecision;
- EDL;
- ReviewReport.

Do not expose a generic “clear cache” action that silently deletes costly/revisioned reasoning artifacts.

---

## 8. Cache invalidation

Because the project uses revisioned structured timeline state, preview caching should become range-aware.

Conceptually:

```text
EDL segment changed
→ determine affected timeline range
→ invalidate only affected preview chunks
→ background rerender affected chunks
```

This should be preferred to rebuilding an entire preview on every small edit.

---

## 9. Preview candidates

Current research candidates:

- GStreamer D3D11 — high-priority Windows preview prototype candidate;
- LGPL-configured libmpv — strong alternative, requires exact build/license discipline;
- libVLC — strong mature alternative;
- GStreamer Editing Services — optional richer NLE backend, not automatically required for preview.

Selection should be based on real Windows benchmarks using phone footage, especially:

- startup latency;
- seek/scrub responsiveness;
- 4K H.264/H.265 decode;
- VFR behavior;
- HDR behavior where relevant;
- CPU/GPU use;
- memory use;
- embedding complexity.

---

## 10. Hardware acceleration routing

Do not implement:

```text
GPU detected → all tasks use GPU
```

Hardware decode can become slower when frames must immediately be copied back to system RAM for CPU/CV
analysis.

Routing should be task-aware.

Examples:

- preview: hardware decode often attractive;
- final encode: hardware encode may be attractive;
- frame-heavy CPU analysis: software decode may be simpler/faster;
- local large vision model: GPU may be required or strongly preferred.

Provider abstractions should hide vendor specifics from Director/Resolver/EDL.

---

## 11. Windows render / codec research posture

Likely first output target remains MP4 with broad compatibility.

Current Windows H.264 candidates include:

- Media Foundation (`h264_mf`) baseline candidate, with software/hardware paths;
- Intel QSV/oneVPL;
- AMD AMF;
- NVIDIA NVENC;
- OpenH264 as a special fallback/installation scenario, not current first choice.

Final selection must be benchmarked for quality, speed, compatibility, CPU/GPU usage, and legal distribution.

---

## 12. Distribution/legal gates

FFmpeg/open-source-license compliance and codec-patent compliance are separate concerns.

A future approved Windows runtime should record:

- exact FFmpeg version;
- configure flags;
- enabled libraries/codecs/filters;
- binary hashes;
- source archive / build recipe;
- third-party notices;
- patent/legal review status for distributed codec capabilities.

Do not download an arbitrary FFmpeg or mpv binary from the web and redistribute it as a product runtime.

Formal commercial release should include a dedicated Codec/Distribution Legal Gate.

---

## 13. Open questions

- automatic vs user-confirmed prerequisite installation boundaries;
- package manager / installer strategy for optional capability tiers;
- whether Python is bundled privately or exposed as an external prerequisite;
- exact GStreamer/libmpv/libVLC preview winner;
- adaptive proxy profile benchmark design;
- approved FFmpeg build profile;
- default CPU H.264 encoder after quality benchmarking;
- disk-quota and cache-cleanup policy;
- how Environment Doctor exports safe diagnostic context to an external AI assistant without exposing secrets.
