#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
AIComps: Production-ready, modular AI components for document and text processing workflows.
"""

from .tasks.version import __version__

# Export commonly used components from tasks subpackage
from .tasks import (
    # Documents
    Audio2TextDoc,
    Base64ByteStrDoc,
    DocPath,
    EmbedDoc,
    GeneratedDoc,
    LLMParamsDoc,
    SearchedDoc,
    SearchedMultimodalDoc,
    RerankedDoc,
    TextDoc,
    MetadataTextDoc,
    RAGASParams,
    RAGASScores,
    LVMDoc,
    LVMVideoDoc,
    ImagePath,
    ImagesPath,
    VideoPath,
    ImageDoc,
    SDOutputs,
    TextImageDoc,
    MultimodalDoc,
    EmbedMultimodalDoc,
    FactualityDoc,
    ScoreDoc,
    PIIRequestDoc,
    PIIResponseDoc,
    Audio2text,
    DocSumDoc,
    PromptTemplateInput,
    TranslationInput,
    
    # Constants
    MegaServiceEndpoint,
    ServiceRoleType,
    ServiceType,
    
    # Microservice
    ServiceOrchestrator,
    ServiceOrchestratorWithYaml,
    MicroService,
    register_microservice,
    opea_microservices,
)

__all__ = [
    "__version__",
    # Documents
    "Audio2TextDoc",
    "Base64ByteStrDoc",
    "DocPath",
    "EmbedDoc",
    "GeneratedDoc",
    "LLMParamsDoc",
    "SearchedDoc",
    "SearchedMultimodalDoc",
    "RerankedDoc",
    "TextDoc",
    "MetadataTextDoc",
    "RAGASParams",
    "RAGASScores",
    "LVMDoc",
    "LVMVideoDoc",
    "ImagePath",
    "ImagesPath",
    "VideoPath",
    "ImageDoc",
    "SDOutputs",
    "TextImageDoc",
    "MultimodalDoc",
    "EmbedMultimodalDoc",
    "FactualityDoc",
    "ScoreDoc",
    "PIIRequestDoc",
    "PIIResponseDoc",
    "Audio2text",
    "DocSumDoc",
    "PromptTemplateInput",
    "TranslationInput",
    
    # Constants
    "MegaServiceEndpoint",
    "ServiceRoleType",
    "ServiceType",
    
    # Microservice
    "ServiceOrchestrator",
    "ServiceOrchestratorWithYaml",
    "MicroService",
    "register_microservice",
    "opea_microservices",
]
