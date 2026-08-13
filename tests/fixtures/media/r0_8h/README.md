# R0.8H Local Media Corpus

The media files remain local under the gitignored `example/` directory. The tracked
`corpus_manifest.json` records anonymous content identity, technical metadata and reviewed
coarse coverage only. It contains no local paths, transcripts or personal information.

Generate or validate it with:

```powershell
uv run python tools/media_corpus_manifest.py --media-root example `
  --manifest tests/fixtures/media/r0_8h/corpus_manifest.json `
  --ffprobe .tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin/ffprobe.exe

uv run python tools/media_corpus_manifest.py --media-root example `
  --manifest tests/fixtures/media/r0_8h/corpus_manifest.json `
  --ffprobe .tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin/ffprobe.exe --check
```

Coverage is human-confirmed. Newly discovered content starts with an empty coverage list.
