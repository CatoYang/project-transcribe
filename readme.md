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

My current resources
| Input Source                  | Sampling Rate | Format |
|------------------------------|----------------|--------|
| Blue Yeti and OBS            | 48 kHz         | WAV    |
| iPhone Recording (Recorder App) | 16 kHz      | MP3    |
| Dongle Recorder              | 16 kHz         | WAV    |


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

For Future scaling, as other subtle communication features are not captured and are within the 8Khz to 20 KHz region. I will be keep data collection at 48KHz

# Transcription (ASR/TTS) Model Analysis
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

# How Diarization works
Current understanding of how things work
VAD = Voice Activity Detection
The models first identifies whether segnents of audio contains human speech
Speaker embedding model then labels (embeds) the segments
A model then classifies and assign speaker labels by grouping similar embeddings

Audio →
  VAD →
    Speech segments →
      Speaker Embedding Model →
        Embedding vectors →
          Clustering →
            Speaker Labels

# Diarization Model Analysis 
Chatgpt summary
| Tool / Library          | VAD Component           | Speaker Embedding Model        | Clustering / Classification Method  | Notes                                     |
| ----------------------- | ----------------------- | ------------------------------ | ----------------------------------- | ----------------------------------------- |
| **PyAnnote-Audio**      | Learned (neural VAD)    | Pretrained x-vector / ECAPA    | Agglomerative / ~~Bayesian~~            | Modular pipeline, high accuracy           |
| **WhisperX + PyAnnote** | Whisper (approx. VAD)   | pyannote / resemblyzer         | Agglomerative                       | Word-level alignment + speaker labels     |
| **Resemblyzer**         | External or manual      | LSTM-based speaker encoder     | KMeans / Agglomerative              | Lightweight, embedding-only               |
| **UIS-RNN**             | External (e.g., WebRTC) | d-vector (Google)              | RNN-based sequence clustering       | Needs training on speaker transitions     |
| **NVIDIA NeMo**         | Neural VAD              | ECAPA-TDNN                     | Spectral clustering                 | Fast with GPU acceleration                |
| **SpeechBrain**         | Learned VAD (optional)  | ECAPA-TDNN                     | Agglomerative / spectral clustering | Research-focused, flexible                |
| **Google Cloud**        | Proprietary             | Unknown (likely x-vector-like) | Proprietary                         | API-based, minimal control                |
| **AWS Transcribe**      | Proprietary             | Unknown                        | Proprietary                         | Supports diarization in transcripts       |
| **Azure Speech**        | Proprietary             | Unknown                        | Proprietary                         | Supports speaker separation               |
| **Picovoice Leopard**   | Threshold-based VAD     | N/A (not true diarization)     | N/A                                 | Not diarization; more of a command system |
| **Whisper Only**        | N/A                     | N/A                            | N/A                                 | No diarization built-in                   |

Clustering / Classification Methods
| Method                   | Learns Over Time? | Needs #Speakers? | Strengths                                 |
| ------------------------ | ----------------- | ---------------- | ----------------------------------------- |
| Agglomerative Clustering | ❌ No              | ❌ Not always     | Simple, interpretable                     |
| Bayesian Clustering      | ✅ Yes (inference) | ❌ No             | Probabilistic, uncertainty-aware          |
| RNN-based Clustering     | ✅ Yes             | ❌/✅ Depends      | Models sequences and speaker transitions  |
| Spectral Clustering      | ❌ No              | ✅ Yes            | Good for complex cluster shapes, accurate |

For accuracy i will be using Pyannote-audio, however it does not inately have bayesian clustering so i will add a new step to the pipeline with VBx Diarization. I will be considering RNN-based clustering once i get more experienced and the time to work on labeling my data.


Originally i was using Whisper and pyannote for my transcriptions but development of the models has been progressing quick and i have considered it deprecated. WhisperX is a well optimised fork of whisper but i do not know how long it will be maintained and i risk over-relying on the repo for pipeline. It uses pyannote for speaker embedding anyway so i might as well use pyannote







# Pipeline
- 