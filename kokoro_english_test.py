from kokoro import KPipeline
import soundfile as sf

print("Loading Kokoro English model...")

pipeline = KPipeline(lang_code="a")

text = "Hi Sat-yum, I'm Aria. It's really nice to talk to you. How are you doing today?"

print("Generating English voice...")

generator = pipeline(
    text,
    voice="af_heart"
)

for i, (gs, ps, audio) in enumerate(generator):
    filename = f"kokoro_english_{i}.wav"
    sf.write(filename, audio, 24000)
    print(f"Saved: {filename}")

print("Done!")