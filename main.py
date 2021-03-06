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
    global color_attractors
    source_image = FalconImage(filename)
    source_points = sample_N_points_from_falconimage(num_samples, source_image)
    color_attractors = cluster_colors_from_points(source_points)



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

def cluster_colors_from_points(source_points: List[List[Coordinates, Color, int]]) -> List[Color]:
    """
    Uses the K-Means algorithm to clusters all the given points into k colors, picking the optimal colors
    for doing so.
    :param source_points: a list of [coordinates, colors, attractor_nums] - the coordinates are ignored at this point.
    :return: a list of color attractors; the attractor_nums in the source_points parameter are altered to point to these
    """
    attractors = []
    for i in range(k):
        attractors.append((random.randint(0,256), random.randint(0,256), random.randint(0,256)))
    iterations = 0
    while True:
        # REASSIGN ATTRACTORS TO DOTS
        iterations += 1
        made_a_change = False
        for data in source_points:
            data_color = data[1]
            data_attractor = data[2]
            closest_color_dist_squared = 200000
            closest_attractor_num = -1
            for i in range(k):
                attractor_color = attractors[i]
                dist_squared = 0
                for j in range(3):
                    dist_squared += (attractor_color[j]-data_color[j])**2
                if dist_squared < closest_color_dist_squared:
                    closest_color_dist_squared = dist_squared
                    closest_attractor_num = i
            if closest_attractor_num != data_attractor:
                data[2] = closest_attractor_num
                made_a_change = True

        if made_a_change:
            # RECALCULATE MEANS FOR THE ATTRACTORS
            for i in range(k):
                r = 0
                g = 0
                b = 0
                N = 0
                for data in source_points:
                    if data[2] == i:
                        data_color = data[1]
                        r += data_color[0]
                        g += data_color[1]
                        b += data_color[2]
                        N += 1
                if N > 0:
                    attractors[i] = (int(r/N), int(g/N), int(b/N))
                else:
                    attractors[i] = (random.randint(0,256), random.randint(0,256, random.randint(0,256)))

        else:
            break # done with the k Means search process.

        return attractors

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
