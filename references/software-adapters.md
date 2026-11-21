# Software and generative pipeline adapters

Read this before writing automation for a creative tool, choosing a render path, or planning a generative pipeline.

Contents
1. Ground rules for tool claims
2. Code-driven and procedural motion
3. Compositing and editing
4. Generative video and audio: the three-layer pattern
5. What needs which licence

Everything here is dated. Capabilities, prices and model line-ups change within months; statuses and re-check queries are in `freshness-ledger.md`. If the plan depends on one of these facts and you can search the web, verify it first.

---

## 1. Ground rules for tool claims

- **Never invent an API method.** If you have not seen it in the tool's documentation, do not write it. Say what you would need to check.
- **Never assume a plugin, licence or edition.** Ask, or write the plan so it works on the free tier and note what the paid tier would add.
- **Check every return value** when scripting host applications; several fail silently.
- **Say what you ran.** "Here is a script" and "I ran this script" are different claims.

## 2. Code-driven and procedural motion

**Remotion (React, programmatic video).** Best for data-driven explainers, kinetic typography, batch variations from a spreadsheet, repeatable brand templates.
- New project: `npx create-video@latest --yes --blank my-video`.
- Official Agent Skills: `npx remotion skills add` inside the project, or `npx skills add remotion-dev/skills`. Use them alongside this skill when writing Remotion code; they cover the API, this skill covers what to make.
- Core API: `useCurrentFrame()`, `useVideoConfig()`, `spring()`, `interpolate()`. Render with `npx remotion render <CompositionId> out.mp4`.
- Licence: free for individuals and companies of up to 3 people; larger companies need a company licence (listed at $25 per seat per month for the creators plan in November 2026). A licence change has been flagged for version 5; check before committing a team.

**Cavalry (procedural 2D).** Node-based duplicators, CSV import, Lottie and rendered video output. Good for batch 2D motion systems and brand rigs. No interactive state-machine runtime. Reported acquired by Canva in 2026 and still shipping standalone.

**Rive (interactive runtime motion).** State-machine editor with open-source runtimes for web, iOS, Android and Flutter. Best for interactive product and UI motion that responds to input; weak for batch-rendered video.

**Blender (`bpy`, Geometry Nodes, Grease Pencil).**
- Headless: `blender -b file.blend --python <your script>`. The desktop build can write video through FFmpeg directly.
- The standalone `pip install bpy` module may not include the bundled FFmpeg: render a PNG sequence and assemble it with system `ffmpeg`.
- Blockout bridge: export a 3D camera and pose animation plus the first frame, restyle frame 1, then feed both to a motion-reference video model for a controlled camera move.

**Houdini (`hython`, TOPs/PDG).** Procedural Dependency Graphs for data-driven, headless 3D and VFX batch work.

## 3. Compositing and editing

**Adobe After Effects.**
- **UXP plugins** entered public beta in After Effects (Beta) 27.1 with UXP 9.4, announced 17 November 2026. Adobe's roadmap puts general availability in Q2 2027. Build new panels in UXP, on the beta channel for now.
- **CEP panels**: Adobe's migration timeline has the Marketplace cut-off and default disabling of CEP panels in December 2028.
- **Standalone ExtendScript** (`.jsx`, ScriptUI) still works and is the safe default for lightweight, repeatable project automation today.

**DaVinci Resolve.**
- From **21.1** (September 2026), Blackmagic moved Python scripting to the **Studio** edition: "Advanced scripting now requires DaVinci Resolve Studio." Python 2 support is gone. External scripting, workflow integrations, UIManager interfaces and the built-in MCP server are Studio features.
- **Free edition:** reports conflict. Some say scripting is gone entirely; others say console scripting remains in a restricted form. Do not plan automation around the free edition. If the person only has it, have them run a one-line script in the console first and build on what works.
- **Limits that apply even on Studio:** many API calls return `False` or `None` on failure without raising, so check every return. The API is strong on project, media pool, timeline assembly and render queue, and weak on edit-page operations such as trims, keyframes and transitions; Fairlight mixing and OFX parameters are largely closed. Methods such as `AddTransition()` or `SetEffect()` do not exist: do not write them.
- Back up project libraries before a major-version upgrade.

**FFmpeg and Python.** The zero-cost finishing path: concatenation, loudness normalisation, caption burn-in, format conversion, and every measurement the scripts in this skill make.

## 4. Generative video and audio: the three-layer pattern

Separate art direction from motion generation. Prompt-only video generation without locked frames turns into a retry spiral; a good target is 80% or more usable takes on the first pass.

**Layer 1: static anchors.** Lock composition, character or prop design, palette and lighting as still reference frames. Approve these before generating a second of video.

**Layer 2: motion.** Generate short clips from the anchors. Choose a model by the job, not by the leaderboard:

| Need | Look for |
|---|---|
| Broadcast realism, weather, wide exteriors, native audio | A top-tier closed model with 4K and synced audio |
| Continuity across shots from many reference images | A multimodal-reference model that accepts several images, clips and audio files |
| Precise camera moves and compositing edits | A model with explicit camera or motion-brush control, or a 3D blockout as motion reference |
| Confidential or NDA material that cannot leave your machines | An open-weight model run locally; budget for slow renders on consumer GPUs |
| Lip-synced talking heads | Avoid if you can; off-screen narration removes the failure mode |

Snapshot, November 2026 (expect this to be stale): Google Veo 3.1, ByteDance Seedance 2.0 and 2.5, Kuaishou Kling 3.0, Runway Gen-4.5, MiniMax H3, Gemini Omni Flash and Alibaba's open-weight Wan family were the commonly compared options. **OpenAI Sora is discontinued**: the shutdown was announced on 24 March 2026 and the API was reported to end on 24 September 2026. Do not plan on it. Look up the current line-up, clip lengths and per-second prices before quoting any of them.

**Layer 3: voice, music and finishing.** A human voice actor, or a licensed, original (non-cloned) synthetic voice. Licensed music and SFX. Finish, duck and master in a DAW, an editor or FFmpeg.

**Risk controls that belong in any generative plan**
- *Mechanical accuracy and drift:* do not let a diffusion model invent interlocking mechanisms, readable text or consistent faces. Render mechanisms in 3D or code, and keep human presence to hands, silhouettes and reflections, trimmed to the cleanest 2-3 seconds.
- *Lip-sync failure:* designed out with off-screen narration.
- *Budget and retries:* approve stills and a timed animatic before any per-second API. Put a spend ceiling in the gate.
- *Disclosure:* photoreal generated shots need platform labels; keep the provenance metadata the tools embed.
- *Likeness and IP:* verify permissions for any reference image of a person, character or brand.

## 5. What needs which licence

| Component | Status | Needs |
|---|---|---|
| Scripts, briefs, specs, AV scripts, this skill's validators | Usable immediately | Python 3.9+ for the scripts |
| `audit_media.py`, `extract_contact_sheet.py`, `screen_flashes.py` | Usable immediately | `ffmpeg` and `ffprobe` on PATH |
| Remotion compositions | Scaffold with the CLI | Node.js; free for up to 3 people, paid above |
| Blender headless renders | Script with `bpy` | Free Blender build |
| DaVinci Resolve automation | Adapter code only | Resolve **Studio** for Python, external scripting and MCP |
| After Effects automation | ExtendScript today, UXP on beta | Creative Cloud |
| Generative video and synthetic voice | Prompts and storyboards only | Paid per-second or per-character credits; approval before spending |
