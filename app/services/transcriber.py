import crepe
import librosa
import io
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, uniform_filter1d


def transcribe_pitch(audio_bytes, step_size=10):
  y, sr = sf.read(io.BytesIO(audio_bytes), dtype='float32')

  # Convert to Mono and resample to 16kHz
  if y.ndim > 1:
      y = y.mean(axis=1)
  if sr != 16000:
      y = librosa.resample(y, orig_sr=sr, target_sr=16000)
      sr = 16000

  time, freq, confidence, _ = crepe.predict(y, sr, viterbi=True, step_size=step_size)

  conf_thresh = 0.8
  indices = np.where(confidence >= conf_thresh)[0]

  if len(indices) > 0:
    start = indices[0]
    end = indices[-1]
  else:
    start = end = None

  freq = freq[start:end]

  time = time[start:end]

  smoothed_freq = median_filter(freq, size=100)

  # Convert to notes
  notes = []

  prev_letter = None

  # group note by letter name
  for f, t in zip(smoothed_freq, time):
    current_note, deviation = hz_to_note(f)
    if current_note != prev_letter:
       prev_letter = current_note
       notes.append({"note_name": current_note, "deviations": [deviation], "time": [t]})
    else:
      notes[-1]["deviations"].append(deviation)
      notes[-1]["time"].append(t)

  # average frequency and remove extremely short pitches
  avg_notes = []

  for note in notes:
     length = len(note["deviations"])
     if length < 10:
        continue
     start_time = note["time"][0]
     end_time = note["time"][-1] + .05
     avg_deviation = round(sum(note["deviations"]) / length, -1)
     avg_notes.append({"note_name": note["note_name"], "avg_deviation": avg_deviation, "start": start_time, "end": end_time})

  fig, ax1 = plt.subplots()
 
  # Plot the pitch track
  # ax1.plot(time, smoothed_freq, color='b', label='Smoothed Pitch1')
  # ax1.set_xlabel("Time (s)")
  # ax1.set_ylabel("Frequency (Hz)", color='b')
  # ax1.tick_params(axis='y', labelcolor='b')


  # plt.title("CREPE Pitch Track with Confidence Overlay")
  # fig.tight_layout()
  # plt.show()

  for note in notes:
   print(note)

  return avg_notes

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
  # return midi
  return (f"{note_letter_name}{octave}", cent_deviation)

filepath = "VocalSet11/FULL/male6/arpeggios/belt/m6_arpeggios_belt_a.wav"

with open(filepath, "rb") as f:
   audio_bytes = f.read()

notes = transcribe_pitch(audio_bytes)

for note in notes:
   print(note)

