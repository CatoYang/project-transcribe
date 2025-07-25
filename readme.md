## Project objectives
I run tabletop RPGs and typically want a tool to summarise sessions.

A issues arose then typical tools available to me do not transcribe/diarize and summarize effectively. (initially)
- transcription accuracy being poor due to the fact training is done globally but the speech recorded is uniquely singaporean.
- unique words are being spoken at the table such as names, places and characters and are not identified by a transcriber
- Sessions are several hours long and need to be broken down preprocessing and restitched back after
- Background noise of other tables bleeding into the recorded audio

In this project i wish to solve these problems.

# Research and Understanding the Tools
I have been collecting various data for analysis and experimenting with various hardware. 
They are typically not the same and needs tuning to match the models used. The below is my original inputs without changing any settings

Inputs                                          Sampling        Codecs
- Blue yeti and OBS                             48 KHz          wav
- Iphone recording (recorder app)               16 kHz          mp3
- Dongle Recorder                               16 kHz          wav

Inputs of various models
| Model          | Sample Rate | Channels | Format    | Notes                                 |
| -------------- | ----------- | -------- | --------- | ------------------------------------- |
| Whisper        | 16 kHz      | Mono     | WAV, FLAC | Internally resampled to 16kHz/log-Mel |
| wav2vec2       | 16 kHz      | Mono     | WAV       | Raw waveform                          |
| HuBERT         | 16 kHz      | Mono     | WAV       | Raw waveform                          |
| Silero VAD     | 16 kHz      | Mono     | WAV/numpy | Float32 or PCM                        |
| pyannote-audio | 16 kHz      | Mono     | WAV       | Required 16kHz mono                   |
| ESPnet         | 16 kHz      | Mono     | WAV       | Can vary by model                     |
| DeepSpeech     | 16 kHz      | Mono     | WAV       | Strict 16kHz only                     |
| Kaldi          | 8k/16k Hz   | Mono     | WAV/raw   | Varies with config                    |

For audio recordings with OBS since we are sampling at 3 times the frequency i have a option to record at 16 KHz so i do not have to do any resampling prior to input to whisper
Or record them in 48KHz and resample using FFmpeg's SoX resampling using the flags
	soxr_quality=quick
    soxr_quality=medium
    soxr_quality=high
    soxr_quality=veryhigh
Since i do not know how OBS resamples their data and its not a hardware constraint at this point (on my laptop) i can record at 48 KHz and resample.

The other inputs need not much preprocessing and the quality of data to input into models seems to be standardised at 16k Hz since human speech exists in the 300 to 8000 Hz range
By Nyquist’s Theorem, to capture frequencies up to 8 kHz without aliasing, we need a minimum sample rate of 16 kHz.
So 16 kHz can fully capture intelligible speech (voice, tone, most consonants and vowels) without much perceptual loss.

# Transcription Model Analysis

Direct Modeling of raw waveform
raw waveform → neural net → ASR (automatic speech recognition)

Classical pipeline with MFCCs (mel-frequency cepstral coefficients)
raw waveform → MFCC → traditional ASR

Spectrogram-based
raw waveform → spectrogram → ASR / TTS (Text to speech)

Mel-Spectrogram (perceptual scaling)
raw waveform → spectrogram → mel-spectrogram → ASR (Whisper)

Speaker Embedding pipeline (for diarization)
raw waveform → mel-spectrogram → log-mel → embedding model → speaker segments

# Diarization Model Analysis 


# Pipeline
- 