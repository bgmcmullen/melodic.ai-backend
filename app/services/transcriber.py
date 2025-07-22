import crepe
import librosa
import io
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

def transcribe_pitch(audio_bytes, step_size=20):
  y, sr = sf.read(io.BytesIO(audio_bytes), dtype='float32')

  # Convert to Mono and resample to 16kHz
  if y.ndim > 1:
      y = y.mean(axis=1)
  if sr != 16000:
      y = librosa.resample(y, orig_sr=sr, target_sr=16000)
      sr = 16000

  time, freq, confidence, _ = crepe.predict(y, sr, viterbi=True, step_size=step_size)


  # Convert to notes
  notes = []

  for f, c in zip(freq, confidence):
    print(f, c)
    if c < 0.5:
      notes.append(0)
    else:
      notes.append(hz_to_note(f))

  fig, ax1 = plt.subplots()
 
  # Plot the pitch track
  ax1.plot(time, notes, color='b', label='Smoothed Pitch')
  ax1.set_xlabel("Time (s)")
  ax1.set_ylabel("Frequency (Hz)", color='b')
  ax1.tick_params(axis='y', labelcolor='b')

  # Create a second y-axis for confidence
  ax2 = ax1.twinx()
  ax2.plot(time, confidence, color='r', alpha=0.6, label='confidence')
  ax2.set_ylabel("confidence", color='r')
  ax2.tick_params(axis='y', labelcolor='r')


  plt.title("CREPE Pitch Track with Confidence Overlay")
  fig.tight_layout()
  plt.show()

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
  octave = rounded_midi // 12 - 1
  return midi
  return f"{note_letter_name} {octave} {cent_deviation}"

filepath = "VocalSet11/FULL/female1/arpeggios/straight/f1_arpeggios_straight_a.wav"

with open(filepath, "rb") as f:
   audio_bytes = f.read()

notes = transcribe_pitch(audio_bytes)

print(notes)

