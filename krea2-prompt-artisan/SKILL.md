---
name: krea2-prompt-artisan
description: Use when the user asks for a Krea2, Krea 2, K2, Krea.ai, "k2提示词", "K2化", "生成一段k2提示词", or "将下面的提示词K2化" image-generation prompt, or asks Codex to turn a text idea or reference image into a Krea 2-ready prompt; always create a local HTML deliverable with copy controls by default.
---

# Krea2 Prompt Artisan

Use this skill to turn a text idea, detailed visual brief, or reference image into a high-density Krea 2 / Krea.ai Turbo prompt. Produce a polished English prompt, a faithful Chinese translation, and always render a local HTML page for reading, copying, the one-line punctuated poem, and the Codex footer signature.

## Workflow

1. Identify the input type:
   - Text-only idea or brief: work directly from the user's description.
   - Reference image: first analyze the image with Codex's available vision capability. For images pasted directly into the Codex chat, use the attached image itself; do not depend on QQ/WeChat/cache filesystem paths. Do not copy pasted images into the workspace unless the attachment is not visible, the resolution is insufficient, or file-based tooling is truly required. If a temporary image file is unavoidable, save it under the current workspace or the system temporary directory, use it, then delete it after verification.

2. Read `references/krea2_system_prompt.md` before generating the prompt unless the current conversation already contains those rules.

3. Generate one continuous English prompt for Krea 2:
   - Write natural prose, not a labeled checklist.
   - Default to at least 500 English words; prefer 650-850 words when the user did not ask for a shorter prompt.
   - Cover subject details, intended use and aspect ratio, environment, composition/camera, lighting, style/medium, materials/colors, and quality safeguards.
   - Include negative constraints naturally, such as no text, no logo, no watermark, no malformed anatomy, and no extra fingers when relevant.

4. Provide a faithful Chinese translation:
   - Match the English content closely.
   - Do not compress a long English prompt into a short Chinese summary.
   - Preserve every important visual detail.

5. Prepare display metadata:
   - `title_cn` or `chinese_title`: mandatory full Chinese title name. Use a concise Chinese title, ideally 6-18 Chinese characters and usually no more than 24. Do not abbreviate it in `filename_title`. The renderer uses this same Chinese title name in two places: the visible page title is `Krea 2 提示词 - 标题名` with a relevant emoji prefix, such as `🎬 Krea 2 提示词 - 红妆庭院贵族仕女`; the file name is `Krea2_prompt_标题名.html`, such as `Krea2_prompt_红妆庭院贵族仕女.html`. The `标题名` part must be identical in both places, fully Chinese, and contain no English letters. Also choose a suitable `title_emoji` from the prompt content when possible, such as flowers, night, ocean, city, forest, books, coffee, cinematic, or fantasy motifs.
   - `scene_name`: optional short display scene name; prefer Chinese when used, but do not use it as a shorter replacement for `title_cn`.
   - `intro_text`: one or two sentences summarizing the user's request and the chosen visual direction.
   - `breakdown_rows`: eight rows for subject details, canvas/use, environment, composition/camera, lighting/tone, style/medium, materials/colors, and quality safeguards. Each row must include non-empty design reasoning via `rationale` or a supported alias such as `logic`, `design_logic`, `consideration`, `reasoning`, `why`, `note`, or `设计考虑`. Use the canonical English slot names or explicit `slot_cn`/`slot_en`; the HTML renderer displays the module column as Chinese plus English, with the Chinese label in a colorful accent and English in body-muted color. The renderer has a fallback, but agents should still provide real row-specific rationale.
   - `optimization_notes`: short notes explaining important prompt-design choices. When Advanced Stylization Mode is used, briefly state the cross-domain mapping source and which generic default aesthetics were removed.
   - `poem`: **七言绝句单行铁律**：`{{POEM}}` 必须现场原创一首应景贴题、绝不重复的**七言四句诗**。必须恰好 28 个中文正文字符（标点和首尾 🌸 不计入字数），四句每句七字。为了排版精美，整首诗**必须写在同一行（不使用 `<br>` 换行）**，每句加规范中文标点，推荐节奏为“七字，七字。七字，七字。”，首尾只用 🌸 符号包裹；诗句正文不得出现其他 emoji、图标或装饰符号。不满足 28 字或含有额外符号时渲染器会拒绝生成 HTML。
   - `signature`: use `—— Codex 协助整理，愿灵感顺手成图 🌸` for the HTML footer signature.

6. Always render the HTML deliverable:
   - For every completed Krea2/K2 prompt task, run `scripts/render_krea2_html.py` with the generated data. Do not wait for the user to ask for HTML.
   - By default, the script writes `.html` files under the current Codex working directory:

```text
<current working directory>\Krea2提示词
```

     This resolves to a project-local output folder named `Krea2提示词` under the current working directory. The renderer creates this directory automatically if it does not exist. For a custom location, pass `--output-dir <path>` or set the `KREA2_OUTPUT_DIR` environment variable.

   - Use this JSON schema for the renderer payload: `title_cn` or `chinese_title` (mandatory full Chinese page/file title), optional matching `filename_title`, `scene_name`, optional `title_emoji`, `intro_text`, `prompt_text` for the English prompt, `translation_text` for the Chinese translation, `breakdown_rows`, `optimization_notes`, `poem`, and optional `signature`. The renderer also accepts `scene_name_cn`, `english_prompt`, and `chinese_prompt` as aliases, but prefer `title_cn`, `prompt_text`, and `translation_text`.
   - Do not open the page during initial rendering. Render first without `--open`, inspect the generated HTML for title, prompt text, translation text, non-empty breakdown rationales, poem, signature, encoding, and absence of direct `.json` leftovers. Only after these checks pass, open the already-created file as the final step with `scripts/render_krea2_html.py --open-existing <html path>`.
   - Because opening starts the user's default browser, run the final `--open-existing` command with escalated shell permissions when available. In the Codex Windows sandbox, a normal run can return `opened: false` or WinError 5. If that happens, rerun only the open-existing command with escalation instead of silently accepting no popup.
   - Omit the final open step only when the user explicitly says not to open the browser.
   - Prevent encoding damage: do not pipe JSON through a default Windows PowerShell native pipeline unless UTF-8 is set first. Prefer passing a UTF-8 JSON file with `--input`, or set `$OutputEncoding=[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)` and `$env:PYTHONUTF8='1'` before piping JSON to Python. The renderer writes HTML as UTF-8 with BOM and refuses to generate a page if Chinese/emoji fields have already turned into `??` question-mark mojibake.
   - Do not create `.md` or any Markdown file as the final deliverable; Markdown may only be an internal draft.
   - Do not leave payload `.json` files directly in the `Krea2提示词` output directory. Prefer piping JSON through stdin. If a `.json` payload file is passed with `--input`, the renderer deletes only that input file after successful HTML generation, and only when it is a direct child of the output directory. It does not delete unrelated `.json` files and does not recurse into subfolders.
   - If opening the page fails, still return the created `.html` file path and state that opening failed.

## Output Expectations

In chat, keep the response concise:

- State that the Krea 2 prompt is ready.
- Include the created `.html` file path and whether it was opened in the browser.
- Treat the HTML file as the primary deliverable; do not stop after chat text or a Markdown document.
- Include the English prompt and Chinese translation directly only when the user asks for them in chat.

## Boundaries

- Do not modify external application workspaces, model settings, Python runtimes, node_modules, or unrelated workspace files.
- Do not write output to another application's workspace by default.
- Do not call unrelated image-generation tools or hard-code provider-specific model IDs.
- Do not generate the final image unless the user separately asks for image generation.
