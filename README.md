# Active Silence in Beethoven

This repository contains the materials behind **"Active Silence in Beethoven: Pause Strategies in the Grave of the Pathetique,"** a late-breaking demo paper prepared for **ISMIR LBD 2026**. It includes the analysis code, extracted timing tables, figures, and the source manifest for the study set verified on July 21, 2026.

The CSV files in `data/` are the verified outputs used in the current draft. If you rerun the detector on newly downloaded audio, or under a different `ffmpeg` build, a few pause boundaries may land slightly differently.

## What Is Not Here

No audio files are included. The WAVs linked through ATEPP are copyrighted commercial recordings, so this repository only includes code, extracted features, figures, and provenance metadata. If you want to rebuild the results, use `data/manifest.csv` together with the documented ATEPP and YouTube links, then place the audio in your own local directory.

## Reproduce In Three Commands

Before running anything, install `ffmpeg` and put the local audio files in one directory. The scripts look for filenames such as `AB.wav`, `DB.wav`, or the pianist name, across `wav`, `mp3`, `flac`, `m4a`, and `aiff`.

```bash
python3 -m pip install -r requirements.txt
export AS_AUDIO_DIR="/absolute/path/to/local/audio"
python3 code/01_detect.py --audio-dir "$AS_AUDIO_DIR" && python3 code/02_normalize_rerun.py --audio-dir "$AS_AUDIO_DIR" && python3 code/03_analysis.py && python3 code/04_figures.py
```

## Data Dictionary: `data/events.csv`

- `recording_id`: short identifier used throughout the package.
- `pianist`: performer name.
- `pause`: score-localized pause label (`P1`-`P4`).
- `d_s`: sounding duration before the detected low-energy region, in seconds.
- `d_l`: low-energy duration after decay and before the next attack, in seconds.
- `T`: total local pause interval, defined as `d_s + d_l`.
- `condition`: `source` for the source-conditioned baseline run, `peaknorm` for the `-1 dBFS` peak/gain control rerun.
- `threshold_setting`: silence-detector setting used for that row. The shipped event table uses the verified baseline `-35dB_0.10s`.

## Known Limitations

- The boundary detector uses an absolute `dBFS` threshold, so event boundaries remain sensitive to source level and mastering differences.
- The peak-normalized rerun is a simple gain control to `-1 dBFS`, not integrated-loudness normalization; LUFS-based normalization is left to future work.
- `d_s` is not treated as a pure performance variable because it mixes acoustics, transfer, score texture, pedaling, and release behavior.
- The historical Schnabel source is documented in the manifest but excluded from the core event table because ATEPP flags the representative source as background noise.

## How To Cite

Harold Wang, *Active Silence in Beethoven: Pause Strategies in the Grave of the Pathetique*, prepared for submission to ISMIR LBD 2026.

Contact: haroldw101313@wpga.ca
