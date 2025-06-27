import crepe
import librosa
import io
import numpy as np
import soundfile as sf

def transcribe_pitch(audio_bytes, n=1, step_size=50):
  y, sr = sf.read(io.BytesIO(audio_bytes), dtype='float32')

  # 🔒 Mono and resample to 16kHz
  if y.ndim > 1:
      y = y.mean(axis=1)
  if sr != 16000:
      y = librosa.resample(y, orig_sr=sr, target_sr=16000)
      sr = 16000


  time, freq, confidence, _ = crepe.predict(y, sr, viterbi=True, step_size=step_size)

  # trim array to a number divisible by n

  length = len(freq) - (len(freq) % n)
  freq_timmed = freq[:length] 

  # Convert to notes
  notes = []

  # Average every n frequencies
  freq_averaged = np.mean(freq_timmed.reshape(-1, n), axis=1)

  for f in freq_averaged:
    notes.append(hz_to_note(f))

  return notes

def hz_to_note(freq):
  A4 = 440.0
  if freq == 0:
    return "Rest"
  
  note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
  midi = 69 + 12 * np.log2(freq / A4)
  rounded_midi = int(round(midi))

  cent_deviation = (midi - rounded_midi) * 100
  note_letter_name = note_names[rounded_midi % 12]
  octave = midi // 12 - 1
  return f"{note_letter_name} {octave} {cent_deviation}"