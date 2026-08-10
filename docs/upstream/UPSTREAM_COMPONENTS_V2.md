# Upstream Component Ledger V2

**Status:** ACTIVE CANDIDATE LEDGER — post Survey V2  
**Date:** 2026-08-11  
**Policy:** `UPSTREAM_POLICY_V2.md`  
**Architecture:** `docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md`

This ledger records current engineering posture. It is **not** a blanket legal approval list.

Before any new direct dependency/source migration, replace `TBD` with an exact upstream revision and complete the release gate.

## Status vocabulary

- `DIRECT-APPROVED` — dependency/revision has passed the required project gate for the stated use.
- `DIRECT-CANDIDATE` — technically/licensing-wise promising; still needs exact revision/benchmark/release review.
- `PROTOTYPE-CANDIDATE` — suitable for isolated benchmark/prototype behind a Port, not production dependency yet.
- `REFERENCE-STRONG` — strongly useful mechanism/architecture; reimplement/adapt behind local contracts.
- `REFERENCE-ONLY` — idea source only; direct use unattractive/incompatible.
- `BLOCKED-LICENSE` — known license/model/terms obstacle for normal proprietary commercial distribution.
- `BLOCKED-REVIEW` — model/data/transitive terms unresolved.

---

## Core pipeline / editing references

| Upstream | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| FireRed-OpenStoryline | pipeline, media, render engineering | Apache-2.0 at reviewed baseline; existing R0.1 work independently reimplemented | REFERENCE-STRONG / selective direct candidate | Application pipeline, shot detection/media/render patterns; no upstream Domain ownership |
| MoneyPrinterTurbo | provider/caching/retry/provenance engineering | MIT at reviewed baseline | REFERENCE-STRONG | Audio/provider engineering only; **remote visual-stock behavior neutralized** |
| CutClaw | Director/Resolver/search/review architecture | no sufficiently clear reusable-license basis in original audit | REFERENCE-ONLY | source copying forbidden; independent reimplementation |
| agentic-video-editor | retrieval→deep inspect→trim→review reference | exact adoption review TBD | REFERENCE-STRONG | mechanism only; its exact-timestamp EditPlan semantics are not adopted |
| OpenMontage | agent/tool/checkpoint/quality patterns | AGPL/product mismatch | REFERENCE-ONLY | generated/remote visual paths neutralized |
| X-Cut | portable editing style/skill ideas | AGPL + generative-media mismatch | REFERENCE-ONLY | CommercialSkill/style-recipe concepts only |
| VideoAgent research | cost-aware agent/task graph | paper/research artifact | REFERENCE-STRONG | intent/tool filtering, reduce unnecessary model calls |
| Crayotter research | inspectable editing artifacts | paper/research artifact | REFERENCE-STRONG | retrieval reports/blueprints/tool calls/intermediate renders as artifacts |

---

## Shot detection / media understanding

| Upstream | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| soCzech/TransNetV2 | shot detection inference contract | original reviewed source/model provenance already documented | REFERENCE-STRONG | current ShotDetector seam; identity owned locally |
| allenday/transnetv2_pytorch | optional Torch runtime reference | package exact release approval pending | PROTOTYPE-CANDIDATE | optional runtime adapter only |
| OpenTAD | temporal action localization | dependency/model stack review required | REFERENCE-STRONG | optional temporal evidence provider, not baseline |
| MMAction2 | action recognition/localization | large dependency/model matrix | REFERENCE-STRONG | optional advanced provider; no baseline dependency |
| VideoITG | coarse-to-fine temporal information gathering | model/weights not approved for default commercial distribution | REFERENCE-STRONG | information-gathering strategy only |
| OpenCV | motion/tracking/quality/local CV | Apache-2.0 current project; model files separately reviewed | DIRECT-CANDIDATE | Tier-0 deterministic motion/global camera/tracking utilities |
| MediaPipe | face/hand/pose/on-device tasks | Apache-2.0 framework; individual task-model terms still audited | DIRECT-CANDIDATE | optional Tier-1 geometry provider |
| SAM 2 | promptable segmentation/tracking | upstream code/published checkpoints reported Apache-2.0; exact release revision TBD | PROTOTYPE-CANDIDATE | optional GPU/local enhancement |
| CoTracker | point tracking reference | majority current project CC-BY-NC | BLOCKED-LICENSE / REFERENCE-ONLY | algorithm reference only |

---

## Speech / dialogue

