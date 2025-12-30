# Tasks / Services

This layer contains runnable microservices for common document/text workflows (RAG-oriented building blocks). Most tasks include their own `deployment/` assets and a runnable implementation under `src/`.

## Contents

### Text

| Task | Description | Docs | Path |
| --- | --- | --- | --- |
| Dataprep | Prepares/cleans text for downstream workflows | [README](text/dataprep/src/README.md) | [text/dataprep](text/dataprep) |
| Retrievers | Fetches relevant context from a vector store | [README](text/retrievers/src/README.md) | [text/retrievers](text/retrievers) |
| Summarization | Summarizes long content into concise outputs | [README](text/summarization/src/README.md) | [text/summarization](text/summarization) |
| Tagging | Auto tag/label text content | [README](text/tagging/src/README.md) | [text/tagging](text/tagging) |

### Speech

| Task | Description | Docs | Path |
| --- | --- | --- | --- |
| ASR (Wav2vec2) | Converts speech to text | [README](speech/asr/Wav2vec2/README.md) | [speech/asr/Wav2vec2](speech/asr/Wav2vec2) |
| Translation (IndicTrans2) | Indic-focused translation | [README](speech/translation/IndicTrans2/README.md) | [speech/translation/IndicTrans2](speech/translation/IndicTrans2) |
| TTS (fastspeech2_HS) | Converts text to speech | [README](speech/text2speech/fastspeech2_HS/README.md) | [speech/text2speech/fastspeech2_HS](speech/text2speech/fastspeech2_HS) |

### Shared cores

Common foundations used by multiple services live under [cores](cores) (orchestration, protocol/types, storage adapters, telemetry, etc.).

## Quick start

Pick a task from the tables above and follow its README for run/config details.
