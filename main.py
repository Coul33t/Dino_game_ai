from PIL import Image, ImageGrab
import pyautogui

import numpy
import scipy.ndimage

import matplotlib
import matplotlib.pyplot as plt

FORWARD_BOX = (850,400,890,500)
GAME_OVER_BOX = (850,350,1100,400)

def to_bw(img):
    return img.convert('L').point(lambda x: 0 if x<128 else 255, '1')


def test_screen():
    im = ImageGrab.grab()
    region = im.crop(FORWARD_BOX)
    bw = to_bw(region)
    count_forward = numpy.array(bw).sum() / ((FORWARD_BOX[2] - FORWARD_BOX[0]) * (FORWARD_BOX[3] - FORWARD_BOX[1]))

    if numpy.array(to_bw(im.crop(GAME_OVER_BOX))).sum() / ((GAME_OVER_BOX[2] - GAME_OVER_BOX[0]) * (GAME_OVER_BOX[3] - GAME_OVER_BOX[1])) < 1.0:
        return False

    return count_forward

if __name__ == '__main__':
    values = []
    counter = 0
    mena_var_set = False
    mean = 1
    var = 0

    print('Waiting for game to start...')
    while not test_screen():
        pass

    print('GO GO GO')
    while True:
        val = test_screen()

        if val == False:
            break

        values.append(test_screen())

        if mena_var_set and val < mean - var:
            pyautogui.press('space')

        counter += 1

        if mena_var_set == False and counter > 10:
            mean = sum(values) / len(values)
            var = abs(max(values)) - abs(min(values))
            mena_var_set = True


    fig, ax = plt.subplots()
    ax.plot([x for x in range(len(values))], values)
    ax.set(xlabel='Screen capture number', ylabel='White pixel density',
       title='White pixel density per frame')
    ax.grid()
    plt.show()