| Upstream | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| faster-whisper | local ASR, word timestamps | code/runtime/model-family exact release audit required | DIRECT-CANDIDATE | CPU-capable SpeechRecognitionPort baseline candidate |
| Silero VAD | speech ranges | MIT project/model candidate; exact bundled artifact review | DIRECT-CANDIDATE | lightweight VAD provider |
| WhisperX | alignment/diarization workflow | downstream alignment/diarization model terms vary | BLOCKED-REVIEW | architecture reference/prototype only until all models approved |
| FunClip | transcript selection→timestamp edit pattern | exact dependency/adoption review TBD | REFERENCE-STRONG | proves semantic phrase selection should map to ASR timestamps |
| ClipsAI | speaker-aware clip/reframe workflow | MIT top-level; WhisperX/Pyannote/FaceNet/MediaPipe stack needs separate review | REFERENCE-STRONG | speaker segmentation/reframe ideas; no direct approval |

---

## Retrieval / embeddings

| Upstream / model | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| FAISS | exact/ANN vector search | MIT | DIRECT-CANDIDATE if scale needs it | not first mandatory dependency; benchmark exact local scan first |
| sqlite-vec | embedded SQLite vectors | MIT/Apache-2.0; pre-v1/breaking-change risk | PROTOTYPE-CANDIDATE | ShotIndex implementation only, never Domain schema dependency |
| Qdrant | vector DB/hybrid retrieval reference | Apache-2.0 | REFERENCE-STRONG | too heavy as mandatory first desktop server; RRF/hybrid ideas useful |
| FastEmbed | ONNX local embedding runtime pattern | exact package/model review per selected version | PROTOTYPE-CANDIDATE | CPU ONNX deployment pattern |
| paraphrase-multilingual-MiniLM-L12-v2 | multilingual embedding candidate | Apache-2.0 model card at surveyed revision | PROTOTYPE-CANDIDATE | benchmark only |
| multilingual-e5-small | multilingual embedding candidate | MIT model card at surveyed revision | PROTOTYPE-CANDIDATE | benchmark only |
| BGE small zh/en | lightweight language-specific embedding candidates | MIT model cards at surveyed revision | PROTOTYPE-CANDIDATE | benchmark/cross-language comparison |

---

## Music / audio analysis and selection

| Upstream / provider | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| librosa | lightweight MIR/DSP baseline | permissive current project; exact release TBD | DIRECT-CANDIDATE | BeatAnalysis helpers |
| Beat This! | beat/downbeat model | code/model/training provenance requires final release review | PROTOTYPE-CANDIDATE | BeatMap benchmark |
| libsonare | CPU-oriented local music analysis | promising permissive posture; benchmark/revision review pending | PROTOTYPE-CANDIDATE | BeatMap/music-analysis benchmark |
| Essentia | rich MIR/DSP | AGPL concerns for proprietary product | REFERENCE-ONLY | algorithms/features reference |
| BeatSync Engine | beat/musical sync reference | licensing review required | REFERENCE-ONLY | BeatMap ideas only |
| LAION-AI/CLAP | audio-text semantic retrieval | source openly licensed; upstream notes copyrighted/restricted training data; checkpoint/data gate remains | REFERENCE-STRONG / PROTOTYPE | do not release-approve from code license alone |
| microsoft/CLAP code | audio-text semantic retrieval | MIT code | PROTOTYPE-CANDIDATE | CPU-capable implementation reference |
| microsoft/msclap weights | pretrained CLAP weights | model card currently `ms-pl`, different from code license | BLOCKED-REVIEW | must interpret/approve model terms before bundle/use |
| Jamendo API / Licensing | commercial music discovery/license reference | provider/API/license-product terms; per-track/project evidence required | PROTOTYPE-CANDIDATE | Rights-aware MusicProvider candidate |
| YouTube Audio Library | platform music source/reference | YouTube-specific safety/attribution context; no universal off-platform guarantee | REFERENCE-STRONG / user acquisition | preserve platform scope; not generic universal provider |
| Freesound | SFX source/reference | per-item CC0/BY/BY-NC; API commercial terms separate | REFERENCE-STRONG | SFX rights-gate reference |
| Spotify Pedalboard | audio effect chain | GPLv3 | BLOCKED-LICENSE / REFERENCE-ONLY | effect-chain/DSP UX ideas; FFmpeg baseline preferred |
| VTMR / VMMR-ReaL research | video→music retrieval and moment localization | research papers/datasets separately gated | REFERENCE-STRONG | coarse retrieval→temporal rerank / music moment task |

---

## Timeline / render / preview / subtitle

