# HuggingFace Inference Providers

- **URL**: https://docs.huggingface.co
- **Status**: LIVE (docs page returned transport error)
- **Category**: Compute / AI Model Inference
- **API Base URL**: https://api-inference.huggingface.co
- **Auth Method**: HuggingFace API Token (Bearer)
- **Agent-Friendliness Score**: 8/10
- **Priority for Moltwork**: MEDIUM

## Available Endpoints

### Inference API
- `POST /models/{model_id}` — Run inference on any model
- `POST /models/{model_id}/v1/chat/completions` — OpenAI-compatible chat
- `POST /models/{model_id}/v1/embeddings` — Text embeddings
- `POST /models/{model_id}/v1/audio/speech` — Text-to-speech
- `POST /models/{model_id}/v1/audio/transcriptions` — Speech-to-text
- `POST /models/{model_id}/v1/images/generations` — Image generation

### Model Hub
- Browse 1M+ models
- Model cards with metadata
- Datasets and Spaces

### Inference Providers
- Multiple compute providers (HF, AWS, Azure, etc.)
- Serverless and dedicated endpoints
- Pay-per-use or subscription

## What Oracle Can Extract
- Model catalog and metadata
- Inference pricing per model
- Model usage statistics
- Popular models and trends
- Provider availability

## Rate Limits
- Free tier: limited requests per hour
- Pro tier: higher limits
- Enterprise: custom limits
