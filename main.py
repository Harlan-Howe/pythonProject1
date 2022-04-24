import random
from typing import List, Tuple
from FalconImageFile import FalconImage
from FalconImageDisplayFile import FalconImageDisplay
import pyglet

Color = Tuple[int, int, int]
Coordinates = Tuple[int, int]

k = 10
color_attractors: List[Color] = []
filename = "Howe-2021-reduced.jpg"
num_samples = 2000


def main():
    global color_attractors
    source_image = FalconImage(filename)
    source_points = sample_N_points_from_falconimage(num_samples, source_image)
    color_attractors = cluster_colors_from_points(source_points)
    display_source_points_and_attractors(source_points, source_image.width, source_image.height)

    training_inputs, training_outputs = generate_data_for_model_from_samples(source_points)
    # pyglet.clock.schedule_interval(perform_animation_step, 0.001)

    pyglet.app.run()

def sample_N_points_from_falconimage(N: int, img: FalconImage) -> List[List]:
    """
    selects N points on the screen (potentially with duplicates) and generates a list of the points' coordinates,
    colors, and randomized attractor_numbers for a k-means search, to be performed later.
    :param N: the number of points to sample
    :param img: the FalconImage from which we are recording the colors
    :return: a list of (coordinate, color, attractor_num) Lists.
    """
    results = []
    for i in range(N):
        x = random.randint(0, img.width-1)
        y = random.randint(0, img.height-1)
        color = img.get_RGB_at(x,y)
        attractor = random.randint(0,k-1)
        results.append([(x,y),color,attractor])
    return results

def cluster_colors_from_points(source_points: List[List]) -> List[Color]:
    """
    Uses the K-Means algorithm to clusters all the given points into k colors, picking the optimal colors
    for doing so.
    :param source_points: a list of [coordinates, colors, attractor_nums] - the coordinates are ignored at this point.
    :return: a list of color attractors; the attractor_nums in the source_points parameter are altered to point to these
    """
    attractors = []
    for i in range(k):
        attractors.append((random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    iterations = 0
    while True:
        # REASSIGN ATTRACTORS TO DOTS
        iterations += 1
        print(f"K-Means: iteration {iterations}")
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
                    attractors[i] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

        else:
            break # done with the k Means search process.

    return attractors

def display_source_points_and_attractors(points: List[List],
                                         source_width: int,
                                         source_height: int) -> FalconImageDisplay:
    """
    creates a new FalconImage window that shows the sample dots (in reduced colors) and a row of the k attractor colors.
    :param points: A list of [Coordinates, Color, attractor_num] that we wish to plot. (The color is ignored; instead,
                    we use the color associated with the attractor_num.)
    :param source_width: The width of the window to create.
    :param source_height: The window will have this height, plus 20
    :return: a FalconImageDisplay with the image we are creating.
    """
    sample_image = FalconImage(None, width= source_width, height = source_height+20)
    for p in points:
        sample_image.set_RGB_at(color=color_attractors[p[2]], x=p[0][0], y=p[0][1])
    box_width = int(source_width / k)
    for i in range(k):
        sample_image.set_RGB_region_at_rect([[color_attractors[i] for k in range(box_width)] for j in range(20)],
                                            (box_width*i, source_height, box_width, 20))
    sample_image.refresh()
    display = FalconImageDisplay(sample_image,"Sampling")
    display.update()
    return display

def generate_data_for_model_from_samples(points: List[List]) -> Tuple[List[Coordinates], List[List[int]]]:
    """
    converts the data that we've sampled from the source image into two lists that are in a format readable by
    the ANN: a list of the (x, y) coordinates, and a list of one-hot readings for the attractor_nums. The one-hot
    is a list of k numbers, all of which are zero, except one that is 1. Which value gets the 1 corresponds to
    the attractor_num.
    For instance, if k = 6 and attractor_num is 3, then the one_hot would be [0, 0, 0, 1, 0, 0].
                  if k = 8 and attractor_num is 0, then the one_hot would be [1, 0, 0, 0, 0, 0, 0, 0].
    :param points: a list of [coordinates, color, attractor_num] (the color is ignored.)
    :return: a list of coordinates and a list of one-hots. Both lists should have the same number of items, the number
                of [coordinate, color, attractor_num] data points as the given list.
    """
    inputs = []
    outputs = []
    for coords, color, att_num in points:
        inputs.append(coords)
        one_hot = [0] * k
        one_hot[att_num] = 1
        outputs.append(one_hot)
    return inputs, outputs

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
