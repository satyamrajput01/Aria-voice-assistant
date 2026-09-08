from kokoro import KPipeline
import soundfile as sf

print("Loading Kokoro Hindi model...")

pipeline = KPipeline(lang_code="h")

text = "नमस्ते सत्यम, कैसे हो? मैं आरिया हूँ। आज हम अपना डेस्कटॉप असिस्टेंट बना रहे हैं।"

print("Generating voice...")

generator = pipeline(
    text,
    voice="hf_alpha"
)

for i, (gs, ps, audio) in enumerate(generator):
    filename = f"kokoro_hindi_{i}.wav"
    sf.write(filename, audio, 24000)
    print(f"Saved: {filename}")

print("Done!")