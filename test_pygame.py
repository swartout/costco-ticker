import math
import pygame as py

py.init()

clock = py.time.Clock()

FrameHeight = 600
FrameWidth = 1200

# PYGAME FRAME WINDOW
py.display.set_caption("Endless Scrolling in pygame")
screen = py.display.set_mode((FrameWidth, FrameHeight))

# IMAGES
image_files = ["image1.png", "image2.png", "image3.png", 'image3.png', 'image3.png']  # Add your image filenames here
images = [py.image.load(img).convert() for img in image_files]

# CONCATENATE IMAGES SIDE BY SIDE
total_width = sum(image.get_width() for image in images)
scroll_image = py.Surface((total_width, FrameHeight))

x_offset = 0
for img in images:
    scroll_image.blit(img, (x_offset, 0))
    x_offset += img.get_width()

# DEFINING MAIN VARIABLES IN SCROLLING
scroll = 0

# MAIN LOOP
while True:
    # THIS WILL MANAGE THE SPEED OF THE SCROLLING IN PYGAME
    clock.tick(33)

    # SCROLLING LOGIC
    scroll -= 6
    if abs(scroll) > total_width:
        scroll = 0

    # DRAWING THE SCROLLING IMAGE
    screen.blit(scroll_image, (scroll, 0))
    screen.blit(scroll_image, (scroll + total_width, 0))

    # CLOSING THE FRAME OF SCROLLING
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()

    py.display.update()
