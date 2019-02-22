# Used to find Mr T-Rex
import cv2

# used for screenshotting and checking for cactus
from PIL import Image, ImageGrab
import numpy as np

# Used for spacebar auto press
import pyautogui

# Used to detect when the game starts
from pynput.keyboard import Key, Listener

# used to plot the pixel density at the end of the game
import matplotlib
import matplotlib.pyplot as plt

# Constants
FORWARD_BOX = (850,400,890,500)
GAME_OVER_BOX = (850,350,1100,400)

DEBUG = True

# Convert an image to black & white (NOT grayscale!)
def to_bw(img):
    return img.convert('L').point(lambda x: 0 if x<128 else 255, '1')

# Debug function used to take a screen shot and add the original boxes
# position (the one where I put the coordinates by myself)
def print_original_boxes():
    im = ImageGrab.grab()
    fb = Image.new("RGB", (FORWARD_BOX[2] - FORWARD_BOX[0], FORWARD_BOX[3] - FORWARD_BOX[1]), "GREEN")
    im.paste(fb, (FORWARD_BOX[0], FORWARD_BOX[1]))
    gob = Image.new("RGB", (GAME_OVER_BOX[2] - GAME_OVER_BOX[0], GAME_OVER_BOX[3] - GAME_OVER_BOX[1]), "BLUE")
    im.paste(gob, (GAME_OVER_BOX[0], GAME_OVER_BOX[1]))
    im.save("original_pos.png", "PNG")

# Find the T-Rex on the screen
def find_t_rex():
    im = np.array(ImageGrab.grab().convert('RGB'))
    t_rex = cv2.imread("t_rex.png")

    # Match the t_rex image in the im image
    result = cv2.matchTemplate(im,t_rex,cv2.TM_CCOEFF_NORMED)

    # Get the metric value of the best matching
    matching_value = result[np.unravel_index(result.argmax(), shape=result.shape)]

    # If debug, export the screenshot with the t_rex_position
    if DEBUG:
        print(f'Matching value: {matching_value}')
        coordinates = np.unravel_index(result.argmax(),result.shape)
        height, width, _ = t_rex.shape
        box = (coordinates[1], coordinates[1] + width, coordinates[0], coordinates[0] + height)
        im = Image.fromarray(im)
        t_rex_pos = Image.new("RGB", (width, height), "RED")
        im.paste(t_rex_pos, (coordinates[1], coordinates[0]))
        im.save("pos.png", "PNG")


    # If this is not at least a 90% matching, we consider that Mr T-Rex is not on the screen
    if matching_value < 0.90:
        return False

    # Return the top-left coordinates of the best matching
    return np.unravel_index(result.argmax(),result.shape)

# Set the forward and game over boxes coordinates
def set_boxes(t_rex_coord):
    t_rex_size = Image.open("t_rex.png").size

    forward_box = (t_rex_coord[0] + t_rex_size[0], t_rex_coord[1] - 50 + 27, t_rex_coord[0] + 175, t_rex_coord[1] - 50 + 100 + 27)
    game_over_box = (t_rex_coord[0] + 200 - 12, t_rex_coord[1] - 100 + 27, t_rex_coord[0] + 200 + 250 - 12, t_rex_coord[1] - 100 + 50 + 27)

    if DEBUG:
        print(forward_box)
        print(game_over_box)

        im = Image.open('pos.png')

        bb_fo = Image.new("RGB", (forward_box[2] - forward_box[0], forward_box[3] - forward_box[1]), "GREEN")
        im.paste(bb_fo, (forward_box[0], forward_box[1]))

        bb_go = Image.new("RGB", (game_over_box[2] - game_over_box[0], game_over_box[3] - game_over_box[1]), "BLUE")
        im.paste(bb_go, (game_over_box[0], game_over_box[1]))

        im.save("pos.png", "PNG")

    return forward_box, game_over_box

# Returns the black pixel density in the forward box, or returns false
# if the " GAME OVER " text is on screen
def get_pixel_density(forward_box, game_over_box):
    im = ImageGrab.grab()
    region = im.crop(forward_box)
    bw = to_bw(region)

    # Count the density of pixels (since we only have black or white, anything above 0 is white)
    # white_density = nb_white / nb_total
    white_density = np.array(bw).sum() / ((forward_box[2] - forward_box[0]) * (forward_box[3] - forward_box[1]))

    # If there is some black pixels on the " GAME OVER " box, stop the game
    # (Bug: if there is a pterodactyl passing by, it stops the game)
    if np.array(to_bw(im.crop(game_over_box))).sum() / ((game_over_box[2] - game_over_box[0]) * (game_over_box[3] - game_over_box[1])) < 1.0:
        return False

    # return the number of black pixels (black_density = 1 - white_density)
    return (1 - white_density)

# Check when spacebar is pressed
def on_press(key):
    if key == Key.space:
        return False

def main():
    forward_box = ()
    game_over_box = ()

    values = []
    counter = 0
    mean_var_set = False
    mean = 1
    variation = 0

    if DEBUG:
        print_original_boxes()


    print('Finding Mr T-Rex...')
    t_rex_coord = find_t_rex()

    if not t_rex_coord:
        print('It seems that Mister T-Rex is not on the screen >:(')
        return False

    print('Mister T-rex found!')

    print('Setting boxes...')
    # Reversing the tuple since the np.unravel_indexes function gives
    # the coordinates (y, x)
    forward_box, game_over_box = set_boxes(t_rex_coord[::-1])
    print('Boxes set.')

    print('Waiting for game to start...')
    keyboard = Listener()
    with Listener(on_press=on_press, on_release=None) as listener:
        listener.join()

    print('GO GO GO!')

    while True:
        # Get the black pixel density
        pixel_density = get_pixel_density(forward_box, game_over_box)

        if pixel_density == False:
            break

        values.append(pixel_density)

        # If there is a cactus on the forward box, jump!
        if mean_var_set and pixel_density > mean + (variation * 2):
            pyautogui.press('space')

        counter += 1

        # Set the mean and variation values for black pixels density in the forward box
        if mean_var_set == False and counter > 50:
            subvals = values[30:]
            mean = sum(subvals) / len(subvals)
            variation = abs(max(subvals)) - abs(min(subvals))
            mean_var_set = True

            if DEBUG:
                print(f'mean and var set: {mean} / {variation}')


    if DEBUG:
        fig, ax = plt.subplots()
        ax.plot([x for x in range(len(values))], values)
        ax.axhline(y=mean, color='green')
        ax.axhline(y=mean + (variation * 2), color='red')
        ax.set(xlabel='Frame number', ylabel='Black pixel density',
           title='Black pixel density per frame')
        ax.grid()
        plt.show()

if __name__ == '__main__':
    main()