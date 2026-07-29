# Active Silence Viewer

This folder contains the public viewer for the extracted pause events. It includes one author-owned Grave recording for playback; the professional source recordings remain external because they are copyrighted.

The viewer is meant to make one event inspectable quickly: choose a recording and pause, then inspect the derived `d_s`/`d_l` values, recovered detector boundaries, a compact boundary timeline, the corpus trajectory figure, a waveform-check panel for the current selection, the selected threshold-summary row, and playback when an allowed audio path is available. The page opens on `HW_GRAVE_DEMO`, the author-owned recording, so the hosted demo immediately shows a waveform panel, boundary overlay, MIDI/audio release check, and playable audio.

To use copyrighted professional recordings locally:

1. Copy `audio_paths.example.json` to `audio_paths.json`.
2. Replace each placeholder with a local file path or local server URL for the matching recording.
3. From the repository root, run `python3 -m http.server 8000`.
4. Open `http://localhost:8000/demo/`.

The viewer reads corpus metadata from `../data/events.csv` and `../data/pause_boundaries_source.csv`, demo metadata from `../data/demo_recording_events.csv` and `../data/demo_recording_boundaries.csv`, MIDI/audio comparison rows from `../data/demo_recording_midi_release.csv`, aggregate detector-sensitivity metadata from `../data/threshold_sweep.csv`, and images from `../figures/`. The demo-recording manifest declares a measured audio-minus-MIDI offset of `4.358 s`; MIDI release times are aligned by that offset before comparison with audio threshold crossings. The browser audio element is pointed to the selected event span using a media-fragment URL.

The public version is served through GitHub Pages. Professional recording playback should remain local-only; do not commit commercial audio or local path mappings.
