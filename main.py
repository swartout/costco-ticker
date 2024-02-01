import pygame as py
import time
import shutil

from scraper import COSTCO_URL, get_item, get_soup, make_img

# Constants
FRAME_HEIGHT = 900
FRAME_WIDTH = 1500
DOT_SIZE = 2
SPACING = 5
SCROLL_SPEED = 6
FPS = 10
CYCLE_TIME = 10
NUM_ITEMS = 24

# Function to apply the dot matrix filter
def dot_matrix_filter(surface, dot_size, spacing):
    matrix_surface = py.Surface(surface.get_size(), py.SRCALPHA)
    
    for y in range(0, surface.get_height(), spacing):
        for x in range(0, surface.get_width(), spacing):
            color = surface.get_at((x, y))
            py.draw.circle(matrix_surface, color, (x, y), dot_size)
    
    return matrix_surface

py.init()

clock = py.time.Clock()

# PYGAME FRAME WINDOW
py.display.set_caption("Endless Scrolling with LED Board Effect")
screen = py.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT), py.FULLSCREEN)

while True:

    try:
        shutil.rmtree('images/')
    except FileNotFoundError as e:
        pass
    soup = get_soup(COSTCO_URL)
    image_files = []
    for i in range(NUM_ITEMS):
        item = get_item(soup, i)
        if item is not None:
            item_file = f'item_{i}.png'
            image_files.append('images/' + item_file)
            make_img(item, item_file)

    images = [py.image.load(img).convert() for img in image_files]

    # CONCATENATE IMAGES SIDE BY SIDE
    total_width = sum(image.get_width() for image in images)
    extended_width = total_width + FRAME_WIDTH
    scroll_image = py.Surface((extended_width, FRAME_HEIGHT))

    x_offset = 0
    for img in images:
        scroll_image.blit(img, (x_offset, 0))
        x_offset += img.get_width()

    # Copy the initial part of the scroll image to the end to create a seamless transition
    initial_part_surface = py.Surface((FRAME_WIDTH, FRAME_HEIGHT))
    initial_part_surface.blit(scroll_image, (0, 0), (0, 0, FRAME_WIDTH, FRAME_HEIGHT))
    scroll_image.blit(initial_part_surface, (total_width, 0))

    # MAIN VARIABLES FOR SCROLLING
    scroll = 0

    start_time = time.time()

    # MAIN LOOP
    while True:
        if time.time() - start_time > CYCLE_TIME:
            break
        clock.tick(FPS)

        # SCROLLING LOGIC - Adjusted for correct wrap-around effect
        scroll += SCROLL_SPEED
        if scroll >= total_width:
            scroll -= total_width

        # ENSURE THAT WE NEVER TRY TO BLIT A SUBSURFACE THAT EXCEEDS THE scroll_image BOUNDS
        end_pos = scroll + FRAME_WIDTH
        if end_pos > extended_width:
            # DRAWING THE SCROLLING IMAGE IN TWO PARTS WHEN AT THE EDGE
            right_section_rect = (scroll, 0, extended_width - scroll, FRAME_HEIGHT)
            right_section = scroll_image.subsurface(right_section_rect)
            right_filtered = dot_matrix_filter(right_section, DOT_SIZE, SPACING)
            screen.blit(right_filtered, (0, 0))

            left_section_rect = (0, 0, FRAME_WIDTH - right_section.get_width(), FRAME_HEIGHT)
            left_section = scroll_image.subsurface(left_section_rect)
            left_filtered = dot_matrix_filter(left_section, DOT_SIZE, SPACING)
            screen.blit(left_filtered, (right_section.get_width(), 0))
        else:
            # DRAWING THE SCROLLING IMAGE AS USUAL
            visible_section_rect = (scroll, 0, FRAME_WIDTH, FRAME_HEIGHT)
            visible_section = scroll_image.subsurface(visible_section_rect)
            filtered_section = dot_matrix_filter(visible_section, DOT_SIZE, SPACING)
            screen.blit(filtered_section, (0, 0))

        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()

        py.display.update()