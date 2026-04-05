# Kling AI — API reference

| Subcommand | Endpoints |
|------------|-----------|
| video | POST/GET /v1/videos/text2video, /v1/videos/image2video, /v1/videos/omni-video |
| image | POST/GET /v1/images/generations, /v1/images/omni-image |
| element | POST/GET /v1/general/advanced-custom-elements, /v1/general/advanced-presets-elements; POST /v1/general/delete-elements |

All APIs use Bearer token. Priority: stored AK/SK under `~/.config/kling/.credentials` or `KLING_STORAGE_ROOT/.credentials` first (JWT per request); if missing, use `KLING_TOKEN` (shell env first, then `kling.env` injection). Submit returns `task_id`; poll `{path}/{task_id}` until status succeed/failed, then use `output` or `task_result` for URLs.

## Model docs

Official model docs (paths may vary by site locale):

- [video models](https://klingai.com/document-api/apiReference/model/videoModels)
- [Omni video](https://klingai.com/document-api/apiReference/model/OmniVideo)
- [text-to-video](https://klingai.com/document-api/apiReference/model/textToVideo)
- [image models](https://klingai.com/document-api/apiReference/model/imageModels)
- [Omni image](https://klingai.com/document-api/apiReference/model/OmniImage)
- [image generation](https://klingai.com/document-api/apiReference/model/imageGeneration)
