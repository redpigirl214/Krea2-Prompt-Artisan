# Krea 2 Prompt Rules

Use these rules when writing prompts for Krea 2 / Krea.ai Turbo.

## Core Shape

Write a single continuous English paragraph that can be pasted directly into Krea 2. Avoid labels such as `Subject:`, numbered lists, or markdown bullets inside the actual prompt.

Default length:

- Minimum: 500 English words unless the user asks for a shorter prompt.
- Preferred: 650-850 English words for rich scenes, portraits, cinematic images, product images, and concept art.

Krea 2 tends to reward dense visual specificity. Add detail through meaningful visual information, not filler.

## Eight Information Blocks

Balance the prompt across these blocks:

1. Subject details: identity, shape, quantity, pose/action, state, proportions, surface traits, priority details.
2. Canvas and use: intended output type, aspect ratio, product shot, portrait, cover, architecture, anime, concept art, etc.
3. Environment: place, time, weather, atmosphere, foreground, midground, background, spatial depth.
4. Composition and camera: framing, distance, focal length, angle, subject scale, negative space, leading lines, focus.
5. Lighting and tone: key light, fill light, rim light, shadow softness, color temperature, contrast, reflections, highlights.
6. Style and medium: photography, cinematic still, product photography, anime illustration, concept art, architectural photography, editorial style, etc.
7. Materials and colors: textures, material finish, color palette, reflections, grain, realistic flaws.
8. Quality safeguards and exclusions: clarity, no text, no logo, no watermark, no distorted anatomy, no extra fingers, no visual artifacts when relevant.

The final English prompt should feel like one coherent visual direction, not eight stitched-together sections.

## Adaptation Heuristics

Product image:
Emphasize clean composition, material accuracy, brand-neutral polish, controlled lighting, crisp contours, and practical negative constraints such as no text or logo unless explicitly requested.

Short-video cover or poster:
Emphasize strong central subject, vertical composition when appropriate, readable negative space for later title placement, dramatic but not cluttered lighting, and no real text in the generated image unless requested.

Portrait:
Emphasize facial clarity, natural skin texture, expression, anatomy, hands if visible, hair, eyes, wardrobe, and lens behavior.

Architecture:
Emphasize vertical lines, scale, spatial depth, weather, materials, believable structural geometry, and natural light behavior.

Anime or illustration:
Emphasize clean linework, color design, stylized anatomy, cinematic staging, rendering medium, and controlled detail density.

Concept art:
Emphasize scale, atmosphere, silhouette readability, story cues, environmental design, and painterly or cinematic worldbuilding.

## Advanced Stylization Mode

Use this only when the request asks for atmosphere, cinematic feeling, premium editorial mood, literary melancholy, dreamlike isolation, or highly refined art direction.

Add:

- Cross-domain mapping: borrow texture, palette, lighting, or compositional rules from a surprising but relevant domain.
- Default aesthetic removal: explicitly steer away from common generic AI defaults for that subject.

Skip this mode for cheerful, cute, commercial product, energetic combat, bright family, or simple practical prompts.

## Chinese Translation

Translate faithfully into Chinese after the English prompt. The Chinese translation should preserve almost all visual details and should not become a short summary.

## Self Check

Before finishing, verify:

- The English prompt is long enough and not a checklist.
- The subject, scene, composition, lighting, style, materials, and exclusions are all represented.
- The Chinese translation has comparable information density.
- The prompt does not request visible text, logos, or watermarks unless the user explicitly requested them.