| Upstream | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| FFmpeg / ffprobe | primary deterministic media backend | LGPL default family; GPL/nonfree/external-lib/build configuration materially changes distribution obligations | DIRECT-CANDIDATE / ADR-001 | approved build profile required before release |
| OpenTimelineIO | rational time/interchange | permissive upstream; exact release TBD | DIRECT-CANDIDATE | optional MediaTime/interchange adapter; Domain EDL remains authority |
| libass | subtitle renderer | ISC upstream | DIRECT-CANDIDATE | standard subtitle render baseline candidate |
| HyperFrames | deterministic complex text/motion graphics | exact revision/license benchmark review TBD | PROTOTYPE-CANDIDATE | complex CTA/title/card renderer seam |
| GStreamer | Windows preview/D3D11 | LGPL core with plugin/package license variation | PROTOTYPE-CANDIDATE | preview benchmark candidate; package whitelist required |
| GStreamer Editing Services | optional NLE/timeline backend | LGPL family with transitive plugin review | PROTOTYPE-CANDIDATE | optional future backend, never Domain authority |
| MLT | mature NLE framework | LGPL core + module/license complexity | REFERENCE-STRONG / optional backend | do not adopt second timeline semantics without need |
| OpenShot/libopenshot | NLE reference | LGPL/commercial options + transitive dependencies | REFERENCE-STRONG | not preferred first render core |
| MoviePy | high-level media composition | MIT | REFERENCE-ONLY for production backend | prototypes only; FFmpeg direct execution preferred |
| libmpv | preview candidate | default/build licensing must be controlled; LGPL configuration possible | PROTOTYPE-CANDIDATE | benchmark exact approved build |
| libVLC | preview candidate | LGPL core; packaging/plugin review | PROTOTYPE-CANDIDATE | Windows preview benchmark |

---

## Auto Reframe / spatial composition

| Upstream | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| Google AutoFlip | intelligent aspect-ratio/crop-path architecture | historical open-source reference | REFERENCE-STRONG | shot/saliency/path ideas; generative uncrop/inpainting ideas neutralized |
| Watch to Edit | smooth crop-window optimization | research paper | REFERENCE-STRONG | cinematography-constrained path optimization |
| LIVE-YT VC / SmartVidCrop research | portrait-crop human benchmark/method | dataset/source licenses must be audited before training use | REFERENCE-STRONG | benchmark/method only |
| KazKozDev/auto-vertical-reframe | modern scene/subject/camera-state implementation | MIT top-level, but core Ultralytics YOLO dependency/models trigger AGPL/Enterprise issue for proprietary product | BLOCKED-LICENSE / REFERENCE-STRONG | borrow CameraObservation/State, lock/damping/telemetry ideas; no default dependency |
| Ultralytics YOLO stack | detector/segmentation used by some references | current upstream says proprietary commercial embedding needs Enterprise unless AGPL-compatible release | BLOCKED-LICENSE unless explicit commercial agreement | ObjectLocalizationPort must remain vendor-neutral |

---

## Quality / optimization

| Upstream | Role | License / caveat snapshot | Status | Local seam / note |
|---|---|---|---|---|
| VMAF/libvmaf | reference-vs-render fidelity | permissive source/patent notice at surveyed baseline | DIRECT-CANDIDATE | codec/scaling regression, not editorial score |
| OpenCV quality | BRISQUE/SSIM/etc | Apache source; auxiliary model license reviewed separately | PROTOTYPE-CANDIDATE | technical quality evidence |
| OR-Tools CP-SAT | general constraint solver | Apache-2.0 | DIRECT-CANDIDATE if complexity requires | later optimizer escalation; not first required dependency |
| BEAT research | elastic music/visual sequence optimization | paper/implementation exact reuse review TBD | REFERENCE-STRONG | supports beam/DP elastic rhythm idea |
| EditIQ research | explicit cinematic sequence energy optimization | research | REFERENCE-STRONG | supports semantic evidence + deterministic optimization split |

---

## Direct-adoption checklist

Before changing any candidate to `DIRECT-APPROVED`, record:

1. exact repository/model/provider revision;
2. source-code license text at that revision;
3. model/checkpoint license;
4. training/data caveats relevant to distribution/use;
5. transitive native/package licenses;
6. commercial API/provider terms where relevant;
7. codec/patent concerns where relevant;
8. Windows installation/runtime behavior;
9. CPU/GPU requirements;
10. local capability seam/destination;
11. copied/adapted/independently reimplemented classification;
12. required notices/source offer/build recipe;
13. benchmark evidence;
14. release approval owner/date.

No `REFERENCE-*` entry authorizes code copying.
