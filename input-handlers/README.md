# Input Handlers

This layer contains utilities that ingest raw inputs and produce structured outputs that downstream services can consume.

## Contents

| Component | Description | Usage |
| --- | --- | --- |
| PDF Parser | Client utilities to call a PDF parsing backend and normalize its response | [README](pdf/parser/README.md) |
| PDF Viewer | Viewer app to visualize parsed PDF content | [README](pdf/viewer/README.md) |

## Quick start

Typical flow:

1. Use the **PDF Parser** to produce structured output.
2. Open the **PDF Viewer** to validate the extracted content.
