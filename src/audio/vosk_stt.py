import vosk
import pyaudio
import queue
import json
import os
import time

class VoskSTT:
    def __init__(self, model_path, sample_rate=16000, chunk_size=8192):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}. Please download it from https://alphacephei.com/vosk/models")

        self.model = vosk.Model(model_path)
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.running = False

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.audio_callback
        )

    def audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self, process_callback):
        self.running = True
        self.stream.start_stream()
        print("\nListening for audio to transcribe... (Press Ctrl+C in console to stop server)")
        print("-" * 50)

        recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
        recognizer.SetWords(True)

        sentence_buffer = []
        last_recognition_time = time.time()

        while self.running:
            try:
                data = self.audio_queue.get(timeout=0.1)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        sentence_buffer.append(text)
                        full_sentence = " ".join(sentence_buffer)
                        process_callback(full_sentence)
                        sentence_buffer = []
                        last_recognition_time = time.time()
                else:
                    partial_result = json.loads(recognizer.PartialResult())
                    partial_text = partial_result.get('partial', '')
                    if partial_text:
                        last_recognition_time = time.time()

                # Check for end of speech (e.g., 2 seconds of silence)
                if sentence_buffer and (time.time() - last_recognition_time > 2.0):
                    full_sentence = " ".join(sentence_buffer)
                    process_callback(full_sentence)
                    sentence_buffer = []


            except queue.Empty:
                if sentence_buffer and (time.time() - last_recognition_time > 2.0):
                    full_sentence = " ".join(sentence_buffer)
                    process_callback(full_sentence)
                    sentence_buffer = []
                continue
            except Exception as e:
                print(f"\nError processing audio: {e}")

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
