from pygame import image
keys = list(range(256, 266))
images = [image.load("stamps/" + str(i) + ".png") for i in range(10)]

stamps = {}

for i in range(10):
    stamps[keys[i]] = images[i]
