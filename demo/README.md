# Local Demo Viewer

This folder contains a local-only viewer for the extracted pause events. It does not include audio, and it should not be uploaded with copyrighted recordings.

The viewer is meant to make one event inspectable quickly: choose a recording and pause, then inspect the derived `d_s`/`d_l` values, recovered detector boundaries, a compact boundary timeline, the corpus trajectory figure, a waveform-check panel for the current selection, the selected threshold-summary row, and optional playback if you have mapped the corresponding local audio file. Copyright restrictions keep the source recordings outside the hosted artifact.

To use it locally:

1. Copy `audio_paths.example.json` to `audio_paths.json`.
2. Replace each placeholder with a local file path or local server URL for the matching recording.
3. From the repository root, run `python3 -m http.server 8000`.
4. Open `http://localhost:8000/demo/`.

The viewer reads derived metadata from `../data/events.csv`, detector-boundary metadata from `../data/pause_boundaries_source.csv`, aggregate detector-sensitivity metadata from `../data/threshold_sweep.csv`, and images from `../figures/`. Audio remains user-supplied and outside version control. If `audio_paths.json` is configured, the browser audio element is pointed to the selected event span using a media-fragment URL.

GitHub does not run this HTML directly on the repository page. The demo is local-only unless it is later deployed through GitHub Pages or another static host.
