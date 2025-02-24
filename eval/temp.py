from eval_dataset import Audio
from speechmos import dnsmos


gen_audio = Audio('84_121123_000008_000003.wav')

mos = dnsmos.run(gen_audio.normalize(), 16000)

print(mos)