print("Importing standard libraries")
import random
from typing import List, Tuple
from FalconImageFile import FalconImage
from FalconImageDisplayFile import FalconImageDisplay
import pyglet
import datetime, time
start = datetime.datetime.now()
print("Importing Tensorflow.")
import tensorflow as tf
from tensorflow.keras import layers
print("Done importing.")
end = datetime.datetime.now()
print(f"Time to import: {end-start}.")

# flowers.png --> https://www.healthline.com/nutrition/edible-flowers



Color = Tuple[int, int, int]
Coordinates = Tuple[int, int]

k = 6
color_attractors: List[Color] = []
image_filename = "source_images/flowers.png"
num_samples = 3000
model: tf.keras.Model = None
destination_image: FalconImage = None
destination_window: FalconImageDisplay = None
num_points_per_update = 10000
total_epochs_so_far = 0
epochs_per_animation_step = 50

def main():
    global color_attractors, model, destination_image, destination_window, training_inputs, training_outputs
    source_image = FalconImage(f"source_images/{image_filename}")
    mode, data_filename = get_mode_and_filename()

    source_points = sample_N_points_from_falconimage(num_samples, source_image)
    color_attractors = cluster_colors_from_points(source_points)
    generate_reduced_color_image(color_attractors, source_image)
    source_window = display_source_points_and_attractors(source_points, source_image.width, source_image.height)
    source_window.set_location(source_image.width,0)
    print("Setting up ANN.")
    training_inputs, training_outputs = generate_data_for_model_from_samples(source_points)

    model = create_ANN_model()

    #temp....
    destination_image = FalconImage(None, source_image.width, source_image.height)
    destination_window = FalconImageDisplay(destination_image, "Prediction")
    destination_window.set_location(2*destination_image.width, 20)

    # start = datetime.datetime.now()
    # model.fit(training_inputs, training_outputs, batch_size=32, epochs=50)
    # end = datetime.datetime.now()
    # print(f"Time to create and train: {end - start}.")
    #
    # destination_image = FalconImage(None, source_image.width, source_image.height)
    # destination_window = FalconImageDisplay(destination_image, "Prediction")
    # destination_window.set_location(destination_image.width,0)
    #
    pyglet.clock.schedule_interval(perform_animation_step, 1)
    #
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
        results.append([(x/img.width,y/img.height),color,attractor])
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
            closest_attractor_num = find_closest_attractor_to_color(attractors, data_color)
            if closest_attractor_num != data_attractor:
                data[2] = closest_attractor_num
                made_a_change = True

        if made_a_change:
            # RECALCULATE MEANS FOR THE ATTRACTORS
            for i in range(k):
                color_sums = [0,0,0]
                N = 0
                for data in source_points:
                    if data[2] == i:
                        data_color = data[1]
                        for j in range(3):
                            color_sums[j] += data_color[j]
                        N += 1
                if N > 0:
                    for j in range(3):
                        color_sums[j] = int(color_sums[j]/N)
                    attractors[i] = color_sums
                else:
                    attractors[i] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

        else:
            break # done with the k Means search process.

    return attractors

def find_closest_attractor_to_color(attractors: List[Color], col: Color) -> int:

    closest_color_dist_squared = 200000
    closest_attractor_num = -1
    for i in range(k):
        attractor_color = attractors[i]
        dist_squared = 0
        for j in range(3):
            dist_squared += (attractor_color[j] - col[j]) ** 2
        if dist_squared < closest_color_dist_squared:
            closest_color_dist_squared = dist_squared
            closest_attractor_num = i

    return closest_attractor_num

def generate_reduced_color_image(attractors: List[Color], img: FalconImage) -> None:
    result_image = FalconImage(None, img.width, img.height+20)
    for x in range(img.width):
        for y in range(img.height):
            c = img.get_RGB_at(x,y)
            att = find_closest_attractor_to_color(attractors = attractors, col=c)
            result_image.set_RGB_at(attractors[att], x, y)

    box_width = int(img.width/k)
    for i in range(k):
        result_image.set_RGB_region_at_rect([[color_attractors[i] for k in range(box_width)] for j in range(20)],
                                            (box_width * i, img.height, box_width, 20))

    result_image.refresh()
    reduced_color_window = FalconImageDisplay(result_image, "Reduced Color Image")
    reduced_color_window.set_location(0,0)

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
        sample_image.set_RGB_at(color=color_attractors[p[2]], x=int(p[0][0]*source_width),
                                y=int(p[0][1]*source_height))
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


def create_ANN_model() -> tf.keras.Model:
    my_model = tf.keras.Sequential(
        [
            layers.Dense(40, activation='relu'),
            layers.Dense(40, activation='sigmoid'),
            layers.Dense(500, activation='sigmoid'),
            layers.Dense(500, activation='sigmoid'),
            layers.Dense(150, activation='sigmoid'),
            layers.Dense(30, activation='sigmoid'),
            layers.Dense(k, activation='relu')

        ]
    )

    my_model.compile(loss=tf.keras.losses.MeanSquaredError(),
                          optimizer=tf.optimizers.Adam())

    return my_model

def perform_animation_step(deltaT: float):
    """
    asks the AI model to predict the attractor number for "num_points_per_update" random points on the screen and draws
    the corresponding colored dots in the window.
    :param deltaT: The time since the last perform_animation_step (not used)
    :return: None
    """
    global destination_image, destination_window, total_epochs_so_far

    start = datetime.datetime.now()
    model.fit(training_inputs, training_outputs, batch_size=32, epochs=epochs_per_animation_step)
    total_epochs_so_far += epochs_per_animation_step
    end = datetime.datetime.now()
    print(f"Time to create and train: {end - start}.")
    print(f"Total Epochs used to train this model: {total_epochs_so_far}")
    print("Generating new points")
    points = []
    for i in range(num_points_per_update):
        p = (random.random(), random.random())
        points.append(p)

    # for x in range(destination_image.width):
    #     for y in range(destination_image.height):
    #         points.append((x/destination_image.width, y/destination_image.height))
    print("Predicting colors at points")
    output = model.predict(points)

    print("Plotting points")
    for i in range(len(output)):
        scores = output[i]
        max_value = -99999
        max_index = 0
        for j in range(k):
            if scores[j] > max_value:
                max_value = scores[j]
                max_index = j
        destination_image.set_RGB_at(color_attractors[max_index], int(points[i][0]*destination_image.width),
                                     int(points[i][1]*destination_image.height))

    destination_image.refresh()
    destination_window.update()
    print("Done.")

def get_mode_and_filename():
    no_choice_made = True
    while no_choice_made:
        new_or_load_string = input("Do you want to 1) start fresh or 2) load an existing ANN?")
        try:
            new_or_load_num = int(new_or_load_string)
            if new_or_load_num > 0 and new_or_load_num < 3:
                no_choice_made = False
            else:
                print("Out of range. Please try again.")
        except:
            print("That was not a valid choice.")

    data_filename = input("Type in the filename you wish to use, without the suffix.")
    return new_or_load_num, data_filename

if __name__ == '__main__':
    main()
