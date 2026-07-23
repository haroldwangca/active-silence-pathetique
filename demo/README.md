# Demo Stub

This folder contains a local-only stub for a future "Pause Alignment" demo. It does not include audio, and it should not be uploaded with copyrighted recordings.

To use it locally:

1. Copy `audio_paths.example.json` to `audio_paths.json`.
2. Replace each placeholder with a local file path or local server URL for the matching recording.
3. From the repository root, run `python3 -m http.server 8000`.
4. Open `http://localhost:8000/demo/`.

The stub reads derived metadata from `../data/events.csv` and `../data/manifest.csv`. Audio remains user-supplied and outside version control.

GitHub does not run this HTML directly on the repository page. The demo is local-only unless it is later deployed through GitHub Pages or another static host.
