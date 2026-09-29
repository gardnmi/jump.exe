"""Generate the original, quiet four-note summit cue (no sampled game audio)."""
import math
from pathlib import Path
from .resources import ROOT
import struct
import wave


def generate(path):
    rate=22050
    notes=((0.,523.25),(.18,659.25),(.36,783.99),(.62,1046.5))
    samples=[]
    for n in range(int(2.2*rate)):
        t=n/rate;value=0.
        for start,hz in notes:
            age=t-start
            if age<0:continue
            envelope=min(1,age/.012)*math.exp(-age*3.3)
            value+=envelope*(math.sin(math.tau*hz*age)+.22*math.sin(math.tau*2*hz*age))
        value*=min(1,(2.2-t)/.15)
        samples.append(value)
    peak=max(abs(v) for v in samples)
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as out:
        out.setparams((1,2,rate,0,'NONE','not compressed'))
        out.writeframes(b''.join(struct.pack('<h',round(v/peak*.14*32767)) for v in samples))


if __name__=='__main__':
    generate(ROOT/'assets/sfx/white_pill.wav')
