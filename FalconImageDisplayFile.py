import pyglet
from FalconImageFile import FalconImage
import time

class FalconImageDisplay(pyglet.window.Window):

    def __init__(self,fImage:FalconImage, title:str, animation_callback = None):

        super(FalconImageDisplay,self).__init__(fImage.width,fImage.height,title)
        self.my_falcon_image = fImage
        self.batch = self.build_batch()
        self.needs_save = False
        self.animation_callback = animation_callback

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.animation_callback is not None:
            self.animation_callback(-1)


    def build_batch(self) -> pyglet.graphics.Batch:
        batch = pyglet.graphics.Batch()
        self.spr = pyglet.sprite.Sprite(self.my_falcon_image.my_image_data, x=0, y=0, batch=batch)

        return batch

    def update(self):
        self.batch = self.build_batch()