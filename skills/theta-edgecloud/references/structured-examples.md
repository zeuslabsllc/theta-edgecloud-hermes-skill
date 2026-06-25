# Structured Theta EdgeCloud examples

These examples are safe templates. Replace IDs, URLs, and credentials with your own values. Use `THETA_DRY_RUN=1` before paid or mutating operations.

## Official MCP: `gpt_oss_120b`

Use `stream: false` inside `input` so the official MCP server receives JSON instead of SSE chunks.

```json
{
  "service": "gpt_oss_120b",
  "input": {
    "messages": [
      {"role": "user", "content": "Reply exactly: Theta MCP OK"}
    ],
    "max_tokens": 64,
    "temperature": 0.3,
    "stream": false
  },
  "wait": 60
}
```

## Official MCP: `qwen3`

```json
{
  "service": "qwen3",
  "input": {
    "messages": [
      {"role": "user", "content": "Convert this JSON to a Python dataclass: {\"name\": \"string\", \"age\": \"int\"}"}
    ],
    "max_tokens": 512,
    "temperature": 0.3,
    "stream": false
  },
  "wait": 60
}
```

If Theta returns `409 No instances available`, retry later; that is a capacity response, not a local configuration failure.

## Official MCP: Flux image generation

```json
{
  "service": "flux",
  "input": {
    "prompt": "A cinematic product photo of a blue AI cloud icon on a dark background",
    "num_inference_steps": 4
  },
  "wait": 60
}
```

## Official MCP: Stable Diffusion XL Turbo

```json
{
  "service": "stable_diffusion_xl_turbo",
  "prediction": "predict",
  "input": {
    "prompt": "A small blue cloud icon, simple vector style",
    "steps": 2,
    "guidance": 0
  },
  "wait": 60
}
```

## Official MCP: Whisper

1. Get an upload URL:

```json
{
  "service": "whisper",
  "input_field": "audio_filename"
}
```

2. Upload the file to the returned URL.
3. Run inference with the uploaded filename/key:

```json
{
  "service": "whisper",
  "input": {
    "audio_filename": "UPLOADED_AUDIO_FILENAME"
  },
  "wait": 0
}
```

Then poll with `get_request_status(request_id="infr_rqst_...")`.

## Official MCP: LLaVA

```json
{
  "service": "llava",
  "input": {
    "image": "UPLOADED_IMAGE_OR_URL",
    "prompt": "Describe the image in one sentence."
  },
  "wait": 60
}
```

## Official MCP: Step Video / long media jobs

Use async mode for long-running video jobs:

```json
{
  "service": "step_video",
  "input": {
    "prompt": "A 3 second shot of a blue cloud logo forming from particles"
  },
  "wait": 0
}
```

Then poll with `get_request_status`.

## Direct helper: disposable dedicated validation

```bash
THETA_DRY_RUN=1 python scripts/theta_edgecloud.py controller-validate-disposable \
  --org-id org_demo \
  --probe openai \
  --payload-json '{"project_id":"prj_demo","deployment_template_id":"img_demo"}'
```

Real paid/mutating validation requires `--yes` and valid Theta controller credentials.

## Direct helper: dedicated endpoint readiness

```bash
python scripts/theta_edgecloud.py dedicated-ready \
  --probe openai \
  --ready-timeout 900 \
  --interval 15
```

Use `--probe gradio` for Gradio-style templates that expose `/config` instead of `/v1/models`.
