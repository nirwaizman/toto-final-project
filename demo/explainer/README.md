# Explainer video — build notes

`../toto-explainer-2min-he-subs.mp4` — 2:00, 1280×720, English narration (Higgsfield Seed Audio, voice "Cillian"),
Hebrew subtitles, style preset "Editorial Motion Graphics", mascot **Toto**.

Pipeline (Higgsfield CLI): 12 blocks × 10 s → `seed_audio` voice takes (`voices/jobs.json`) →
`gemini_omni` clips with the preset style key attached (`clips/jobs.json`) → local ffmpeg
assembly (`assemble.sh`: voice centered per block, pitch-safe atempo ≤ 1.11 for takes over 9.6 s,
ambient clip audio ducked to 25 %) → Hebrew SRT (`subs_he.py`) burned as PNG overlays (`burn_subs.py`,
this ffmpeg has no libass).

Files: `narration.txt` (script), `prompts.py`/`prompts.json` (clip prompts), `subs_he.srt`.
Media (mp3/mp4 intermediates) are git-ignored; job ids/URLs are in the json files.
