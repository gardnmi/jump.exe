#!/usr/bin/python
"""Original synthesized jump/impact sounds; deterministic, no sampled recordings."""
import math
from pathlib import Path
import random
import struct
import wave


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    for name, duration in (('jump', .16), ('land', .13), ('heavy_land', .28)):
        randomizer = random.Random(name)
        samples, phase, noise = [], 0., 0.
        for i in range(round(24000*duration)):
            t = i/24000
            u = t/duration
            noise = .62*noise + .38*randomizer.uniform(-1, 1)
            if name == 'jump':
                phase += (230+610*u*u)/24000
                tone = math.sin(phase*math.tau)+.16*math.sin(phase*math.tau*3)
                value = .36*math.sin(math.pi*u)**1.5*(.82*tone+.18*noise)
            else:
                heavy = name == 'heavy_land'
                phase += ((98 if heavy else 165)*math.exp(-7*t)+35)/24000
                envelope = min(1, t/.002)*math.exp(-u*7)*(1-u)
                value = (.65 if heavy else .48)*envelope*(.7*math.sin(phase*math.tau)+.3*noise)
                if heavy and .085<t<.14:
                    value += .07*math.sin(math.pi*(t-.085)/.055)*noise
            samples.append(struct.pack('<h', round(max(-1, min(1, value))*32767)))
        with wave.open(str(directory/(name+'.wav')), 'wb') as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(24000)
            out.writeframes(b''.join(samples))


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1]/'assets/sfx')
