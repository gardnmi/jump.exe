import unittest
import cairo
from jump_exe.art import tile
from jump_exe.character import FRAMES,frame
from jump_exe.course import ROOMS
from jump_exe.life import DesktopLife


class PixelRenderingTests(unittest.TestCase):
    def test_complete_scenes_scale_on_one_pixel_grid(self):
        # Includes text, character/NPC, animated hardware, props and glow. A draw
        # accidentally moved after the upscale would introduce unmatched pixels.
        for rank in range(len(ROOMS)):
            w,h=ROOMS[rank].rect[2:]
            events=DesktopLife().room(rank)
            for event in events:event.update(active=True,age=.75,perched=False)
            results=[]
            for scale in (1,3):
                surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w*scale,h*scale)
                tile(cairo.Context(surface),w*scale,h*scale,rank,rank//3,2.25,events=events)
                surface.flush()
                results.append(bytes(surface.get_data()))
            native,scaled=results
            rows=[]
            for y in range(h):
                row=native[y*w*4:(y+1)*w*4]
                rows.append(b''.join(row[x*4:x*4+4]*3 for x in range(w))*3)
            self.assertEqual(scaled,b''.join(rows),f'Room {rank} has mixed pixel scales')

    def test_every_animation_pose_fits_its_transparent_canvas(self):
        for name in FRAMES:
            sprite=frame(name)
            data=bytes(sprite.get_data())
            alpha=data[3::4]
            self.assertGreater(sum(a>128 for a in alpha),100,name)
            self.assertFalse(any(alpha[:40]),name)
            self.assertFalse(any(alpha[-40:]),name)
            self.assertFalse(any(alpha[::40]),name)
            self.assertFalse(any(alpha[39::40]),name)


if __name__=='__main__':
    unittest.main()
