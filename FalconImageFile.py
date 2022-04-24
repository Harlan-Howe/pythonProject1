
import pyglet
from typing import Tuple, List

encoding = "UTF-8"

class FalconImage:

    def __init__(self, filename, width=None, height=None):
        if filename is not None:
            self.my_image = pyglet.image.load(filename)
            self.my_image_data = self.my_image.get_image_data()
            self.width = self.my_image.width
            self.height = self.my_image.height
        else:
            zeroes = [0 for i in range(width*height*3)]
            self.my_image_data = pyglet.image.ImageData(width, height, "RGB", bytes(zeroes), width*3 )
            self.width = width
            self.height = height

        self.my_data = []
        self.my_data.extend(self.my_image_data.get_data('RGB', self.width * 3))


    def remove_pure_black(self):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                rgb = self.get_RGB_at(x,y)
                if rgb[0] == rgb[1] == rgb[2] == 0:
                    self.set_RGB_at((1, 1, 1), x, y)
                    count += 1
        # print(f"{count=}")

    def get_RGB_at(self, x: int, y: int) -> Tuple[int, int, int]:
        start = (self.width*y+x)*3
        return (self.my_data[start],self.my_data[start+1],self.my_data[start+2])

    def set_RGB_at(self, color:Tuple[int,int,int], x:int, y:int) -> None:
        """
        sets the color of a single pixel, but does not update the image_data for this image - you'll need to call
        self.refresh() for that. This is because that step is slow - it updates all the pixels, and you may wish
        to set color for several pixels first and then do a refresh.
        :param color:
        :param x:
        :param y:
        :return:
        """
        start = (self.width*y+x)*3
        for i in range(3):
            self.my_data[start+i] = color[i]

    def get_RGB_region(self, rect:Tuple[int, int, int, int])->List[List[Tuple[int,int,int]]]:
        result = []
        for row in range(rect[3]):
            row_of_RGB = []
            for col in range(rect[2]):
                row_of_RGB.append(self.get_RGB_at(rect[0]+col, rect[1]+row))
            result.append(row_of_RGB)
        return result

    def set_RGB_region_at_rect(self, colors:List[List[Tuple[int,int,int]]], rect: Tuple[int,int,int,int])->None:
        """
        blits the given set of colors to self.my_data at the given rect. Note: does not change the image; you'll need
        to call self.refresh to make that happen.

        :param colors: a grid of (R,G,B) values, 0-255
        :param rect: Must be the same dimensions as colors (x, y, w, h)
        :return:
        """
        assert rect[3] == len(colors) and rect[2] == len(colors[0]), f"Mismatch.... {rect=}\t{len(colors)=}\t{len(colors[0])=}"
        for row in range(rect[3]):
            for col in range(rect[2]):
                self.set_RGB_at(colors[row][col],rect[0]+col, rect[1]+row)


    def refresh(self)->None:

        self.my_image_data = pyglet.image.ImageData(self.width, self.height, 'RGB',bytes(self.my_data),self.width*3)
