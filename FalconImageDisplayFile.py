import pyglet
from FalconImageFile import FalconImage
import time

class FalconImageDisplay(pyglet.window.Window):

    def __init__(self,fImage:FalconImage, title:str, animation_callback = None, save_callback = None):

        super(FalconImageDisplay,self).__init__(fImage.width,fImage.height,title)
        self.my_falcon_image = fImage
        self.batch = self.build_batch()
        self.needs_save = False
        self.animation_callback = animation_callback
        self.save_callback = save_callback

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT :
            if (modifiers & pyglet.window.key.MOD_SHIFT)
                if self.save_callback is not None:
                    self.save_callback()
            else:
                if self.animation_callback is not None:
                    self.animation_callback(-1)
        if button == pyglet.window.mouse.RIGHT and self.save_callback is not None:
            self.save_callback()

    def build_batch(self) -> pyglet.graphics.Batch:
        batch = pyglet.graphics.Batch()
        self.spr = pyglet.sprite.Sprite(self.my_falcon_image.my_image_data, x=0, y=0, batch=batch)

        return batch

    def update(self):
        self.batch = self.build_batch()