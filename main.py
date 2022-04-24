import random
from typing import List, Tuple
from FalconImageFile import FalconImage
from FalconImageDisplayFile import FalconImageDisplay

Color = Tuple[int, int, int]
Coordinates = Tuple[int, int]

k = 5
color_attractors: List[Color] = []
filename = "Howe-2021-reduced.jpg"
num_samples = 1000


def main():
    source_image = FalconImage(filename)
    source_points = sample_N_points_from_falconimage(num_samples, source_image)



def sample_N_points_from_falconimage(N: int, img: FalconImage) -> List[List[Coordinates, Color, int]]:
    """
    selects N points on the screen (potentially with duplicates) and generates a list of the points' coordinates,
    colors, and randomized attractor_numbers for a k-means search, to be performed later.
    :param N: the number of points to sample
    :param img: the FalconImage from which we are recording the colors
    :return: a list of (coordinate, color, attractor_num) Lists.
    """
    results = []
    for i in range(N):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        color = img.get_RGB_at(x,y)
        attractor = random.randint(0,k)
        results.append([(x,y),color,attractor])
    return results

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
