import pygame
import math
import ctypes
from pygame.locals import *
from math import atan, pi
from random import randint, choice
from copy import deepcopy
from possible_adjacent_combinations import indexloop
from button import Button
from block import Block, set_block_orientation
from truncate_decimal import truncate
import editor

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()
width, height = 1920, 1080
ctypes.windll.user32.SetProcessDPIAware()
# true_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
true_res = (1920, 1080)
scale_mult = (truncate(true_res[0] / width, 8), truncate(true_res[1] / height, 8))
scale = False if scale_mult == (1.0, 1.0) else True

with open("game_settings", "r") as r:
    a = (r.read()).split()
    graphics_settings = [True if a[0] == "1" else False, True if a[1] == "1" else False, True if a[2] == "1" else False, True if a[3] == "1" else False]
    sound_settings = [True if a[4] == "1" else False, True if a[5] == "1" else False]
    num_3d_slices = int(a[6])
if graphics_settings[3]:
    win = pygame.display.set_mode(true_res, pygame.FULLSCREEN)
else:
    win = pygame.display.set_mode(true_res)
center = (win.get_width() / 2, win.get_height() / 2)
blocksize = None
max_playersize = 300
solids, hazards, blocks_with_empty_space = ("solid", "nonstickysolid"), ("spike", "lava"), ("air", "spawnpoint", "spike", "end")
sound_library = {"spawn": pygame.mixer.Sound("sfx/spawn.wav"), "charge": pygame.mixer.Sound("sfx/charge.wav"), "launch": pygame.mixer.Sound("sfx/launch.wav"), "ability": pygame.mixer.Sound("sfx/ability.wav"), "mediumimpact1": pygame.mixer.Sound("sfx/mediumimpact1.wav"), "mediumimpact2": pygame.mixer.Sound("sfx/mediumimpact2.wav"), "largeimpact1": pygame.mixer.Sound("sfx/largeimpact1.wav"),
                 "largeimpact2": pygame.mixer.Sound("sfx/largeimpact2.wav"), "bounce": pygame.mixer.Sound("sfx/bounce.wav"), "spike_death": pygame.mixer.Sound("sfx/spike_death.wav"), "lava_death": pygame.mixer.Sound("sfx/lava_death.wav"), "kill_all_death": pygame.mixer.Sound("sfx/spontaneous_death.wav"), "hover": pygame.mixer.Sound("sfx/hover.wav"), "select": pygame.mixer.Sound("sfx/select.wav"),
                 "drag": pygame.mixer.Sound("sfx/drag.wav"), "place": pygame.mixer.Sound("sfx/place block.wav"), "preview": pygame.mixer.Sound("sfx/preview.wav"), "error": pygame.mixer.Sound("sfx/error.wav"), "win": pygame.mixer.Sound("sfx/win.wav"), "play": pygame.mixer.Sound("sfx/play level.wav"), "whoosh": pygame.mixer.Sound("sfx/menu_whoosh.wav")}
pygame.mixer.music.load("sfx/ups_and_downs.wav")
pygame.mixer.music.set_volume(0.45 if sound_settings[1] else 0.0)
event_sound_triggers = [False, False]
block_textures, three_d_textures = {}, {}
pygame.display.set_caption("A Gravity Game")
pygame.display.set_icon(pygame.image.load("textures/icon2.png"))


block_surfaces = [pygame.image.load("textures/solidspritesheet.png").convert(), pygame.image.load("textures/notstickyspritesheet.png").convert(), pygame.image.load("textures/spike.png").convert()]
lava_surfaces = [pygame.image.load("textures/lava.png").convert(), pygame.Surface((199, 199)).convert(), pygame.Surface((199, 199)).convert()]
three_d_surfaces = [pygame.image.load("textures/3Dtextures.png").convert(), pygame.Surface((106, 105)).convert(), pygame.Surface((106, 95)).convert(), pygame.Surface((106, 105)).convert(), pygame.Surface((100, 100)).convert()]
vignette_texture = pygame.image.load("textures/vignette.png").convert_alpha()
bg_surfaces = [pygame.image.load("textures/BGparallax1.png").convert(), pygame.image.load("textures/BGparallax2.png").convert_alpha() if scale else pygame.image.load("textures/BGparallax2.png").convert(), pygame.image.load("textures/BGparallax3.png").convert_alpha()]
environmental_particles = pygame.image.load("textures/backgroundparticles.png").convert_alpha()
endgradient = pygame.image.load("textures/endgradient.png").convert_alpha()
levelwinsurfaces = pygame.image.load("textures/levelwintextures.png").convert_alpha()
pausesurfaces = pygame.image.load("textures/pausetextures.png").convert_alpha()
editorbuttonsurfaces = pygame.image.load("textures/editorbuttons.png").convert_alpha()
numbersurfaces = pygame.image.load("textures/numbers.png").convert_alpha()
arrow = pygame.image.load("textures/arrow.png").convert_alpha()
editorsettingsbartextures = pygame.image.load("textures/editorsettingsbar.png").convert_alpha()
entity_attributes = pygame.image.load("textures/entity_attributes.png").convert_alpha()
menubuttonsurfaces = pygame.image.load("textures/menubuttontextures.png").convert_alpha()
settingwordsurfaces = pygame.image.load("textures/settingswords.png").convert_alpha()
introanimationsurfaces = pygame.image.load("textures/intro animation.png").convert_alpha()
flash_surfaces = pygame.image.load("textures/flash_spritesheet.png").convert_alpha()
editorinvisblocktextures = []

editor_bg = pygame.image.load("textures/editorBG.png").convert()


def convert_spritesheet_to_textures(spritesheet, surfaces, surface_positions):
    converted_surfaces = []
    if type(surfaces) == tuple:
        for index, i in enumerate(tuple(surfaces)):
            converted_surfaces.append(i)
            converted_surfaces[index].blit(spritesheet, surface_positions[index])
    else:
        converted_surfaces = surfaces
        converted_surfaces.blit(spritesheet, surface_positions)
    for index, surface in enumerate(converted_surfaces):
        if scale:
            converted_surfaces[index] = pygame.transform.smoothscale(surface, (surface.get_width() * scale_mult[0], surface.get_height() * scale_mult[1]))
    return converted_surfaces if type(surfaces) == tuple else converted_surfaces


def scale_textures(surface_list):
    if scale:
        if type(surface_list) == list:
            converted_surface_list = surface_list.copy()
            for index, surface in enumerate(surface_list):
                converted_surface_list[index] = pygame.transform.smoothscale(surface, (surface.get_width() * scale_mult[0], surface.get_height() * scale_mult[1]))
        else:
            converted_surface_list = pygame.transform.smoothscale(surface_list, (surface_list.get_width() * scale_mult[0], surface_list.get_height() * scale_mult[1]))
        return converted_surface_list
    else:
        return surface_list


for i in bg_surfaces[0:2]:
    i.set_colorkey((0, 0, 0))
bg_surfaces = scale_textures(bg_surfaces)


bg = {
    0: {"bg": bg_surfaces[0], "width": bg_surfaces[0].get_width(), "height": bg_surfaces[0].get_height()},
    1: {"bg": bg_surfaces[1], "width": bg_surfaces[1].get_width(), "height": bg_surfaces[1].get_height()},
    2: {"bg": bg_surfaces[2], "width": bg_surfaces[2].get_width(), "height": bg_surfaces[2].get_height()}
}


winbuttontextures = convert_spritesheet_to_textures(levelwinsurfaces, (pygame.Surface((1, 1080), SRCALPHA), pygame.Surface((1057, 567), SRCALPHA), pygame.Surface((339, 339), SRCALPHA), pygame.Surface((339, 339), SRCALPHA), pygame.Surface((339, 339), SRCALPHA)), ((-1, 0), (-3, 6), (-1061, -3), (-1400, -3), (-1739, -3)))
levelwinbar = winbuttontextures[0].copy()
winbuttontextures.pop(0)
pausetextures = convert_spritesheet_to_textures(pausesurfaces, (pygame.Surface((1920, 1080), SRCALPHA), pygame.Surface((1396, 889), SRCALPHA), pygame.Surface((247, 59), SRCALPHA), pygame.Surface((226, 58), SRCALPHA), pygame.Surface((261, 58), SRCALPHA), pygame.Surface((229, 58), SRCALPHA), pygame.Surface((161, 59), SRCALPHA)), ((0, 0), (-1925, 6), (-3321, -33), (-3572, -33), (-3802, -33), (-4067, -33), (-4300, -33)))
pause_bg = pausetextures[0]
pause_bg = pygame.transform.scale(pause_bg, (1920 * scale_mult[0], 1082 * scale_mult[1]))
pausetextures.pop(0)
editorbuttontextures = convert_spritesheet_to_textures(editorbuttonsurfaces, (pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA), pygame.Surface((126, 125), SRCALPHA)), ((0, 0), (-126, 0), (-252, 0), (-378, 0), (-504, 0), (-630, 0), (-756, 0), (-882, 0), (-1008, 0),  (-1134, 0)))
numbertextures = convert_spritesheet_to_textures(numbersurfaces, (pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA), pygame.Surface((117, 117), SRCALPHA)),
                                                 ((0, 0), (-117, 0), (-234, 0), (-351, 0), (0, -117), (-117, -117), (-234, -117), (-351, -117), (0, -234), (-117, -234)))
numbertextures = {"0": numbertextures[0], "1": numbertextures[1], "2": numbertextures[2], "3": numbertextures[3], "4": numbertextures[4], "5": numbertextures[5], "6": numbertextures[6], "7": numbertextures[7], "8": numbertextures[8], "9": numbertextures[9]}
editorsettingstextures = convert_spritesheet_to_textures(editorsettingsbartextures, (pygame.Surface((1729, 176), SRCALPHA), pygame.Surface((1729, 176), SRCALPHA)),
                                                         ((0, 0), (0, -176)))
entityattributetextures = convert_spritesheet_to_textures(entity_attributes, (pygame.Surface((112, 75), SRCALPHA), pygame.Surface((97, 75), SRCALPHA), pygame.Surface((117, 75), SRCALPHA), pygame.Surface((92, 75), SRCALPHA), pygame.Surface((101, 75), SRCALPHA), pygame.Surface((102, 75), SRCALPHA), pygame.Surface((108, 75), SRCALPHA), pygame.Surface((102, 75), SRCALPHA), pygame.Surface((79, 75), SRCALPHA), pygame.Surface((94, 75), SRCALPHA)),
                                                         ((0, 0), (-112, 0), (-209, 0), (-326, 0), (-418, 0), (-519, 0), (-621, 0), (-729, 0), (-831, 0), (-910, 0)))
menubuttontextures = convert_spritesheet_to_textures(menubuttonsurfaces, (pygame.Surface((1039, 565), SRCALPHA), pygame.Surface((395, 166), SRCALPHA), pygame.Surface((395, 166), SRCALPHA), pygame.Surface((395, 166), SRCALPHA), pygame.Surface((395, 166), SRCALPHA), pygame.Surface((229, 220), SRCALPHA), pygame.Surface((373, 230), SRCALPHA), pygame.Surface((395, 166), SRCALPHA), pygame.Surface((759, 349), SRCALPHA), pygame.Surface((1074, 1130), SRCALPHA)),
                                                 ((0, 0), (-1039, 0), (-1434, 0), (0, -565), (-395, -565), (-790, -565), (-1019, -565), (-1392, -565), (0, -794), (-759, -794)))
introanimationtextures = convert_spritesheet_to_textures(introanimationsurfaces, (pygame.Surface((2305, 1298), SRCALPHA), pygame.Surface((2305, 1298), SRCALPHA), pygame.Surface((2309, 1301), SRCALPHA), pygame.Surface((2309, 1301), SRCALPHA), pygame.Surface((2309, 1301), SRCALPHA), pygame.Surface((2309, 1301), SRCALPHA), pygame.Surface((2309, 1301), SRCALPHA), pygame.Surface((2309, 1301), SRCALPHA)),
                                                 ((0, 0), (-2305, 0), (-4610, 0), (0, -1301), (-2309, -1301), (-4618, -1301), (0, -2602), (-2309, -2602)))

settingswordstextures = convert_spritesheet_to_textures(settingwordsurfaces, (pygame.Surface((251, 109), SRCALPHA), pygame.Surface((220, 109), SRCALPHA), pygame.Surface((326, 109), SRCALPHA), pygame.Surface((339, 109), SRCALPHA), pygame.Surface((173, 109), SRCALPHA), pygame.Surface((136, 109), SRCALPHA), pygame.Surface((117, 109), SRCALPHA), pygame.Surface((122, 109), SRCALPHA), pygame.Surface((155, 109), SRCALPHA),  pygame.Surface((303, 109), SRCALPHA),  pygame.Surface((255, 109), SRCALPHA),  pygame.Surface((255, 109), SRCALPHA)),
                                                 ((0, 0), (-251, 0), (-471, 0), (-797, 0), (-1136, 0), (-1309, 0), (-1445, 0), (-1562, 0), (-1684, 0), (-1839, 0), (-2142, 0), (-2397, 0)))
for index, surface in enumerate(settingswordstextures):
    if not index == 8:
        settingswordstextures[index] = pygame.transform.scale(surface, (int(surface.get_width() * (0.42 if index == 10 or index == 11 else 0.85)), int(surface.get_height() * (0.42 if index == 10 or index == 11 else 0.85))))
flash = convert_spritesheet_to_textures(flash_surfaces, (pygame.Surface((1920, 1080), SRCALPHA), pygame.Surface((1920, 1080), SRCALPHA), pygame.Surface((1920, 1080), SRCALPHA), pygame.Surface((1920, 1080), SRCALPHA), pygame.Surface((1920, 1080), SRCALPHA), pygame.Surface((1920, 1080), SRCALPHA)),
                                        ((0, 0), (-1921, 0), (0, -1081), (-1921, -1081), (0, 0), (0, -2162)))
arrow_corrected = pygame.Surface((144, 80), pygame.SRCALPHA)
arrow_corrected.blit(arrow, (0, 0))
arrow = arrow_corrected.copy()

arrowtextures = [arrow, pygame.transform.flip(arrow, True, False)]
for i in range(2):
    arrowtextures[i] = pygame.transform.scale(arrowtextures[i].copy(), (43, 25))

playertextures = [pygame.image.load("textures/tracer.png").convert(), pygame.image.load("textures/ability slime textures.png").convert()]
for i in range(6):
    playertextures.append(pygame.Surface((114, 114)))
    playertextures[2 + i].blit(playertextures[1], (-1 + -114 * i, 0))
playertextures.pop(1)
for i in playertextures:
    i.set_colorkey((0, 0, 0))

environmental_particle_surfaces = [pygame.Surface((85, 21), pygame.SRCALPHA), pygame.Surface((65, 44), pygame.SRCALPHA), pygame.Surface((90, 24), pygame.SRCALPHA), pygame.Surface((72, 25), pygame.SRCALPHA), pygame.Surface((40, 41), pygame.SRCALPHA)]
for itemindex, i in enumerate((0, -21, -65, -89, -114)):
    environmental_particle_surfaces[itemindex].blit(environmental_particles, (0, i))

playertypes = {
    "normal": ("normal", (60, 207, 86), playertextures[1].copy()),
    "doublejump": ("doublejump", (111, 189, 247), playertextures[2].copy()),
    "gravityswitch": ("gravityswitch", (222, 145, 255), playertextures[3].copy()),
    "groundpound": ("groundpound", (255, 155, 155), playertextures[4].copy()),
    "nogravity": ("nogravity", (200, 200, 200), playertextures[5].copy()),
    "mitosis": ("mitosis", (74, 213, 182), playertextures[6].copy()),
               }

for i in ("normal", "doublejump", "gravityswitch", "groundpound", "nogravity", "mitosis"):
    editorinvisblocktextures.append(pygame.transform.scale(playertypes[i][2], (100, 100)))
editorinvisblocktextures.append(pygame.image.load("textures/visible_air.png").convert_alpha())
editorinvisblocktextures[6] = pygame.transform.scale(editorinvisblocktextures[6], (editor.editorsize, editor.editorsize))

arrowtextures = scale_textures(arrowtextures)
vignette_texture = scale_textures(vignette_texture)
editor_bg = scale_textures(editor_bg)
environmental_particle_surfaces = scale_textures(environmental_particle_surfaces)
editor_pause_bg = pause_bg.copy()
pause_bg.blit(vignette_texture, (0, 0))


def setup_level(txt, reload=False):  # the worst line of code in human history
    global level, spawnpoint, blocksize, entities, camera_boundaries, end_hitboxes, lava_layer, bugfix_end_gradients, spawnpoint, bg_slices, lava_timer, keystrokes, camera, camera_shake, camera_shake_power, camera_shake_timer, camera_ease, camera_non_offset_coords, focus, victory, victory_timer, background_robots, sparks, lava_particles, ripples, winbuttons, end_direction, num_3d_slices, global_death_timer
    if not reload and sound_settings[0]:
        pygame.mixer.Sound.stop(sound_library["select"])
        pygame.mixer.Sound.play(sound_library["play"])
    level, spawnpoint, blocksize, entities, camera_boundaries, end_hitboxes, lava_layer, bugfix_end_gradients, end_direction = setup_leveldata(txt.read(), num_3d_slices)
    spawnpoint = spawnpoint[0].copy()
    bg_slices, lava_timer, keystrokes = 2, 0, {"x": False, "z": False, "esc": False, "right": False, "left": False, "up": False, "down": False, "d": False, "a": False, "w": False, "s": False}
    camera, camera_shake, camera_shake_power, camera_shake_timer, camera_ease, camera_non_offset_coords, focus, victory, victory_timer = ((entities[0].position[0] - width / 2), (entities[0].position[1] - height / 2)), (0, 0), (0, 0), 0, (0, 0), ((entities[0].position[0] - width / 2), (entities[0].position[1] - height / 2)), 0, False, 0
    background_robots, sparks, lava_particles, ripples = [], [], [], []
    winbuttons = [Button(winbuttontextures[0], (width / 2, height / 2), 0.8, [0, 0], True), Button(winbuttontextures[1], (width / 2 - 290, height * 0.7), 0.76, [0, 660]), Button(winbuttontextures[2], (width / 2, height * 0.7), 0.76, [0, 660]), Button(winbuttontextures[3], (width / 2 + 290, height * 0.7), 0.76, [0, 660])]
    sparks.clear()
    global_death_timer = 11

    for _ in range(13):
        background_robots.append(Particle("environmental", environmental_particle_surfaces[randint(0, 3)], (randint(0, width), randint(int(height * 0.3), int(height * 0.7))), (0.23, 0), randint(5, 10), None))


def loadleveldata(leveldata):
    for index, row in enumerate(leveldata[0]):
        leveldata[0][index] = row.split()


def drawobject(surface, position, centered, rect=None, color=None, width=None):
    if scale:
        position = (position[0] * scale_mult[0], position[1] * scale_mult[1])
    if rect is None:
        if centered:
            dimensions = (surface.get_width(), surface.get_height())
            res_scale_blit(surface, (position[0] - (dimensions[0] / 2) - camera[0] - camera_shake[0], position[1] - (dimensions[1] / 2) - camera[1] - camera_shake[1]))
        else:
            res_scale_blit(surface, (position[0] - camera[0] - camera_shake[0], position[1] - camera[1] - camera_shake[1]))
    elif centered:
        if width is None:
            pygame.draw.rect(win, color, ((rect.x - (rect.w / 2) - camera[0] - camera_shake[0]) * scale_mult[0], (rect.y - (rect.h / 2) - camera[1] - camera_shake[1]) * scale_mult[1], rect.w, rect.h))
        else:
            pygame.draw.rect(win, color, ((rect.x - (rect.w / 2) - camera[0] - camera_shake[0]) * scale_mult[0], (rect.y - (rect.h / 2) - camera[1] - camera_shake[1]) * scale_mult[1], rect.w, rect.h), int(width))
    else:
        if width is None:
            pygame.draw.rect(win, color, ((rect.x - camera[0] - camera_shake[0]) * scale_mult[0], (rect.y - camera[1] - camera_shake[1]) * scale_mult[1], rect.w, rect.h))
        else:
            pygame.draw.rect(win, color, ((rect.x - camera[0] - camera_shake[0]) * scale_mult[0], (rect.y - camera[1] - camera_shake[1]) * scale_mult[1], rect.w, rect.h), int(width))


def res_scale_blit(surface, position):
    if scale:
        position = (position[0] * scale_mult[0], position[1] * scale_mult[1])
        if surface == menubar or surface == levelwinbar:
            pygame.draw.rect(win, (0, 0, 0), (position[0], position[1], surface.get_width(), surface.get_height()))
    win.blit(surface, position)


def renderlevel(level, lava_layer, bugfix_end_gradients, paused, splice=None):
    global sparks
    if splice is None:
        splice = [[0, len(level[0])], [0, len(level)]]
    splice[0][0], splice[1][0] = 0 if splice[0][0] < 0 else splice[0][0], 0 if splice[1][0] < 0 else splice[1][0]
    splice_chunks = [[(splice[0][0] + 1 if not splice[0][0] == 0 else 0) * blocksize, (splice[0][1] - 1) * blocksize], [(splice[1][0] + 1 if not splice[1][0] == 0 else 0) * blocksize, (splice[1][1] - 1) * blocksize]]
    for item in bugfix_end_gradients:
        drawobject(block_textures[item.type][item.bordering_blocks], item.position, False)
    for index, i in enumerate(lava_layer):
        for item in i:
            if (not item.position[0] < splice_chunks[0][0]) and (not item.position[0] > splice_chunks[0][1])\
             and (not item.position[1] < splice_chunks[1][0]) and (not item.position[1] > splice_chunks[1][1]):
                drawobject(block_textures[item.type][item.bordering_blocks], item.position if item.bordering_blocks == "none" else item.get_lava_offset(lava_timer), False)
                if index == 1 and not paused:
                    if graphics_settings[1] and randint(0, 70) == 70:
                        direction = {"up": ((randint(-70, 70) / 10, randint(-200, -80) / 10), "down"), "left": ((randint(-200, -80) / 10, randint(-70, 70) / 10), "right"), "down": ((randint(-70, 70) / 10, randint(80, 200) / 10), "up"), "right": ((randint(80, 200) / 10, randint(-70, 70) / 10), "left")}
                        lava_particles.append(Particle("circle", (255, 144, 90), (item.position[0] + item.size / 2, item.position[1] + item.size / 2), direction[item.bordering_blocks][0], randint(7, 10), direction[item.bordering_blocks][1], 0.1))
                    if item.ripple_offset[1] > 0:
                        item.ripple_offset[1] += 1
                        if item.ripple_offset[1] > 35:
                            item.ripple_offset = [0, 0]
    for rowindex, row in enumerate(level[splice[1][0]:splice[1][1]]):  # top layer
        for index, item in enumerate(row[splice[0][0]:splice[0][1]]):
            if not item.type == "air" and not (item.type == "spike" and num_3d_slices > 4) and not item.type == "spawnpoint" and not item.type == "lava":
                drawobject(block_textures[item.type][item.bordering_blocks], item.position if not item.type == "lava" or (item.type == "lava" and item.bordering_blocks == "none") else item.get_lava_offset(), False)
            if item.type in hazards and not (item.type == "lava" and item.bordering_blocks == 'none') and not paused:
                if graphics_settings[1] and randint(0, 1150) == 1150:
                    direction = {"up": (randint(-30, 30) / 50, randint(-30, 0) / 50), "left": (randint(-30, 0) / 50, randint(-30, 30) / 50), "down": (randint(-30, 30) / 50, randint(0, 30) / 50), "right": (randint(0, 30) / 50, randint(-30, 30) / 50)}
                    sparks.append(Particle("environmental", environmental_particle_surfaces[4], (item.position[0] + item.size / 2, item.position[1] + item.size / 2), direction[item.bordering_blocks], 10, None))
    if not paused:
        for item in end_hitboxes:
            if randint(0, 12) == 12:
                direction = {"up": ((randint(-10, 10) / 10, randint(-200, -70) / 10), "none"),
                             "left": ((randint(-200, -70) / 10, randint(-10, 10) / 10), "none"),
                             "down": ((randint(-10, 10) / 10, randint(70, 200) / 10), "none"),
                             "right": ((randint(70, 200) / 10, randint(-10, 10) / 10), "none")}
                lava_particles.append(Particle("circle", (255, 255, 255), (item.x + item.w / 2, item.y + item.h / 2), direction[end_direction][0], randint(5, 10), direction[end_direction][1], 0.1))


def render3Deffect(level, center, lava_timer, splice=None, num_slices=9):
    extrusion = num_slices * 12
    if splice is None:
        splice = [[0, len(level[0])], [0, len(level)]]
    splice[0][0], splice[1][0] = 0 if splice[0][0] < 0 else splice[0][0], 0 if splice[1][0] < 0 else splice[1][0]
    for i in range(num_slices - 1, -1, -1):
        for rowindex, row in enumerate(level[splice[1][0]:splice[1][1]]):
            for index, item in enumerate(row[splice[0][0]:splice[0][1]]):
                if item.type in solids and item.render3D:
                    pos = (item.position[0] - camera[0] - camera_shake[0], item.position[1] - camera[1] - camera_shake[1])
                    if not (item.bordering_blocks == 0 and pos[1] <= 540) and not (item.bordering_blocks == 1 and pos[0] <= 960) and not (item.bordering_blocks == 2 and pos[1] >= 540 - item.size / 2) and not (item.bordering_blocks == 3 and pos[0] >= 960 - item.size / 2)\
                            and not (item.bordering_blocks == 4 and pos[0] <= 960 and pos[1] <= 540) and not (item.bordering_blocks == 5 and pos[0] <= 960 and pos[1] >= 540 - item.size / 2) and not (item.bordering_blocks == 6 and pos[0] >= 960 - item.size / 2 and pos[1] >= 540 - item.size / 2) and not (item.bordering_blocks == 7 and pos[0] >= 960 - item.size / 2 and pos[1] <= 540)\
                            and not (item.bordering_blocks == 15 and (pos[0] <= 960 or pos[1] <= 540)) and not (item.bordering_blocks == 16 and (pos[0] <= 960 or pos[1] >= 540 - item.size / 2)) and not (item.bordering_blocks == 17 and (pos[0] >= 960 - item.size / 2 or pos[1] >= 540 - item.size / 2)) and not (item.bordering_blocks == 18 and (pos[0] >= 960 - item.size / 2 or pos[1] <= 540)):
                        slice_width = int(sorted([abs(((item.position[0] - center[0]) / extrusion)), abs(((item.position[1] - center[1]) / extrusion))])[1] + 1)
                        pygame.draw.rect(win, three_d_textures[item.type][i], (item.position[0] - ((item.position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], item.position[1] - ((item.position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize, blocksize), slice_width)
                        if item.position[1] == 0:
                            pygame.draw.rect(win, three_d_textures[item.type][i], (item.position[0] - ((item.position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], (item.position[1] - blocksize * 2) - ((item.position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize, blocksize * 2), slice_width)
                        elif item.position[1] == (len(level) - 1) * blocksize:
                            pygame.draw.rect(win, three_d_textures[item.type][i], (item.position[0] - ((item.position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], (item.position[1] + blocksize) - ((item.position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize, blocksize * 2), slice_width)
                        if item.position[0] == 0:
                            pygame.draw.rect(win, three_d_textures[item.type][i], ((item.position[0] - blocksize * 2) - ((item.position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], item.position[1] - ((item.position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize * 2, blocksize), slice_width)
                        elif item.position[0] == (len(level[0]) - 1) * blocksize:
                            pygame.draw.rect(win, three_d_textures[item.type][i], ((item.position[0] + blocksize) - ((item.position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], item.position[1] - ((item.position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize * 2, blocksize), slice_width)
                elif item.type == "spike" and not i > num_slices - 3:
                    if not i == 0:
                        drawobject(three_d_textures[item.type][item.bordering_blocks][i], (item.position[0] - ((item.position[0] - center[0]) / extrusion) * (i + 1), item.position[1] - ((item.position[1] - center[1]) / extrusion) * (i + 1)), False)
                    else:
                        drawobject(block_textures[item.type][item.bordering_blocks], (item.position[0] - ((item.position[0] - center[0]) / extrusion) * (i + 1), item.position[1] - ((item.position[1] - center[1]) / extrusion) * (i + 1)), False)
                elif item.type == "lava" and item.render3D:
                    if not (item.bordering_blocks == "up" and item.position[1] - camera[1] - camera_shake[1] <= 540) and not (item.bordering_blocks == "left" and item.position[0] - camera[0] - camera_shake[0] <= 960)\
                            and not (item.bordering_blocks == "down" and item.position[1] - camera[1] - camera_shake[1] >= 540 - item.size / 2) and not (item.bordering_blocks == "right" and item.position[0] - camera[0] - camera_shake[0] >= 960 - item.size / 2):
                        slice_width = int(sorted([abs(((item.position[0] - center[0]) / extrusion)), abs(((item.position[1] - center[1]) / extrusion))])[1] + 2)
                        adjusted_position = item.get_lava_offset(lava_timer)
                        pygame.draw.rect(win, three_d_textures[item.type][i], (adjusted_position[0] - ((adjusted_position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], adjusted_position[1] - ((adjusted_position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize, blocksize), slice_width)
                        if item.position[1] == 0:
                            pygame.draw.rect(win, three_d_textures[item.type][i], (adjusted_position[0] - ((adjusted_position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], (adjusted_position[1] - blocksize * 2) - ((adjusted_position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize, blocksize * 2), slice_width)
                        elif item.position[1] == (len(level) - 1) * blocksize:
                            pygame.draw.rect(win, three_d_textures[item.type][i], (adjusted_position[0] - ((adjusted_position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], (adjusted_position[1] + blocksize) - ((adjusted_position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize, blocksize * 2), slice_width)
                        if item.position[0] == 0:
                            pygame.draw.rect(win, three_d_textures[item.type][i], ((adjusted_position[0] - blocksize * 2) - ((adjusted_position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], adjusted_position[1] - ((adjusted_position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize * 2, blocksize), slice_width)
                        elif item.position[0] == (len(level[0]) - 1) * blocksize:
                            pygame.draw.rect(win, three_d_textures[item.type][i], ((adjusted_position[0] + blocksize) - ((adjusted_position[0] - center[0]) / extrusion) * (i + 1) - camera[0] - camera_shake[0], adjusted_position[1] - ((adjusted_position[1] - center[1]) / extrusion) * (i + 1) - camera[1] - camera_shake[1], blocksize * 2, blocksize), slice_width)
                elif item.render3D and not item.type == "spike":
                    drawobject(three_d_textures[item.type][item.bordering_blocks][i], (item.position[0] - ((item.position[0] - center[0]) / extrusion) * (i + 1), item.position[1] - ((item.position[1] - center[1]) / extrusion) * (i + 1)), False)
        if i == num_slices - 4 and graphics_settings[1]:
            for particle in sparks:
                particle.draw()


def hyp(a, b):
    return math.sqrt(pow(a, 2) + pow(b, 2))


def check_for_level_collisions(level, hitbox, splice=None, default_hitbox=False, return_touching_end=False):
    current_placeholder = None
    entity_collision = None
    touched_end = False
    for entity in grounded_entities:
        if hitbox.colliderect(entity.hitbox):
            entity_collision = (entity.hitbox, entity.landed_direction)
    if entity_collision is None:
        if splice is None:
            splice = [[0, len(level[0])], [0, len(level)]]
        splice[0][0], splice[1][0] = 0 if splice[0][0] < 0 else splice[0][0], 0 if splice[1][0] < 0 else splice[1][0]
        for rowindex, row in enumerate(level[splice[1][0]:splice[1][1]]):
            for itemindex, item in enumerate(row[splice[0][0]:splice[0][1]]):
                if not item.type == "air" and not item.type == "spawnpoint":
                    if hitbox.colliderect(item.hitbox if not default_hitbox and not item.type == "end" else Rect(item.position[0], item.position[1], blocksize, blocksize)):
                        if (item.type in solids or hazards) or item.type == "end":
                            if not (current_placeholder is not None and current_placeholder[1] == "solid" and item.type in hazards) and not item.type == "end":
                                current_placeholder = (item.hitbox, item.type, touched_end)
                            elif item.type == "end" and return_touching_end:
                                touched_end = True
    return (current_placeholder, touched_end, entity_collision) if return_touching_end else current_placeholder


def convert_txt_to_leveldata(txt):
    level, blocksize, leveldata, entitydata = txt.split("\n"), 0, [], []
    blocksize = int(level[0])
    for i in range(1, len(level)):
        if " " not in level[i][0:2]:
            entitydata.append(level[i])
            entitydata[-1] = entitydata[-1].split()
            entitydata[-1][1] = int(entitydata[-1][1])
            entitydata[-1] = tuple(entitydata[-1])
        else:
            break
    leveldata = level[len(entitydata) + 1:].copy()
    for index, row in enumerate(leveldata):
        leveldata[index] = row.split()
    return leveldata, entitydata, blocksize


def setup_leveldata(txt, num_3d_slices):
    leveldata, entitydata, blocksize = convert_txt_to_leveldata(txt)
    resize_textures(blocksize, num_3d_slices)
    spawnpoints, entity_list, camera_boundaries = [], [], None
    converted_leveldata = deepcopy(leveldata)
    for rowindex, row in enumerate(leveldata):  # convert strings to block class
        for itemindex, item in enumerate(row):
            converted_leveldata[rowindex][itemindex] = Block([itemindex * blocksize, rowindex * blocksize], item, blocksize)
            if item == "x":
                spawnpoints.append([itemindex * blocksize + blocksize / 2, rowindex * blocksize + blocksize / 2])
            elif item == "X":
                spawnpoints.insert(0, [itemindex * blocksize + blocksize / 2, rowindex * blocksize + blocksize / 2])
    converted_leveldata, endposavg, end_direction, end_hitboxes, lava_layer, bugfix_end_gradients = set_block_orientation(converted_leveldata, blocksize)
    for itemindex, item in enumerate(entitydata):
        entity_list.append(Player(spawnpoints[itemindex], [0, 0], playertypes[item[0]], item[1], item[2]))
    if not len(entitydata) == len(spawnpoints):
        raise Exception("level spawnpoint amount does not match number of players")
    if spawnpoints is not None and len(endposavg[0]) > 0:
        camera_boundaries = ((0, len(leveldata[0]) * blocksize - width), (0, len(leveldata) * blocksize - height))
        return converted_leveldata, spawnpoints, blocksize, entity_list, camera_boundaries, end_hitboxes, lava_layer, bugfix_end_gradients, end_direction
    elif spawnpoints is None:
        raise Exception("level has no spawnpoint")
    else:
        raise Exception("level has no end")


def set_border_offset(camera, borders):
    adjusted_camera = [camera[0], camera[1]]
    for i in range(2):
        if camera[i] < borders[i][0] + 300:
            if camera[i] >= borders[i][0] - 150:
                x = (450 - (camera[i] + 150))
                adjusted_camera[i] = camera[i] + 0.000001646 * pow(x, 3)
            else:
                adjusted_camera[i] = borders[i][0]
        elif camera[i] > borders[i][1] - 300:
            if camera[i] <= borders[i][1] + 150:
                x = (450 - abs(borders[i][1] + 150 - camera[i]))
                adjusted_camera[i] = camera[i] - 0.000001646 * pow(x, 3)
            else:
                adjusted_camera[i] = borders[i][1]
    return adjusted_camera


def killallplayers():
    entity_killed = False
    for entity in entities:
        entity_killed = True if (entity.alive and not entity.won) or entity_killed else False
        entity.die(False, True if entity.alive and not entity.won else False, 0 if not entity.won else 1)
    if entity_killed and sound_settings[0]:
        pygame.mixer.Sound.play(sound_library["kill_all_death"])


def unpause():
    global paused, pause_timer, pausedbuttons
    paused, pause_timer = False, 0
    pygame.mixer.unpause()
    pygame.mixer.music.unpause()
    for button in pausedbuttons:
        button.mouse_touching_timer, button.size_offset, button.texture = 0, 0.9, pygame.transform.scale(button.source_texture, (int(button.source_texture.get_width() * 0.9), int(button.source_texture.get_height() * 0.9)))


def drawnumber(number, position, scale=1):
    number, surface = str(number), []
    surface = pygame.Surface((117 + 117 * (len(number) - 1), 117), pygame.SRCALPHA)
    for index, i in enumerate(number):
        surface.blit(numbertextures[i], ((117 * scale_mult[0]) * index, 0))
    surface = pygame.transform.scale(surface, (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    res_scale_blit(surface, (position[0] - (surface.get_width()) / 2, position[1] - (surface.get_height()) / 2))


def resize_textures(blocksize, num_3d_slices):
    global block_textures, three_d_textures
    block_surfaces = [pygame.image.load("textures/solidspritesheet.png").convert(), pygame.image.load("textures/notstickyspritesheet.png").convert(), pygame.image.load("textures/spike.png").convert()]
    lava_surfaces = [pygame.image.load("textures/lava.png").convert(), pygame.Surface((200, 200)).convert(), pygame.Surface((200, 200)).convert()]
    three_d_surfaces = [pygame.image.load("textures/3Dtextures.png").convert(), pygame.Surface((106, 105)).convert(), pygame.Surface((106, 95)).convert(), pygame.Surface((106, 105)).convert(), pygame.Surface((100, 100)).convert()]
    endgradient = pygame.image.load("textures/endgradient.png").convert_alpha()
    for item in block_surfaces:
        item.set_colorkey((0, 0, 0))
    block_surfaces[0], block_surfaces[1] = [block_surfaces[0]], [block_surfaces[1]]
    for i in range(2):
        for j in range(47):
            block_surfaces[i].append(pygame.Surface((100, 100)))
            block_surfaces[i][len(block_surfaces[i]) - 1].blit(block_surfaces[i][0], (-1 + (-105 * j), -1))
            block_surfaces[i][len(block_surfaces[i]) - 1] = pygame.transform.scale(block_surfaces[i][len(block_surfaces[i]) - 1], (blocksize, blocksize))
        block_surfaces[i].pop(0)
    block_surfaces[2] = pygame.transform.scale(block_surfaces[2], (blocksize, blocksize))
    for i in range(2):
        lava_surfaces[i + 1].blit(lava_surfaces[0], ((-207 * i), 0 + (-1 * i)))
        lava_surfaces[i + 1] = pygame.transform.scale(lava_surfaces[i + 1], (blocksize, blocksize))
    for i in range(4):
        three_d_surfaces[i + 1].blit(three_d_surfaces[0], (-1 + (-110 * i), -1))
        three_d_surfaces[i + 1] = pygame.transform.scale(three_d_surfaces[i + 1], (blocksize, blocksize))
    endgradient = pygame.transform.scale(endgradient, (blocksize, blocksize))
    for item in three_d_surfaces:
        item.set_colorkey((0, 0, 0))
    three_d_surfaces.pop(0)
    lava_surfaces.pop(0)
    block_textures = {
        "solid": block_surfaces[0].copy(),
        "nonstickysolid": block_surfaces[1].copy(),
        "spike": {"up": pygame.transform.rotate(block_surfaces[2], 0),
                  "left": pygame.transform.rotate(block_surfaces[2], 90),
                  "down": pygame.transform.rotate(block_surfaces[2], 180),
                  "right": pygame.transform.rotate(block_surfaces[2], 270)},
        "lava": {"none": lava_surfaces[1].copy(),
                 "up": pygame.transform.rotate(lava_surfaces[0], 0),
                 "left": pygame.transform.rotate(lava_surfaces[0], 90),
                 "down": pygame.transform.rotate(lava_surfaces[0], 180),
                 "right": pygame.transform.rotate(lava_surfaces[0], 270)},
        "end": {"up": pygame.transform.rotate(endgradient, 0),
                "left": pygame.transform.rotate(endgradient, 90),
                "down": pygame.transform.rotate(endgradient, 180),
                "right": pygame.transform.rotate(endgradient, 270)},
    }

    three_d_textures = {
        "solid": [],
        "nonstickysolid": [],
        "spike": {"up": [],
                  "left": [],
                  "down": [],
                  "right": []},
        "lava": []
    }
    br_inc = [int(6 * (9 / num_3d_slices)), int(5 * (9 / num_3d_slices)), int(8 * (9 / num_3d_slices))]
    for i in range(num_3d_slices):
        three_d_textures["solid"].append(three_d_surfaces[0].get_at((0, 0)))
        three_d_textures["solid"][i] = (three_d_textures["solid"][i][0] - i * br_inc[0], three_d_textures["solid"][i][1] - i * br_inc[0], three_d_textures["solid"][i][2] - i * br_inc[0])
        three_d_textures["nonstickysolid"].append(three_d_surfaces[3].get_at((1, 1)))
        three_d_textures["nonstickysolid"][i] = (three_d_textures["nonstickysolid"][i][0] - i * br_inc[0], three_d_textures["nonstickysolid"][i][1] - i * br_inc[0], three_d_textures["nonstickysolid"][i][2] - i * br_inc[0])
        three_d_textures["lava"].append(three_d_surfaces[2].get_at((0, 0)))
        three_d_textures["lava"][i] = (three_d_textures["lava"][i][0] - i * br_inc[0], three_d_textures["lava"][i][1] - i * br_inc[0], three_d_textures["lava"][i][2] - i * br_inc[0])
    for itemindex, i in enumerate(("up", "left", "down", "right")):
        for j in range(num_3d_slices):
            three_d_textures["spike"][i].append(three_d_surfaces[1].copy())
            three_d_textures["spike"][i][j] = pygame.transform.rotate(three_d_textures["spike"][i][j], itemindex * 90)
            three_d_textures["spike"][i][j].fill((j * br_inc[1], j * br_inc[2], j * br_inc[2]), special_flags=BLEND_RGB_SUB)


def draw_entity_3d_and_trail(center, num_slices=7):
    adjusted_position = []
    for entity in entities:
        for i in entity.trail:
            i.draw()
    for index, entity in enumerate(entities):
        adjusted_position.append(entity.position)
        if entity.alive and not entity.won:
            adjusted_elasticity, adjusted_charge, extrusion = [entity.elasticity[0], entity.elasticity[1]], entity.charge[0] * (entity.size / 50), num_slices * 25
            if entity.grounded:
                try:
                    entity.transformed_texture = pygame.transform.scale(entity.source_texture, (int(entity.size + adjusted_elasticity[0] - adjusted_elasticity[1] + adjusted_charge + 2), int(entity.size - adjusted_elasticity[0] + adjusted_elasticity[1] + adjusted_charge * -1 + 2)))
                except ValueError:
                    entity.transformed_texture = pygame.transform.scale(entity.source_texture, (0, 0))
                if entity.landed_direction == "dowm":
                    entity.transformed_texture = pygame.transform.rotate(entity.transformed_texture, 0)
                elif entity.landed_direction == "up":
                    entity.transformed_texture = pygame.transform.rotate(entity.transformed_texture, 180)
                elif entity.landed_direction == "right":
                    entity.transformed_texture = pygame.transform.rotate(entity.transformed_texture, 90)
                elif entity.landed_direction == "left":
                    entity.transformed_texture = pygame.transform.rotate(entity.transformed_texture, 270)
                adjusted_position[index] = (entity.position[0] + (int(adjusted_elasticity[0] / 2) * (1 if entity.landed_direction == 'right' else -1)) + ((int(adjusted_charge / 2) * (1 if entity.landed_direction == 'right' else -1)) if entity.landed_direction == 'right' or entity.landed_direction == 'left' else 0),
                entity.position[1] - (int(adjusted_elasticity[1] / 2) * (1 if entity.landed_direction == 'down' else -1)) + ((int(adjusted_charge / 2) * (1 if entity.landed_direction == 'down' else -1)) if entity.landed_direction == 'down' or entity.landed_direction == 'up' else 0))
            else:
                entity.hyp = hyp(entity.position[0] - (entity.position[0] - entity.velocity[0]), entity.position[1] - (entity.position[1] - entity.velocity[1]))
                entity.hyp = (-31 * (entity.size / 50)) if entity.hyp < (-31 * (entity.size / 50)) else ((31 * (entity.size / 50)) if entity.hyp > (31 * (entity.size / 50)) else entity.hyp)
                try:
                    entity.transformed_texture = pygame.transform.scale(entity.source_texture, (int(entity.size * entity.spawn_animation[entity.spawn_timer] - entity.hyp + 2), int(entity.size * entity.spawn_animation[entity.spawn_timer] + entity.hyp + 2)))
                except ValueError:
                    entity.transformed_texture = pygame.transform.scale(entity.source_texture, (0, 0))
                try:
                    entity.transformed_texture = pygame.transform.rotate(entity.transformed_texture, atan((entity.position[0] - (entity.position[0] - entity.velocity[0])) / (entity.position[1] - (entity.position[1] - entity.velocity[1]))) * (180/pi))
                except ZeroDivisionError:
                    pass
            for i in range(num_slices - 1, -1, -1):
                drawobject(entity.transformed_texture, (adjusted_position[index][0] - ((adjusted_position[index][0] - center[0]) / extrusion) * (i + 1), adjusted_position[index][1] - ((adjusted_position[index][1] - center[1]) / extrusion) * (i + 1)), True)
    for index, entity in enumerate(entities):
        if entity.alive and not entity.won:
            drawobject(entity.transformed_texture, adjusted_position[index], True, None, None)
            if not entity.spawn_timer >= 11:
                entity.spawn_timer += 1


def get_mouse_pos():
    mousepos = pygame.mouse.get_pos()
    if scale:
        mousepos = (round(mousepos[0] / scale_mult[0]), round(mousepos[1] / scale_mult[1]))
    return mousepos


class Player:
    def __init__(self, position, velocity, playertype, size, gravity='down', temporary=False):
        self.position, self.velocity, self.type, self.color, self.source_texture, self.transformed_texture, self.size, self.hitbox, self.temporary = position, velocity, playertype[0], playertype[1], playertype[2], playertype[2], size, Rect(position[0], position[1], size - 1, size - 1), temporary
        self.elasticity = [0, 0]
        self.grounded = False
        self.impact = 0
        self.landed_direction, self.launched_velocity = gravity, velocity
        self.charge = [0, 0]
        self.launched_position = None
        self.gravity, self.default_gravity = gravity, gravity
        self.gravity_strength = 0.7
        self.air_resistance = 0.996
        self.mousedown = False
        self.airtime = 1 if self.temporary else 0
        self.hyp = 0
        self.alive = True
        self.won = False
        self.particles, self.trail = [], []
        self.tracer_texture = playertextures[0].copy()
        self.tracer_texture.set_colorkey((0, 0, 0))
        self.previous_position = position
        self.splice_adjustment = 0
        self.death_timer = 0
        self.spawn_timer = 11 if temporary else 0
        self.bounced = [False, False]
        self.spawn_animation = [0.1, 0.27, 0.42, 0.55, 0.65, 0.73, 0.81, 0.87, 0.92, 0.95, 0.97, 1]
        self.spawnpoint = position.copy()
        self.first_death = False
        self.abilityready = False
        self.spawn_death_particles = True
        self.touching_end = False

    def move_horizontal(self, level, blocksize):
        global ripples
        if not self.grounded:
            if self.gravity == "up" or self.gravity == "down" or self.gravity == "none":
                self.velocity[0] *= self.air_resistance
            else:
                self.velocity[0] += (self.gravity_strength if self.gravity == "right" else self.gravity_strength * -1)
            self.position[0] += self.velocity[0]
            self.align_hitbox()
            self.splice_adjustment = (self.size / blocksize) if (self.size / blocksize) > 1 else 1
            self.bounced[0] = False
            collision, touched_end, entity_collision = check_for_level_collisions(level, self.hitbox, [[round(self.position[0] / blocksize - self.splice_adjustment), round(self.position[0] / blocksize + self.splice_adjustment)], [round(self.position[1] / blocksize - self.splice_adjustment), round(self.position[1] / blocksize + self.splice_adjustment)]], False, True)
            if collision is not None and not self.grounded:
                self.mousedown = False
                if self.airtime == 0 and collision[1] in solids:
                    self.single_frame_impact_management()
                    stop_sound = True
                    for entity in entities:
                        if not entity.grounded:
                            stop_sound = False
                    if sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library[choice(["mediumimpact1", "mediumimpact2"] if abs(self.impact) < 8 else ["largeimpact1", "largeimpact2"])])
                        if stop_sound:
                            pygame.mixer.Sound.stop(sound_library["launch"])
                        pygame.mixer.Sound.stop(sound_library["charge"])
                        event_sound_triggers[0] = False
                elif collision[1] == "solid":
                    detectedbox = collision[0]
                    self.grounded, self.elasticity, self.impact = True, [abs(self.hyp) / -1.7, 0], round(abs(self.hyp) / 4)
                    if self.hitbox.right - detectedbox.left <= self.velocity[0] + 1:  # landed on left
                        self.gravity = 'right'
                        self.position, self.landed_direction = [detectedbox.x - (self.size / 2), self.position[1]], "right"
                    elif self.hitbox.left - detectedbox.right >= self.velocity[0] - 1:  # landed on right
                        self.gravity = 'left'
                        self.position, self.landed_direction = [detectedbox.x + blocksize + (self.size / 2), self.position[1]], "left"
                    if self.launched_position is not None:
                        self.position = self.launched_position.copy()
                    if self.type == "nogravity":
                        self.gravity = "none"
                    if graphics_settings[2]:
                        self.particles.extend(Particle.generate_particles("circle", abs(self.impact), [self.position[0], self.position[1]], (tuple(sorted([self.velocity[0] / -1.4, 0])), (abs(self.impact) * -0.9 + (self.velocity[1] * 0.15), abs(self.impact * 0.9) + (self.velocity[1] * 0.15))), 8 + abs(self.impact) * 1.3, self.color, self.gravity))
                    self.align_hitbox()
                    self.velocity = [0, 0]
                    self.abilityready = True
                    self.touching_end = False
                    self.previous_position = self.position.copy()
                    check_for_cheese = check_for_level_collisions(level, self.hitbox, [[round(self.position[0] / blocksize - self.splice_adjustment), round(self.position[0] / blocksize + self.splice_adjustment)], [round(self.position[1] / blocksize - self.splice_adjustment), round(self.position[1] / blocksize + self.splice_adjustment)]], True)
                    if check_for_cheese is not None and check_for_cheese[1] in hazards:
                        self.die(True)
                        self.grounded = False
                        if sound_settings[0]:
                            pygame.mixer.Sound.stop(sound_library["launch"])
                        if collision[1] == "lava":
                            ripples.extend([Ripple((int(collision[0].x / blocksize), int(collision[0].y / blocksize)), "up", self.impact * -0.6), Ripple((int(collision[0].x / blocksize), int(collision[0].y / blocksize)), "down", self.impact * -0.6)])
                            if sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["lava_death"])
                        elif sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["spike_death"])
                    elif sound_settings[0]:
                        stop_sound = True
                        for entity in entities:
                            if not entity.grounded:
                                stop_sound = False
                        pygame.mixer.Sound.play(sound_library[choice(["mediumimpact1", "mediumimpact2"] if abs(self.impact) < 8 else ["largeimpact1", "largeimpact2"])])
                        if stop_sound:
                            pygame.mixer.Sound.stop(sound_library["launch"])
                    grounded_entities.append(self)
                elif collision[1] == "nonstickysolid":
                    detectedbox, self.impact = collision[0], round(abs(self.hyp) / 4)
                    if self.hitbox.right - detectedbox.left < self.velocity[0] + 1:  # landed on left
                        self.position = [detectedbox.x - (self.size / 2), self.position[1]]
                    elif self.hitbox.left - detectedbox.right > self.velocity[0] - 1:  # landed on right
                        self.position = [detectedbox.x + blocksize + (self.size / 2), self.position[1]]
                    if graphics_settings[2]:
                        self.particles.extend(Particle.generate_particles("circle", abs(self.impact), [self.position[0], self.position[1]], (tuple(sorted([self.velocity[0] / -1.4, 0])), (abs(self.impact) * -0.9 + (self.velocity[1] * 0.15), abs(self.impact * 0.9) + (self.velocity[1] * 0.15))), 8 + abs(self.impact) * 1.3, self.color, self.gravity))
                    self.velocity, self.bounced[0], self.abilityready, self.mousedown = [self.velocity[0] * -1, self.velocity[1]], True, True, True
                    if sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["bounce"])
                elif collision[1] in hazards:
                    self.die(True)
                    if sound_settings[0]:
                        pygame.mixer.Sound.stop(sound_library["launch"])
                    if collision[1] == "lava":
                        ripples.extend([Ripple((int(collision[0].x / blocksize), int(collision[0].y / blocksize)), "up", self.impact * -0.6), Ripple((int(collision[0].x / blocksize), int(collision[0].y / blocksize)), "down", self.impact * -0.6)])
                        if sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["lava_death"])
                    elif sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["spike_death"])
            elif touched_end:
                self.touching_end = True
            if collision is None and entity_collision is not None:
                bounced, detectedbox, self.impact = False, entity_collision[0], round(abs(self.hyp) / 4)
                if entity_collision[1] == "right" or (entity_collision[1] in ("up", "down") and self.hitbox.right - detectedbox.left < self.velocity[0] + detectedbox.w / 2):  # landed on left
                    self.position, bounced = [detectedbox.x - (self.size / 2), self.position[1]], True
                elif entity_collision[1] == "left" or (entity_collision[1] in ("up", "down") and self.hitbox.left - detectedbox.right > self.velocity[0] - detectedbox.w / 2):  # landed on right
                    self.position, bounced = [detectedbox.x + detectedbox.w + (self.size / 2), self.position[1]], True
                if bounced:
                    if graphics_settings[2]:
                        self.particles.extend(Particle.generate_particles("circle", abs(self.impact), [self.position[0], self.position[1]], (tuple(sorted([self.velocity[0] / -1.4, 0])), (abs(self.impact) * -0.9 + (self.velocity[1] * 0.15), abs(self.impact * 0.9) + (self.velocity[1] * 0.15))), 8 + abs(self.impact) * 1.3, self.color, self.gravity))
                    self.velocity, self.bounced[0], self.abilityready, self.mousedown = [self.velocity[0] * -1, self.velocity[1]], True, True, True
                    if sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["bounce"])

    def move_vertical(self, level, blocksize):
        global ripples
        if not self.grounded and self.alive and not self.won:
            if self.gravity == "up" or self.gravity == "down":
                self.velocity[1] += (self.gravity_strength if self.gravity == "down" else self.gravity_strength * -1)
            else:
                self.velocity[1] *= self.air_resistance
            self.position[1] += self.velocity[1]
            self.align_hitbox()
            self.bounced[1] = False
            self.trail.extend(Particle.generate_particles("trail", 1, (tuple(self.position), tuple(self.previous_position)), ((0, 0), (0, 0)), self.size / 2.3, self.color, "none", False, 0.8))
            collision, touched_end, entity_collision = check_for_level_collisions(level, self.hitbox, [[round(self.position[0] / blocksize - self.splice_adjustment), round(self.position[0] / blocksize + self.splice_adjustment)], [round(self.position[1] / blocksize - self.splice_adjustment), round(self.position[1] / blocksize + self.splice_adjustment)]], False, True)
            if collision is not None and not self.grounded:
                self.mousedown = False
                if self.airtime == 0 and collision[1] in solids:
                    self.single_frame_impact_management()
                    stop_sound = True
                    for entity in entities:
                        if not entity.grounded:
                            stop_sound = False
                    if sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library[choice(["mediumimpact1", "mediumimpact2"] if abs(self.impact) < 8 else ["largeimpact1", "largeimpact2"])])
                        if stop_sound:
                            pygame.mixer.Sound.stop(sound_library["launch"])
                        pygame.mixer.Sound.stop(sound_library["charge"])
                    event_sound_triggers[0] = False
                elif collision[1] == "solid":
                    detectedbox = collision[0]
                    self.grounded, self.elasticity, self.impact = True, [0, abs(self.hyp) / 1.7], round(abs(self.hyp) / 4 * -1)
                    if self.hitbox.bottom - detectedbox.top <= self.velocity[1] + 1:  # landed on top
                        self.gravity = 'down'
                        self.position, self.landed_direction = [self.position[0], detectedbox.y - (self.size / 2)], 'down'
                    elif self.hitbox.top - detectedbox.bottom >= self.velocity[1] - 1:  # landed on bottom
                        self.gravity = 'up'
                        self.position, self.landed_direction = [self.position[0], detectedbox.y + blocksize + (self.size / 2)], 'up'
                    if self.launched_position is not None:
                        self.position = self.launched_position.copy()
                    if self.type == "nogravity":
                        self.gravity = "none"
                    if graphics_settings[2]:
                        self.particles.extend(Particle.generate_particles("circle", abs(self.impact), [self.position[0], self.position[1]], ((abs(self.impact) * -0.9 + (self.velocity[0] * 0.15), abs(self.impact * 0.9) + (self.velocity[0] * 0.15)), tuple(sorted([self.velocity[1] / -1.4, 0]))), 8 + abs(self.impact) * 1.3, self.color, self.gravity))
                    self.align_hitbox()
                    self.velocity = [0, 0]
                    self.abilityready = True
                    self.touching_end = False
                    self.previous_position = self.position.copy()
                    check_for_cheese = check_for_level_collisions(level, self.hitbox, [[round(self.position[0] / blocksize - self.splice_adjustment), round(self.position[0] / blocksize + self.splice_adjustment)], [round(self.position[1] / blocksize - self.splice_adjustment), round(self.position[1] / blocksize + self.splice_adjustment)]], True)
                    if check_for_cheese is not None and check_for_cheese[1] in hazards:
                        self.die(True)
                        self.grounded = False
                        if sound_settings[0]:
                            pygame.mixer.Sound.stop(sound_library["launch"])
                        if collision[1] == "lava":
                            ripples.extend([Ripple((int(collision[0].x / blocksize) + 1, int(collision[0].y / blocksize)), "right", self.impact * -0.6), Ripple((int(collision[0].x / blocksize), int(collision[0].y / blocksize)), "left", self.impact * -0.6)])
                            if sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["lava_death"])
                        elif sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["spike_death"])
                    elif sound_settings[0]:
                        stop_sound = True
                        for entity in entities:
                            if not entity.grounded:
                                stop_sound = False
                        pygame.mixer.Sound.play(sound_library[choice(["mediumimpact1", "mediumimpact2"] if abs(self.impact) < 8 else ["largeimpact1", "largeimpact2"])])
                        if stop_sound:
                            pygame.mixer.Sound.stop(sound_library["launch"])
                    grounded_entities.append(self)
                elif collision[1] == "nonstickysolid":
                    detectedbox, self.impact = collision[0], round(abs(self.hyp) / 4 * -1)
                    if self.hitbox.bottom - detectedbox.top < self.velocity[1] + 1:  # landed on top
                        self.position = [self.position[0], detectedbox.y - (self.size / 2)]
                    elif self.hitbox.top - detectedbox.bottom > self.velocity[1] - 1:  # landed on bottom
                        self.position = [self.position[0], detectedbox.y + blocksize + (self.size / 2)]
                    if graphics_settings[2]:
                        self.particles.extend(Particle.generate_particles("circle", abs(self.impact), [self.position[0], self.position[1]], ((abs(self.impact) * -0.9 + (self.velocity[0] * 0.15), abs(self.impact * 0.9) + (self.velocity[0] * 0.15)), tuple(sorted([self.velocity[1] / -1.4, 0]))), 8 + abs(self.impact) * 1.3, self.color, self.gravity))
                    self.velocity, self.bounced[1], self.abilityready, self.mousedown = [self.velocity[0], self.velocity[1] * -1], True, True, True
                    if sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["bounce"])
                elif collision[1] in hazards:
                    self.die(True)
                    if sound_settings[0]:
                        pygame.mixer.Sound.stop(sound_library["launch"])
                    if collision[1] == "lava":
                        ripples.extend([Ripple((int(collision[0].x / blocksize) + 1, int(collision[0].y / blocksize)), "right", self.impact * -0.6), Ripple((int(collision[0].x / blocksize), int(collision[0].y / blocksize)), "left", self.impact * -0.6)])
                        if sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["lava_death"])
                    elif sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["spike_death"])
            elif touched_end:
                self.touching_end = True
            if collision is None and entity_collision is not None:
                bounced, detectedbox, self.impact = False, entity_collision[0], round(abs(self.hyp) / 4 * -1)
                if entity_collision[1] == "down" or (entity_collision[1] in ("right", "left") and self.hitbox.bottom - detectedbox.top < self.velocity[1] + detectedbox.w / 2):  # landed on top
                    self.position, bounced = [self.position[0], detectedbox.y - (self.size / 2)], True
                elif entity_collision[1] == "up" or (entity_collision[1] in ("right", "left") and self.hitbox.top - detectedbox.bottom > self.velocity[1] - detectedbox.w / 2):  # landed on bottom
                    self.position, bounced = [self.position[0], detectedbox.y + detectedbox.h + (self.size / 2)], True
                if bounced:
                    if graphics_settings[2]:
                        self.particles.extend(Particle.generate_particles("circle", abs(self.impact), [self.position[0], self.position[1]], ((abs(self.impact) * -0.9 + (self.velocity[0] * 0.15), abs(self.impact * 0.9) + (self.velocity[0] * 0.15)), tuple(sorted([self.velocity[1] / -1.4, 0]))), 8 + abs(self.impact) * 1.3, self.color, self.gravity))
                    self.velocity, self.bounced[1], self.abilityready, self.mousedown = [self.velocity[0], self.velocity[1] * -1], True, True, True
                    if sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["bounce"])
            if collision is None and self.launched_position is not None:
                self.launched_position = None
            self.airtime += 1
            self.previous_position = self.position.copy()

    def check_border_events(self, borders, end_hitboxes):
        borders = [list(borders[0]), list(borders[1])]
        borders[0][1], borders[1][1] = borders[0][1] + width, borders[1][1] + height
        if (self.position[0] < borders[0][0] - blocksize * 2) or (self.position[0] > borders[0][1] + blocksize * 2) or (self.position[1] < borders[1][0] - blocksize * 2) or (self.position[1] > borders[1][1] + blocksize * 2):
            self.position, self.gravity = ([borders[0][0] - blocksize * 2, self.position[1]], "left") if (self.position[0] < borders[0][0] - blocksize * 2) else ([borders[0][1] + blocksize * 2, self.position[1]], "right") if (self.position[0] > borders[0][1] + blocksize * 2) else ([self.position[0], borders[1][0] - blocksize * 2], "up") if (self.position[1] < borders[1][0] - blocksize * 2) else ([self.position[0], borders[1][1] + blocksize * 2], "down")
            self.align_hitbox()
            did_i_won = False
            for hitbox in end_hitboxes:
                if self.hitbox.colliderect(hitbox):
                    did_i_won = True
            if did_i_won or self.touching_end:
                self.won = True
                return "won"
            else:
                self.die(True)
                if sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library["kill_all_death"])

    def single_frame_impact_management(self):
        self.hyp = hyp(self.position[0] - (self.position[0] - self.velocity[0]), self.position[1] - (self.position[1] - self.velocity[1]))
        self.position, self.grounded = self.previous_position.copy(), True
        if self.landed_direction == "down" or self.landed_direction == "up":
            self.elasticity, self.impact = [0, abs(self.hyp) / 1.7], round(abs(self.hyp) / 4 * -1)
        else:
            self.elasticity, self.impact = [abs(self.hyp) / -1.7, 0], round(abs(self.hyp) / 4)
        self.velocity = [0, 0]
        self.align_hitbox()

    def idle_iterations(self):
        if not self.elasticity == [0, 0]:
            if self.elasticity[1] == 0:
                self.impact += 1 if self.elasticity[0] < 0 else -1
                if abs(self.elasticity[0]) <= abs(self.impact):
                    self.impact += (self.size / 50) if self.impact < 0 else (self.size / -50)
                if abs(self.elasticity[0]) <= 1 and self.impact == 0:
                    self.elasticity = [0, 0]
                self.elasticity[0] = self.elasticity[0] + self.impact
            else:
                self.impact += 1 if self.elasticity[1] < 0 else -1
                if abs(self.elasticity[1]) <= abs(self.impact):
                    self.impact += (self.size / 50) if self.impact < 0 else (self.size / -50)
                if abs(self.elasticity[1]) <= 1 and self.impact == 0:
                    self.elasticity = [0, 0]
                self.elasticity[1] = self.elasticity[1] + self.impact
            if round(self.impact) == 0 and (round(self.elasticity[0]), round(self.elasticity[1])) == (0, 0):
                self.elasticity, self.impact = [0, 0], 0

    def calculate_launch(self, mousepos):
        if self.charge[0] < 8:
            self.charge = [8, self.charge[1]]
        self.launched_position = self.position.copy()
        a, b = (mousepos[0] - self.hitbox.x), (mousepos[1] - self.hitbox.y)
        mod = hyp(a, b) / (self.charge[0] * math.sqrt(self.size / 50))
        self.grounded = False
        self.airtime = 0
        self.velocity = [a / mod * 0.8, b / mod * 0.8] if self.gravity == "none" else [a / mod, b / mod]
        self.launched_velocity = self.velocity.copy()
        self.charge = [0, 0]
        self.abilityready = True
        power = hyp(self.velocity[0], self.velocity[1])
        if self.landed_direction == "down" or self.landed_direction == "up":
            self.particles.extend(Particle.generate_particles("circle", abs(power / 6), [self.position[0], self.position[1]], ((power / -3, power / 3), tuple(sorted([self.velocity[1] / 2, 0]))), randint(int(power / 3), 8 + int(power / 4)), self.color, self.gravity))
        else:
            self.particles.extend(Particle.generate_particles("circle", abs(power / 6), [self.position[0], self.position[1]], (tuple(sorted([self.velocity[0] / 2, 0])), (power / -3, power / 3)), randint(int(power / 3), 8 + int(power / 4)), self.color, self.gravity))

    def predict_the_future(self, level, mousepos, iterations=20, blocksize=50):
        if self.grounded and self.charge[0] > 0:
            a, b = (mousepos[0] - self.hitbox.x), (mousepos[1] - self.hitbox.y)
            mod = hyp(a, b) / (self.charge[0] * math.sqrt(self.size / 50))
            trackedcoords = []
            pos, vel = self.position.copy(), [a / mod * 0.8, b / mod * 0.8] if self.gravity == "none" else [a / mod, b / mod]
            for a in range(iterations):
                if check_for_level_collisions(level, Rect(pos[0] - 5, pos[1] - 5, 10, 10), [[round(pos[0] / blocksize - 1), round(pos[0] / blocksize) + 1], [round(pos[1] / blocksize - 1), round(pos[1] / blocksize + 1)]]) and not a == 0:
                    break
                for _ in range(3):
                    if self.gravity == "up" or self.gravity == "down" or self.gravity == "none":
                        vel[0] *= self.air_resistance
                    else:
                        vel[0] += (self.gravity_strength if self.gravity == "right" else self.gravity_strength * -1)
                    if self.gravity == "up" or self.gravity == "down":
                        vel[1] += (self.gravity_strength if self.gravity == "down" else self.gravity_strength * -1)
                    else:
                        vel[1] *= self.air_resistance
                    pos = [pos[0] + vel[0], pos[1] + vel[1]]
                trackedcoords.append(pos)
            return trackedcoords
        else:
            return []

    def process_user_inputs(self, mousepos, mousedown):
        if mousedown[0] and not self.mousedown:
            self.mousedown = True
            if self.grounded:
                self.charge = [0, 1.12]
            elif self.abilityready and self.type not in ("normal", "nogravity"):
                if sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library["ability"])
                if self.type == "doublejump":
                    self.velocity = [(self.launched_velocity[0] * 0.9) if self.gravity == "right" or self.gravity == "left" else self.velocity[0], (self.launched_velocity[1] * 0.9) if self.gravity == "up" or self.gravity == "down" else self.velocity[1]]
                if self.type == "gravityswitch":
                    self.gravity = ("down" if self.gravity == "up" else "up") if self.gravity == "down" or self.gravity == "up" else ("right" if self.gravity == "left" else "left")
                if self.type == "groundpound":
                    self.velocity = [(20 if self.gravity == "right" else -20) if self.gravity == "right" or self.gravity == "left" else self.velocity[0], (20 if self.gravity == "down" else -20) if self.gravity == "up" or self.gravity == "down" else self.velocity[1]]
                if self.type == "mitosis":
                    try:
                        slope = (-1 / (self.velocity[1] / self.velocity[0]) if not self.velocity[0] == 0 else 0).as_integer_ratio()
                    except ZeroDivisionError:
                        slope = (-1, 0)
                    ratio = math.sqrt(pow(slope[0], 2) + pow(slope[1], 2)) / hyp(self.launched_velocity[0], self.launched_velocity[1])
                    slope = slope[0] / ratio, slope[1] / ratio
                    self.velocity = [slope[1] * 0.9, slope[0] * 0.9]
                    entities.append(Player([self.position[0] + self.velocity[0], self.position[1]], [self.velocity[0] * -1, self.velocity[1] * -1], playertypes[self.type], self.size, self.gravity, True))
                    self.position = [self.position[0] - self.velocity[0], self.position[1]]
                self.abilityready = False
                hyp_mod = (self.hyp if not self.type == "doublejump" else (hyp(self.velocity[0], self.velocity[1]))) * 0.8
                particle_mod = (randint(7, 9), randint(int(hyp_mod / 1.5), 8 + int(hyp_mod / 2)), 1) if not self.type == "mitosis" else (randint(8, 10), randint(8 + int(hyp_mod / 2), 14 + int(hyp_mod / 2)), 2)
                if self.gravity == "down" or self.gravity == "up":
                    self.particles.extend(Particle.generate_particles("circle", particle_mod[0], [self.position[0], self.position[1]], ((hyp_mod / -3 * particle_mod[2], hyp_mod / 3 * particle_mod[2]), tuple(sorted([self.velocity[1] / 2 * particle_mod[2], 0]))), particle_mod[1], self.color, self.gravity))
                else:
                    self.particles.extend(Particle.generate_particles("circle", particle_mod[0], [self.position[0], self.position[1]], (tuple(sorted([self.velocity[0] / 2 * particle_mod[2], 0])), (hyp_mod / -3 * particle_mod[2], hyp_mod / 3 * particle_mod[2])), particle_mod[1], self.color, self.gravity))
        elif mousedown[0]:
            if self.grounded:
                self.charge = [self.charge[0] + self.charge[1], self.charge[1] * 0.96]
        elif not mousedown[0] and self.mousedown:
            self.mousedown = False
            if self.grounded:
                self.calculate_launch([mousepos[0] - (self.size / 2), mousepos[1] - (self.size / 2)])

    def align_hitbox(self):
        self.hitbox.x, self.hitbox.y = round(self.position[0] - (self.size / 2)), round(self.position[1] - (self.size / 2))

    def die(self, first_death, spawn_death_particles=True, timerset=0):
        global global_death_timer
        self.alive, self.death_timer, self.impact, self.first_death, self.spawn_death_particles, self.won, self.abilityready = False, timerset, int(self.hyp) if spawn_death_particles else 0, first_death if len(entities) > 1 else False, spawn_death_particles, False, False
        global_death_timer = 0 if spawn_death_particles else global_death_timer
        if spawn_death_particles and graphics_settings[2]:
            if self.gravity == "up" or self.gravity == "down":
                self.particles.extend(Particle.generate_particles("circle", abs(self.hyp / 1.7), [self.position[0], self.position[1]], ((abs(self.hyp / 3) * -0.9 + (self.velocity[0] * 0.2), abs(self.hyp / 3) + (self.velocity[0] * 0.2)), tuple(sorted([self.hyp / (-0.7 if self.gravity == "down" else 0.7), 0]))), 12 + abs(self.hyp / 6), (self.color[0] * 1.15, self.color[1] * 1.15, self.color[2] * 1.15), self.gravity, False, 0.3, True))
                self.particles.extend(Particle.generate_particles("circle", randint(3, 5), [self.position[0], self.position[1]], ((self.hyp / -6, self.hyp / 6), tuple(sorted([10 / (-1 if self.gravity == "down" else 1), 0]))), self.size / 1.5, (self.color[0] * 1.15, self.color[1] * 1.15, self.color[2] * 1.15), self.gravity, True, 1, True))
            elif self.gravity == "right" or self.gravity == "left":
                self.particles.extend(Particle.generate_particles("circle", abs(self.hyp / 1.7), [self.position[0], self.position[1]], (tuple(sorted([self.hyp / (-0.7 if self.gravity == "right" else 0.7), 0])), (abs(self.hyp / 3) * -0.9 + (self.velocity[1] * 0.2), abs(self.hyp / 3) + (self.velocity[1] * 0.2))), 12 + abs(self.hyp / 6), (self.color[0] * 1.15, self.color[1] * 1.15, self.color[2] * 1.15), self.gravity, False, 0.3, True))
                self.particles.extend(Particle.generate_particles("circle", randint(3, 5), [self.position[0], self.position[1]], (tuple(sorted([10 / (-1 if self.gravity == "right" else 1), 0])), (self.hyp / -6, self.hyp / 6)), self.size / 1.5, (self.color[0] * 1.15, self.color[1] * 1.15, self.color[2] * 1.15), self.gravity, True, 1, True))
            elif self.gravity == "none":
                self.particles.extend(Particle.generate_particles("circle", abs(self.hyp / 1.7), [self.position[0], self.position[1]], (tuple(sorted([self.hyp / -1.2, self.hyp / 1.2])), tuple(sorted([self.hyp / -1.2, self.hyp / 1.2]))), 12 + abs(self.hyp / 6), (self.color[0] * 1.15, self.color[1] * 1.15, self.color[2] * 1.15), self.gravity, False, 0.3, True))
                self.particles.extend(Particle.generate_particles("circle", randint(3, 5), [self.position[0], self.position[1]], (tuple(sorted([self.hyp / -4, self.hyp / 4])), tuple(sorted([self.hyp / -4, self.hyp / 4]))), self.size / 1.5, (self.color[0] * 1.15, self.color[1] * 1.15, self.color[2] * 1.15), self.gravity, True, 1, True))

    def death_cooldown(self):
        if self.death_timer == 20 and self.first_death:
            killallplayers()
        self.death_timer += 1
        if self.death_timer == 60:
            self.alive, self.velocity, self.position, self.previous_position, self.gravity, self.impact, self.spawn_timer, self.airtime, self.grounded, self.mousedown, self.elasticity, self.charge = True, [0, 0], self.spawnpoint.copy(), self.spawnpoint.copy(), self.default_gravity, 0, 0, 4, False, False, [0, 0], [0, 0]


class Particle:
    def __init__(self, particle_type, surface, position, velocity, size, gravity, decay_rate=0.3, flash=False):
        if str(type(surface)) == "<class 'tuple'>":
            color_brightness_mod = randint(-7, 7)
            self.texture_type, self.color = "color", (surface[0] + color_brightness_mod, surface[1] + color_brightness_mod, surface[2] + color_brightness_mod) if not particle_type == "trail" else surface
            self.color = tuple(map(lambda x: x if x < 255 else 255, self.color))
            if flash:
                self.age = 13
            else:
                self.age = 0
        else:
            self.texture_type, self.texture, self.source_texture, self.scale = "texture", surface, surface, size / 10
            self.texture = pygame.transform.scale(self.texture, (int(self.texture.get_width() * self.scale), int(self.texture.get_height() * self.scale)))
        self.particle_type, self.position, self.velocity, self.size, self.gravity, self.decay_rate = particle_type, position, tuple(velocity), size, gravity, decay_rate

    def set_scale(self, randrange=(0.5, 1)):
        self.scale = randint(randrange[0], randrange[1])

    def draw(self):
        if self.texture_type == "color":
            if self.particle_type == "circle" or self.particle_type == "environmental":
                adjusted_color = self.color if self.age == 0 else (self.color[0] + self.age * 20, self.color[1] + self.age * 20, self.color[2] + self.age * 20)
                pygame.draw.circle(win, tuple(map(lambda x: x if x < 255 else 255, adjusted_color)), ((self.position[0] - camera[0] - camera_shake[0]) * scale_mult[0], (self.position[1] - camera[1] - camera_shake[1]) * scale_mult[1]), self.size)
            elif self.particle_type == "trail":
                pygame.draw.line(win, self.color, ((self.position[0][0] - camera[0] - camera_shake[0]) * scale_mult[0], (self.position[0][1] - camera[1] - camera_shake[1]) * scale_mult[1]), ((self.position[1][0] - camera[0] - camera_shake[0]) * scale_mult[0], (self.position[1][1] - camera[1] - camera_shake[1]) * scale_mult[1]), width=int(self.size))
        else:
            res_scale_blit(self.texture, (self.position[0] - camera[0] - camera_shake[0] - self.size / 2, self.position[1] - camera[1] - camera_shake[1] - self.size / 2))

    def iterate(self, gravity_strength, air_resistance):
        if self.particle_type == "circle":
            if self.gravity == "up" or self.gravity == "down":
                self.velocity = (self.velocity[0] * air_resistance, self.velocity[1] + (gravity_strength if self.gravity == "down" else gravity_strength * -1))
            elif self.gravity == "right" or self.gravity == "left":
                self.velocity = (self.velocity[0] + (gravity_strength if self.gravity == "right" else gravity_strength * -1), self.velocity[1] * air_resistance)
            else:
                self.velocity = (self.velocity[0] * air_resistance, self.velocity[1] * air_resistance)
            self.position = [self.position[0] + self.velocity[0], self.position[1] + self.velocity[1]]
            if flash and not self.age == 0:
                self.age -= 1
        elif self.particle_type == "environmental":
            self.position = (self.position[0] + self.velocity[0] * self.scale, self.position[1] + self.velocity[1] * self.scale)
        if not self.particle_type == "environmental":
            self.size -= self.decay_rate

    @staticmethod
    def generate_particles(particle_type, count, position, velocity, size, color=(0, 0, 0), gravity="down", random=True, decay_rate=0.3, flash=False):
        queued_particles = []
        if random:
            for _ in range(randint(int(count / 2), int(count * 1.5))):
                queued_particles.append(Particle(particle_type, color, [position[0], position[1]], [randint(int(velocity[0][0]) * 10, int(velocity[0][1]) * 10) / 10, randint(int(velocity[1][0]) * 10, int(velocity[1][1]) * 10) / 10], randint(int(size / 1.3), int(size * 1.3)), gravity, decay_rate, flash))
        else:
            for _ in range(int(count)):
                queued_particles.append(Particle(particle_type, (color[0] * 0.95, color[1] * 0.95, color[2] * 0.95), [position[0], position[1]], [randint(int(velocity[0][0]), int(velocity[0][1])), randint(int(velocity[1][0]), int(velocity[1][1]))], size, gravity, decay_rate, flash))
        return queued_particles


class Ripple:
    def __init__(self, position, direction, power):
        self.position, self.direction, self.power = position, direction, power if power > -18 else -18

    def iterate(self):
        self.position = (self.position[0] + ((1 if self.direction == "right" else -1) if self.direction == "right" or self.direction == "left" else 0),
                         self.position[1] + ((1 if self.direction == "down" else -1) if self.direction == "up" or self.direction == "down" else 0))
        self.power += 0.4


mode, submode, playing_level, intro_timer = "menu", "intro", 1, 0
run = True
clock = pygame.time.Clock()

# set up level
# I know i can just use the setup_level() function, but pycharm keeps giving me errors and it's really annoying
level, spawnpoint, blocksize, entities, camera_boundaries, end_hitboxes, lava_layer, bugfix_end_gradients, end_direction = setup_leveldata(open("leveldata/level1", "r").read(), num_3d_slices)
spawnpoint = spawnpoint[0].copy()
bg_slices, lava_timer, keystrokes = 2, 0, {"x": False, "z": False, "esc": False, "right": False, "left": False, "up": False, "down": False, "d": False, "a": False, "w": False, "s": False}
camera, camera_shake, camera_shake_power, camera_shake_timer, camera_ease, camera_non_offset_coords, focus, victory, victory_timer = ((entities[0].position[0] - width / 2), (entities[0].position[1] - height / 2)), (0, 0), (0, 0), 0, (0, 0), ((entities[0].position[0] - width / 2), (entities[0].position[1] - height / 2)), 0, False, 0
background_robots, sparks, lava_particles, ripples = [], [], [], []
winbuttons, paused = [Button(winbuttontextures[0], (width / 2, height / 2), 0.8, [0, 0], True), Button(winbuttontextures[1], (width / 2 - 290, height * 0.7), 0.76, [0, 660]), Button(winbuttontextures[2], (width / 2, height * 0.7), 0.76, [0, 660]), Button(winbuttontextures[3], (width / 2 + 290, height * 0.7), 0.76, [0, 660])], False
pausedbuttons, editorbuttons = [Button(pausetextures[0], (width / 2, height / 2), 0.8, [0, 0], True), Button(pausetextures[1], (width / 2, 540), 0.7, [0, 0], False), Button(pausetextures[2], (width / 2, 585), 0.7, [0, 0], False), Button(pausetextures[3], (width / 2, 630), 0.7, [0, 0], False), Button(pausetextures[4], (width / 2, 675), 0.7, [0, 0], False), Button(pausetextures[5], (width / 2, 720), 0.7, [0, 0], False)], [[], []]
editorsettingsbuttons = [Button(editorsettingstextures[0], (width / 2, 32), 0.8, [0, 0], True), Button(arrowtextures[0], (540, 32), 0.8, [0, 0], False), Button(arrowtextures[1], (660, 32), 0.8, [0, 0], False), Button(arrowtextures[0], (990, 32), 0.8, [0, 0], False), Button(arrowtextures[1], (1100, 32), 0.8, [0, 0], False), Button(arrowtextures[0], (1455, 32), 0.8, [0, 0], False), Button(arrowtextures[1], (1575, 32), 0.8, [0, 0], False)]
menubuttons = [Button(menubuttontextures[0], (width / 2, 295), 0.67, [0, 0], True), Button(menubuttontextures[1], (width / 2, 585), 0.67, [0, 0]), Button(menubuttontextures[2], (width / 2, 692), 0.67, [0, 0]), Button(menubuttontextures[4], (width / 2, 799), 0.67, [0, 0]), Button(menubuttontextures[7], (width / 2, 906), 0.67, [0, 0])]
backbutton = Button(menubuttontextures[6], (175, 1020), 0.67, [0, 0])
settingsbuttons = [Button(settingswordstextures[8], (width / 2, 720), 0.67, [0, 0]), Button(arrowtextures[0], (width / 2 - 160, 517), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 - 40, 517), 0.67, [0, 0]), Button(arrowtextures[0], (width / 2 - 160, 557), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 - 40, 557), 0.67, [0, 0]), Button(arrowtextures[0], (width / 2 - 160, 597), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 - 40, 597), 0.67, [0, 0]), Button(arrowtextures[0], (width / 2 - 160, 637), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 - 40, 637), 0.67, [0, 0]), Button(arrowtextures[0], (width / 2 - 160, 677), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 - 40, 677), 0.67, [0, 0]),
                   Button(arrowtextures[0], (width / 2 + 220, 577), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 + 333, 577), 0.67, [0, 0]), Button(arrowtextures[0], (width / 2 + 220, 617), 0.67, [0, 0]), Button(arrowtextures[1], (width / 2 + 333, 617), 0.67, [0, 0])]
menu_transition_timer, button_clicked, help_offset = ["forward", 0], None, 0
global_death_timer = 11

levelbuttons = []
for i in range(4):
    for j in range(5):
        levelbuttons.append(Button(menubuttontextures[5], (520 + j * 220, 440 + i * 165), 0.77, [0, 0]))  # 450 160
buttonsheldtimer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
menu_timer = 0

for i in range(7):
    editorbuttons[0].append(Button(editorbuttontextures[i], (60, 60 + i * 85), 0.7, [0, 0]))
for i in range(3):
    editorbuttons[1].append(Button(editorbuttontextures[i + 7], (60, 1020 - i * 85), 0.7, [0, 0]))
pause_timer = 0
for _ in range(13):
    background_robots.append(Particle("environmental", environmental_particle_surfaces[randint(0, 3)], (randint(0, width), randint(int(height * 0.3), int(height * 0.7))), (0.23, 0), randint(5, 10), None))

while run:
    keys = pygame.key.get_pressed()
    mouse, mousepos = pygame.mouse.get_pressed(), get_mouse_pos()
    if mode == "play":
        # set variables
        mousepos = (mousepos[0] + camera[0] + (entities[focus].position[0] - camera[0] - camera_shake[0] - width / 2),
                    mousepos[1] + camera[1] + (entities[focus].position[1] - camera[1] - camera_shake[1] - height / 2))
        player_event = None
        grounded_entities = list(filter(lambda x: x.grounded, entities))
        # run calculations
        if not paused:
            lava_timer = (lava_timer + 1) if lava_timer < 79 else 0
            if global_death_timer < 11:
                global_death_timer += 1
            for i, entity in enumerate(entities):
                if entity.alive and not entity.won and entity.spawn_timer > 6:
                    entity.move_horizontal(level, blocksize)
                    entity.move_vertical(level, blocksize)
                    if entity.grounded:
                        entity.idle_iterations()
                        if entity.charge[0] == 0 and not entity.charge[1] == 0 and not event_sound_triggers[0]:
                            event_sound_triggers[0] = True
                            if sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["charge"])
                    else:
                        if entity.airtime == 1:
                            if entity.spawn_timer == 11 and sound_settings[0]:
                                pygame.mixer.Sound.stop(sound_library["charge"])
                                pygame.mixer.Sound.stop(sound_library["launch"])
                                pygame.mixer.Sound.play(sound_library["launch"])
                                event_sound_triggers[0] = False
                            elif i == 0 and sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["spawn"])
                        if player_event is None:
                            player_event = entity.check_border_events(camera_boundaries, end_hitboxes)
                        else:
                            entity.check_border_events(camera_boundaries, end_hitboxes)
                elif not entity.alive:
                    if entity.spawn_timer > 6:
                        if entity.death_timer == 0:
                            camera_shake_power = [camera_shake_power[0] + (2 + entity.impact * 3), camera_shake_power[1] + (2 + entity.impact * 3)]
                            camera_shake_timer = 1
                        elif entity.death_timer == 58:
                            focus = 0
                            event_sound_triggers[1] = False
                            if i == 0:
                                entity_list_copy = list(reversed(entities)).copy()
                                for index, j in enumerate(entity_list_copy):
                                    if j.temporary:
                                        entities.pop(len(entity_list_copy) - index - 1)
                                if sound_settings[0]:
                                    pygame.mixer.Sound.play(sound_library["spawn"])
                        entity.death_cooldown()
            if keys[K_r] and entities[0].alive and entities[0].spawn_timer > 10:
                killallplayers()
            for entity in entities:  # delete dead particles from list
                particle_list_copy = [list(reversed(entity.particles)).copy(), list(reversed(entity.trail)).copy()]
                for i, particle_list in enumerate(particle_list_copy):
                    for j, particle in enumerate(particle_list):
                        if particle.size > 0:
                            particle.iterate(entity.gravity_strength, entity.air_resistance)
                        else:
                            if i == 0:
                                entity.particles.pop(len(particle_list) - j - 1)
                            else:
                                entity.trail.pop(len(particle_list) - j - 1)
            for i, particle in enumerate(list(reversed(sparks)).copy()):
                particle.iterate(None, None)
                particle.scale *= (0.999 * pow(particle.scale, 0.002))
                particle.texture = pygame.transform.scale(particle.source_texture, (int(particle.source_texture.get_width() * particle.scale), int(particle.source_texture.get_height() * particle.scale)))
                if particle.scale < 0.2:
                    if len(sparks) == 1:
                        sparks.clear()
                    else:
                        try:
                            sparks.pop(len(sparks) - i - 1)
                        except IndexError:
                            pass
            for i, particle in enumerate(list(reversed(lava_particles)).copy()):
                particle.iterate(0.7, 0.995)
                if particle.size < 0:
                    lava_particles.pop(len(lava_particles) - i - 1)
            if lava_timer % 2 == 0:
                for i, ripple in enumerate(list(reversed(ripples)).copy()):
                    try:
                        subject_block = level[ripple.position[1]][ripple.position[0]]
                    except IndexError:
                        subject_block = None
                    if subject_block is not None and subject_block.type == "lava" and not subject_block.bordering_blocks == "none":
                        subject_block.ripple_offset = [ripple.power if ripple.power < 0 else 0, 1]
                    else:
                        ripple.power = 0
                    if ripple.power > 2:
                        if len(ripples) == 1:
                            ripples.clear()
                        else:
                            ripples.pop(len(ripples) - 1 - i)
                    ripple.iterate()
            any_winners_remaining = False
            if player_event == "won":
                for index, entity in enumerate(entities):
                    if not entity.won and entity.alive:
                        any_winners_remaining, focus = True, index
                        break
                    elif not entity.won:
                        any_winners_remaining = True
                    if index == len(entities) - 1 and not any_winners_remaining:
                        victory = True
                        if sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["win"])
            if victory:
                for index, button in enumerate(winbuttons):
                    button_sound = button.iterate(get_mouse_pos(), mouse[0])
                    if (button_sound == "hover" or button_sound == "select") and sound_settings[0] and not (button_sound == "select" and (index == 1 or index == 3) and not playing_level == "editor"):
                        pygame.mixer.Sound.play(sound_library[button_sound])

            # adjust camera
            if entities[focus].grounded and mouse[0]:
                potential_velocity = entities[focus].predict_the_future(level, [mousepos[0] - (entities[focus].size / 2), mousepos[1] - (entities[focus].size / 2)], 1, blocksize)
                if not len(potential_velocity) == 0:
                    camera_ease = ((camera_ease[0] - (entities[focus].position[0] - (potential_velocity[0][0] + (300 if keys[K_d] or keys[K_RIGHT] else -300 if keys[K_a] or keys[K_LEFT] else 0))) * 0.07) * 0.95, (camera_ease[1] - (entities[focus].position[1] - (potential_velocity[0][1] + (300 if keys[K_s] or keys[K_DOWN] else -300 if keys[K_w] or keys[K_UP] else 0))) * 0.07) * 0.95)
            elif entities[focus].airtime > 3 or entities[focus].grounded:
                camera_ease = ((camera_ease[0] - ((entities[focus].position[0] - width / 2) - camera_non_offset_coords[0])) * 0.955, (camera_ease[1] - ((entities[focus].position[1] - height / 2) - camera_non_offset_coords[1])) * 0.955)
            else:
                camera_ease = ((camera_ease[0] - ((entities[focus].position[0] - width / 2) - camera_non_offset_coords[0])), (camera_ease[1] - ((entities[focus].position[1] - height / 2) - camera_non_offset_coords[1])))
            camera_non_offset_coords = ((entities[focus].position[0] - width / 2), (entities[focus].position[1] - height / 2))
            if not camera_shake_timer == 0:
                camera_shake_power = (camera_shake_power[0] * 0.87, camera_shake_power[1] * 0.87)
                camera_shake = (randint(round(camera_shake_power[0] * -1), round(camera_shake_power[0])), randint(round(camera_shake_power[1] * -1), round(camera_shake_power[1])))
                camera_shake_timer += 1
                if (round(camera_shake_power[0]) == 0 and round(camera_shake_power[1]) == 0) and camera_shake_timer >= 20:
                    camera_shake, camera_shake_power, camera_shake_timer = (0, 0), (0, 0), 0
            camera = (camera_non_offset_coords[0] + camera_ease[0], camera_non_offset_coords[1] + camera_ease[1])  # set camera based on player movement
            camera = set_border_offset((camera[0], camera[1]), camera_boundaries)
            for i in range(2):
                if camera[i] - camera_boundaries[i][0] + camera_shake[i] <= 0:
                    camera_shake = (camera[i] - camera_boundaries[i][0], camera_shake[1]) if i == 0 else (camera_shake[0], camera[i] - camera_boundaries[i][0])
                elif camera[i] - camera_boundaries[i][1] + camera_shake[i] >= 0:
                    camera_shake = (camera[i] - camera_boundaries[i][1], camera_shake[1]) if i == 0 else (camera_shake[0], camera[i] - camera_boundaries[i][1])
            hopefully_this_will_work = set_border_offset(camera_non_offset_coords, camera_boundaries)
            camera_splice = [[int((camera[0] + camera_shake[0] + width / 2) / blocksize - width / (blocksize * 2)) - 1, int((camera[0] + camera_shake[0] + width / 2) / blocksize + width / (blocksize * 2)) + 1],
                             [int((camera[1] + camera_shake[1] + height / 2) / blocksize - height / (blocksize * 2)) - 1, int((camera[1] + camera_shake[1] + height / 2) / blocksize + height / (blocksize * 2)) + 1]]

            if entities[focus].alive and ((keys[K_x] and not keystrokes["x"]) or (keys[K_z] and not keystrokes["z"])) and not victory:
                i = 0
                previous_focus = focus
                while i == 0 or (entities[focus].won and i > 0):
                    i += 1
                    if keys[K_x] and not keystrokes["x"]:
                        focus = indexloop(focus + 1, len(entities) - 1)
                    elif keys[K_z] and not keystrokes["z"]:
                        focus = focus - 1 if focus > 0 else len(entities) - 1
                if entities[focus].charge[1] > 0:
                    camera_ease = (camera_ease[0] - (entities[focus].position[0] - entities[previous_focus].position[0]), camera_ease[1] - (entities[focus].position[1] - entities[previous_focus].position[1]))

        # draw stuff
        mousepos = get_mouse_pos()
        for i in range(2):  # draw background and manage background particles
            if i == 1:
                for item in background_robots:
                    if not paused:
                        item.iterate(None, None)
                        if item.position[0] - (camera[0] - camera_shake[0] - spawnpoint[0] + width / 2) / 30 > width + 100:
                            item.position = (item.position[0] - 2200, randint(int(height * 0.3), int(height * 0.7)))
                    res_scale_blit(item.texture, (item.position[0] - (camera[0] - camera_shake[0] - spawnpoint[0] + width / 2) / 30, item.position[1] - (camera[1] - camera_shake[1] - spawnpoint[1] + height / 2) / 30))
            res_scale_blit(bg[i]["bg"], ((width - bg[i]["width"] / scale_mult[0]) / 2 - (camera[0] - spawnpoint[0] - camera_shake[0] + width / 2) / (20 * (bg_slices - i)), (height - bg[i]["height"] / scale_mult[1]) / 2 - (camera[1] - spawnpoint[1] - camera_shake[1] + height / 2) / (20 * (bg_slices - i))))  # draw the bg
        render3Deffect(level, (width / 2 + camera[0] + camera_shake[0], height / 2 + camera[1] + camera_shake[0]), lava_timer, [[camera_splice[0][0] - 1, camera_splice[0][1] + 2], [camera_splice[1][0], camera_splice[1][1] + 1]], num_3d_slices)  # draw 3D effect, spikes, and sparks
        mousepos = (mousepos[0] + hopefully_this_will_work[0], mousepos[1] + hopefully_this_will_work[1])
        for entity in entities:  # draw the tracers
            if entity.alive and not entity.won:
                for index, p in enumerate(entity.predict_the_future(level, [(mousepos[0] if not paused else paused_mousepos[0]) - (entity.size / 2), (mousepos[1] if not paused else paused_mousepos[1]) - (entity.size / 2)], 20, blocksize)):  # draw tracer, if applicable
                    playertextures[0].set_alpha(170 - (index * 9))
                    drawobject(playertextures[0], p, True)
        draw_entity_3d_and_trail((width / 2 + camera[0] + camera_shake[0], height / 2 + camera[1] + camera_shake[0]))
        if graphics_settings[1]:
            for particle in lava_particles:  # draw lava particles
                particle.draw()
        renderlevel(level, lava_layer, bugfix_end_gradients, paused, camera_splice)  # draw the level
        if graphics_settings[2]:
            for entity in entities:  # draw the particles
                for particle in entity.particles:
                    particle.draw()
        if victory:
            victory_timer += 1
            levelwinbar = pygame.transform.scale(levelwinbar.copy(), (int(500 if victory_timer >= 80 else pow(victory_timer - 70, 3) * 0.001458 + 500), 1080))
            res_scale_blit(levelwinbar, (width / 2 - levelwinbar.get_width() / 2, 0))
            winbuttons[0].position_offset[1] = (((840 * math.sin((victory_timer * 0.048)) - 660) if victory_timer <= 41 else 1000 * (pow(0.91, victory_timer - 18.06))) if victory_timer < 90 else (0.00005 * pow(0.90, (victory_timer - 90) - 145.36) - 225)) if victory_timer <= 126 else winbuttons[0].position_offset[1]
            for index, button in enumerate(winbuttons):
                if index > 0 and victory_timer > 88:
                    shifted_timer = victory_timer - 88 - (index - 1) * 3
                    winbuttons[index].position_offset[1] = ((-760 * math.sin((shifted_timer * 0.044)) + 660) if shifted_timer <= 41 else -1000 * (pow(0.9, shifted_timer - 16.97)))
                res_scale_blit(button.texture, (button.position[0] + button.position_offset[0] - (button.texture.get_width() / scale_mult[0]) / 2, button.position[1] + button.position_offset[1] - (button.texture.get_height() / scale_mult[1]) / 2))
                if button.clickscan():
                    if playing_level == "editor":
                        if index == 1 or index == 3:
                            mode, camera, camera_shake, fillrect = "editor", (0, 0), (0, 0), None
                            editor.setup_editor()
                            editor.leveldata = set_block_orientation(editor.leveldata, 30, False)[0]
                            new_texture = editorsettingstextures[0].copy()
                            editorsettingsbuttons[0].source_texture, editorsettingsbuttons[0].texture = editorsettingstextures[0], editorsettingstextures[0]
                            editorsettingsbuttons[0].reload_texture()
                            resize_textures(editor.editorsize, num_3d_slices)
                            editor.load_level()
                            victory = False
                        elif index == 2:
                            setup_level(open("leveldata/editorsavefile", "r"), True)
                    else:
                        if index == 1 and not playing_level == 20:
                            playing_level += 1
                            setup_level(open(str("leveldata/level" + str(playing_level)), "r"))
                        elif index == 2:
                            setup_level(open(str("leveldata/level" + str(playing_level)), "r"), True)
                        elif index == 3 or (index == 1 and playing_level == 20):
                            pygame.mixer.stop()
                            spawnpoint, camera = [632.5, 1127.5], (492.5, 457.5)
                            if sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["select"])
                            unpause()
                            pygame.mixer.music.load("sfx/ups_and_downs.wav")
                            pygame.mixer.music.play(-1)
                            mode, submode, camera, camera_shake, fillrect = "menu", "level select", (0, 0), (0, 0), None
                            victory = False
        if graphics_settings[0] and not paused:
            if global_death_timer > 6:
                res_scale_blit(vignette_texture, (0, 0))
            elif global_death_timer <= 6:
                res_scale_blit(flash[global_death_timer - 1], (0, 0))

    elif mode == "editor":
        mouse_touching_button = False
        if not paused:
            lava_timer = (lava_timer + 1) if lava_timer < 79 else 0
            new_xpos, new_ypos = None, None
            if keys[K_z] and not keystrokes["z"]:
                new_xpos = 60 if editorbuttons[0][0].position[0] == 1860 else 1860
                if sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library["place"])
                    pygame.mixer.Sound.play(sound_library["drag"])
            if keys[K_x] and not keystrokes["x"]:
                new_ypos = 32 if editorsettingsbuttons[0].position[1] == 1055 else 1055
                if sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library["place"])
                    pygame.mixer.Sound.play(sound_library["drag"])
            for i, button_list in enumerate(editorbuttons):
                for j, button in enumerate(button_list):
                    button_sound = button.iterate(mousepos, mouse[0])
                    if (button_sound == "hover" or button_sound == "select") and sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library[button_sound])
                    if new_xpos is not None:
                        button.position = (new_xpos, button.position[1])
                        button.update_hitbox()
                    if button.hitbox.collidepoint(mousepos):
                        mouse_touching_button = True
                    if button.clickscan():
                        if i == 0:
                            editor.editormode = {0: ("x", "spawnpoint"), 1: ("1", "solid"), 2: ("i", "nonstickysolid"), 3: ("2", "spike"), 4: ("3", "lava"), 5: ("e", "end"), 6: ("0", "air")}[j]
                            if editor.editormode[0] == "x":
                                new_texture = editorsettingstextures[1].copy()
                                editorsettingsbuttons[0].source_texture, editorsettingsbuttons[0].texture = new_texture, new_texture
                                editorsettingsbuttons[0].reload_texture()
                                for index, k in enumerate([None, (600, 32), (710, 32), (1020, 32), (1135, 32), (1485, 32), (1605, 32)]):
                                    if not index == 0:
                                        editorsettingsbuttons[index].position = (k[0], editorsettingsbuttons[index].position[1])
                        elif i == 1:
                            if j == 0:
                                editor.save_level()
                            elif j == 1:
                                editor.load_level()
                            else:
                                if editor.end_placed and len(editor.entities) > 0:
                                    editor.save_level()
                                    mode, playing_level = "play", "editor"
                                    setup_level(open("leveldata/editorsavefile", "r"))
                        if not editor.editormode[0] == "x":
                            new_texture = editorsettingstextures[0].copy()
                            editorsettingsbuttons[0].source_texture, editorsettingsbuttons[0].texture = editorsettingstextures[0], editorsettingstextures[0]
                            editorsettingsbuttons[0].reload_texture()
                            for index, k in enumerate([None, (540, 32), (660, 32), (990, 32), (1100, 32), (1455, 32), (1575, 32)]):
                                if not index == 0:
                                    editorsettingsbuttons[index].position = (k[0], editorsettingsbuttons[index].position[1])
            for i, button in enumerate(editorsettingsbuttons):
                if new_ypos is not None:
                    button.position = (button.position[0], new_ypos)
                    button.update_hitbox()
                button_sound = button.iterate(mousepos, mouse[0])
                if button_sound == "hover" or button_sound == "select":
                    button_sound = "place" if button_sound == "select" else button_sound
                    if ((i == 1 and editor.blocksize <= 40 and not editor.editormode[0] == "x") or (i == 2 and editor.blocksize >= 100 and not editor.editormode[0] == "x") or (i == 3 and ((not editor.editormode[0] == "x" and editor.width <= 64) or (editor.editormode[0] == "x" and editor.entity_settings[1] <= 20))) or
                            (i == 4 and ((not editor.editormode[0] == "x" and editor.width >= 300) or (editor.editormode[0] == "x" and editor.entity_settings[1] >= 100))) or (i == 5 and editor.height <= 36 and not editor.editormode[0] == "x") or (i == 6 and editor.height >= 200 and not editor.editormode[0] == "x")) and button_sound == "place":
                        if sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["error"])
                    elif sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library[button_sound])

                if button.hitbox.collidepoint(mousepos):
                    mouse_touching_button = True
                if button.clickscan():
                    if i == 1:
                        if editor.editormode[0] == "x":
                            editor.entity_attributes_order[0][0] = 5 if editor.entity_attributes_order[0][0] == 0 else editor.entity_attributes_order[0][0] - 1
                            editor.entity_settings[0] = editor.entity_attributes_order[1][editor.entity_attributes_order[0][0]]
                        elif not editor.editormode[0] == "x" and not editor.blocksize <= 40:
                            editor.blocksize -= 1
                    elif i == 2:
                        if editor.editormode[0] == "x":
                            editor.entity_attributes_order[0][0] = 0 if editor.entity_attributes_order[0][0] == 5 else editor.entity_attributes_order[0][0] + 1
                            editor.entity_settings[0] = editor.entity_attributes_order[1][editor.entity_attributes_order[0][0]]
                        elif not editor.editormode[0] == "x" and not editor.blocksize >= 100:
                            editor.blocksize += 1
                    elif i == 3:
                        if editor.editormode[0] == "x" and not editor.entity_settings[1] <= 20:
                            editor.entity_settings[1] -= 1
                        elif not editor.editormode[0] == "x" and not editor.width <= 64:
                            editor.width -= 1
                    elif i == 4:
                        if editor.editormode[0] == "x" and not editor.entity_settings[1] >= 100:
                            editor.entity_settings[1] += 1
                        elif not editor.editormode[0] == "x" and not editor.width >= 300:
                            editor.width += 1
                            editor.remove_end_gradient()
                    elif i == 5:
                        if editor.editormode[0] == "x":
                            editor.entity_attributes_order[0][1] = 3 if editor.entity_attributes_order[0][1] == 0 else editor.entity_attributes_order[0][1] - 1
                            editor.entity_settings[2] = editor.entity_attributes_order[2][editor.entity_attributes_order[0][1]]
                        elif not editor.editormode[0] == "x" and not editor.height <= 36:
                            editor.height -= 1
                    elif i == 6:
                        if editor.editormode[0] == "x":
                            editor.entity_attributes_order[0][1] = 0 if editor.entity_attributes_order[0][1] == 3 else editor.entity_attributes_order[0][1] + 1
                            editor.entity_settings[2] = editor.entity_attributes_order[2][editor.entity_attributes_order[0][1]]
                        elif not editor.editormode[0] == "x" and not editor.width >= 200:
                            editor.height += 1
                            editor.remove_end_gradient()
                    if i in (3, 4, 5, 6):
                        editor.adjust_dimensions()
            for button in editorsettingsbuttons:
                button.iterate(mousepos, mouse[0])
            if mode == "editor":
                sound_trigger = editor.manage(mouse if not mouse_touching_button else (False, False, False), (mousepos[0] + camera[0], mousepos[1] + camera[1]))
            if sound_trigger in ("place", "drag", "preview") and sound_settings[0]:
                if not sound_trigger == "preview":
                    pygame.mixer.Sound.stop(sound_library[sound_trigger])
                pygame.mixer.Sound.play(sound_library[sound_trigger])
            camera = (camera[0] + editor.editorsize, camera[1]) if (keys[K_RIGHT] and not keystrokes["right"]) or (keys[K_d] and not keystrokes["d"]) else (camera[0] - editor.editorsize, camera[1]) if (keys[K_LEFT] and not keystrokes["left"]) or (keys[K_a] and not keystrokes["a"]) else \
                (camera[0], camera[1] + editor.editorsize) if (keys[K_DOWN] and not keystrokes["down"]) or (keys[K_s] and not keystrokes["s"]) else (camera[0], camera[1] - editor.editorsize) if (keys[K_UP] and not keystrokes["up"]) or (keys[K_w] and not keystrokes["w"]) else camera
        else:
            editor.mouseheldpos = [(), ()]
        camera_splice = [[int((camera[0] + width / 2) / editor.editorsize - width / (editor.editorsize * 2)), int((camera[0] + width / 2) / editor.editorsize + width / (editor.editorsize * 2))],
                        [int((camera[1] + height / 2) / editor.editorsize - height / (editor.editorsize * 2)), int((camera[1] + height / 2) / editor.editorsize + height / (editor.editorsize * 2))]]
        camera_splice = [[camera_splice[0][0] if camera_splice[0][0] >= 0 else 0, camera_splice[0][1] if camera_splice[0][1] <= editor.width else editor.width],
                         [camera_splice[1][0] if camera_splice[1][0] >= 0 else 0, camera_splice[1][1] if camera_splice[1][1] <= editor.height else editor.height]]
        # draw editor
        res_scale_blit(editor_bg, (0, 0))
        for i in range(2):
            for rowindex, row in enumerate(editor.leveldata[camera_splice[1][0]: camera_splice[1][1]]):
                for itemindex, item in enumerate(row[camera_splice[0][0]: camera_splice[0][1]]):
                    if item.type == "spawnpoint":
                        entity_texture_index, entity_size = 0, 0
                        if not item.transparent:
                            for entity in editor.entities:
                                if entity[3] == ((itemindex + camera_splice[0][0]) * editor.editorsize, (rowindex + camera_splice[1][0]) * editor.editorsize):
                                    entity_texture_index, entity_size = {"normal": 0, "doublejump": 1, "gravityswitch": 2, "groundpound": 3, "nogravity": 4, "mitosis": 5}[entity[0]] if entity[3] == ((itemindex + camera_splice[0][0]) * editor.editorsize, (rowindex + camera_splice[1][0]) * editor.editorsize) else None, entity[1]
                        else:
                            entity_texture_index = editor.entity_attributes_order[0][0]
                    if not item.transparent and not item.type == "air":
                        block_texture = block_textures[item.type][item.bordering_blocks].copy() if not (item.type == "spawnpoint") else editorinvisblocktextures[entity_texture_index].copy()
                    elif item.transparent:
                        block_texture = (block_textures[item.type][item.bordering_blocks].copy() if not (item.type == "spawnpoint") else editorinvisblocktextures[entity_texture_index].copy()) if not item.type == "air" else editorinvisblocktextures[6].copy()
                        if not item.type == "air":
                            block_texture.set_alpha(100)
                    if item.type == "spawnpoint":
                        if not item.transparent:
                            block_texture = pygame.transform.scale(block_texture.copy(), (int(30 * (entity_size / 50)), int(30 * (entity_size / 50))))
                        else:
                            block_texture = pygame.transform.scale(block_texture.copy(), (int(30 * (editor.entity_settings[1] / 50)), int(30 * (editor.entity_settings[1] / 50))))
                    if i == 0 and item.type == "lava":
                        drawobject(block_texture, item.position if item.bordering_blocks == "none" else item.get_lava_offset(lava_timer), False)
                    elif i == 1 and (item.type not in ("air", "lava") or (item.transparent and not item.type == "lava")):
                        drawobject(block_texture, item.position if not item.type == "spawnpoint" else (item.position[0] - (block_texture.get_width() - 30) / 2, item.position[1] - (block_texture.get_height() - 30) / 2), False)
        if not editor.mouseheldpos == [(), ()]:
            mouseheldpos = sorted(editor.mouseheldpos)
            if mouseheldpos[1][0] >= mouseheldpos[0][0] and mouseheldpos[1][1] >= mouseheldpos[0][1]:
                fillrect = Rect(mouseheldpos[0][0], mouseheldpos[0][1], mouseheldpos[1][0] - mouseheldpos[0][0], mouseheldpos[1][1] - mouseheldpos[0][1])
            elif mouseheldpos[1][0] >= mouseheldpos[0][0] and not mouseheldpos[1][1] >= mouseheldpos[0][1]:
                fillrect = Rect(mouseheldpos[0][0], mouseheldpos[1][1], mouseheldpos[1][0] - mouseheldpos[0][0], mouseheldpos[0][1] - mouseheldpos[1][1])
            fillrect = Rect(fillrect.x, fillrect.y, fillrect.w if fillrect.w > 0 else 30, fillrect.h if fillrect.h > 0 else 30)
            rect_resize_border = int(2.5 * math.sin(0.12 * editor.timer - 1.6) + 8.5)
            pygame.draw.rect(win, (255, 255, 255), ((fillrect.x - camera[0]) * scale_mult[0], (fillrect.y - camera[1]) * scale_mult[1], fillrect.w, fillrect.h), rect_resize_border)
        elif fillrect is not None:
            if not paused:
                editor.fill_rect(fillrect)
            fillrect = None
        pygame.draw.rect(win, (255, 255, 255), ((0 - camera[0]) * scale_mult[0], (0 - camera[1]) * scale_mult[1], editor.width * editor.editorsize, editor.height * editor.editorsize), 10)
        if not paused:
            editor.remove_preview()
        for i, button_list in enumerate(editorbuttons):
            for button in button_list:
                res_scale_blit(button.texture, (button.position[0] + button.position_offset[0] - (button.texture.get_width() / scale_mult[0]) / 2, button.position[1] + button.position_offset[1] - (button.texture.get_height() / scale_mult[1]) / 2))
        for button in editorsettingsbuttons:
            res_scale_blit(button.texture, (button.position[0] + button.position_offset[0] - (button.texture.get_width() / scale_mult[0]) / 2, button.position[1] + button.position_offset[1] - (button.texture.get_height() / scale_mult[1]) / 2))
        if not editor.editormode[0] == "x":
            drawnumber(editor.blocksize, (600, 31 if editorsettingsbuttons[0].position[1] == 32 else 1056), 0.25)
            drawnumber(editor.width, (1050, 31 if editorsettingsbuttons[0].position[1] == 32 else 1056), 0.25)
            drawnumber(editor.height, (1515, 31 if editorsettingsbuttons[0].position[1] == 32 else 1056), 0.25)
        else:
            res_scale_blit(entityattributetextures[editor.entity_attributes_order[0][0]], (657 - (entityattributetextures[editor.entity_attributes_order[0][0]].get_width() / scale_mult[0]) / 2, (33 if editorsettingsbuttons[0].position[1] == 32 else 1057) - (entityattributetextures[editor.entity_attributes_order[0][0]].get_height() / scale_mult[1]) / 2))
            drawnumber(editor.entity_settings[1], (1080, 31 if editorsettingsbuttons[0].position[1] == 32 else 1056), 0.25)
            res_scale_blit(entityattributetextures[editor.entity_attributes_order[0][1] + 6], (1547 - (entityattributetextures[editor.entity_attributes_order[0][1] + 6].get_width() / scale_mult[0]) / 2, (33 if editorsettingsbuttons[0].position[1] == 32 else 1057) - (entityattributetextures[editor.entity_attributes_order[0][1] + 6].get_height() / scale_mult[1]) / 2))

    elif mode == "menu":
        # scanning
        menu_timer += 1
        camera = ((mousepos[0] / 2), (mousepos[1] / 2))
        if submode == "intro":
            intro_timer += 1
            if intro_timer == 1 and sound_settings[0]:
                pygame.mixer.Sound.play(sound_library["win"])
            elif intro_timer == 100:
                pygame.mixer.music.play(-1)
            elif intro_timer == 110:
                submode = "menu"
        if submode == "menu":
            if button_clicked is None:
                for index, button in enumerate(menubuttons):
                    button_sound = button.iterate(mousepos, mouse[0])
                    if (button_sound == "hover" or button_sound == "select") and sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library[button_sound])
                    if button.clickscan():
                        if index == 1:
                            menu_timer, menu_transition_timer, button_clicked = 0, ["forward", 0], "level select"
                            button.size_offset, button.mouse_touching_timer = 0.9, 0
                            button.reload_texture()
                            if sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["whoosh"])
                        elif index == 2:
                            button.size_offset, button.mouse_touching_timer = 0.9, 0
                            button.reload_texture()
                            editor.setup_editor()
                            editor.leveldata = set_block_orientation(editor.leveldata, editor.editorsize, False)[0]
                            new_texture = editorsettingstextures[0].copy()
                            editorsettingsbuttons[0].source_texture, editorsettingsbuttons[0].texture = editorsettingstextures[0], editorsettingstextures[0]
                            editorsettingsbuttons[0].reload_texture()
                            for i, k in enumerate([None, (540, 32), (660, 32), (990, 32), (1100, 32), (1455, 32), (1575, 32)]):
                                if not i == 0:
                                    editorsettingsbuttons[i].position = (k[0], editorsettingsbuttons[i].position[1])
                            resize_textures(editor.editorsize, num_3d_slices)
                            if playing_level == "editor":
                                editor.load_level()
                            buttonsheldtimer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            mode, camera, camera_shake, fillrect = "editor", (0, 0), (0, 0), None
                        if index == 3:
                            menu_timer, menu_transition_timer, button_clicked = 0, ["forward", 0], "help"
                            button.size_offset, button.mouse_touching_timer = 0.9, 0
                            button.reload_texture()
                            if sound_settings[0]:
                                pygame.mixer.Sound.play(sound_library["whoosh"])
                        elif index == 4:
                            run = False
            else:
                menu_transition_timer[1] += 1 if menu_transition_timer[0] == "forward" else -1
                for index, button in enumerate(list(reversed(menubuttons))):
                    shifted_timer = menu_transition_timer[1] - index * 2 + 2
                    if shifted_timer >= 0:
                        button.position_offset[1] = ((-0.07 * pow((shifted_timer + 7.4), 3) + 2.8 * pow((shifted_timer + 7.4), 2) + -30 * (shifted_timer + 7.4) + 97) * (1 if index == 4 else -1)) if not menu_transition_timer == ["forward", 37] else 0
                if menu_transition_timer == ["forward", 36]:
                    submode = "level select" if button_clicked == "level select" else "help"
                    menu_transition_timer = ["backward", 36]
                elif menu_transition_timer == ["backward", 0]:
                    button_clicked = None
                    menu_timer = 42
        elif submode == "level select":
            for index, button in enumerate(levelbuttons):
                button_sound = button.iterate(mousepos, mouse[0])
                if (button_sound == "hover" or (button_sound == "select" and menu_timer > 1)) and sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library[button_sound])
                if button.clickscan() and menu_timer > 1:
                    mode = "play"
                    pygame.mixer.music.load("sfx/one_way_or_another.wav")
                    pygame.mixer.music.play(-1)
                    playing_level = index + 1
                    setup_level(open(str("leveldata/level" + str(playing_level)), "r"))
                    break
        if submode in ("level select", "help"):
            button_sound = backbutton.iterate(mousepos, mouse[0])
            if button_sound == "hover" or button_sound == "select" and button_clicked is None:
                if sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library[button_sound])
                    if button_sound == "select":
                        pygame.mixer.Sound.play(sound_library["whoosh"])
                if backbutton.clickscan():
                    backbutton.size_offset, backbutton.mouse_touching_timer = 0.9, 0
                    backbutton.reload_texture()
                    menu_transition_timer, button_clicked = ["forward", 0], "menu"
                    for button in menubuttons:
                        button.position_offset[1] = ((-0.07 * pow((37 + 7.4), 3) + 2.8 * pow((37 + 7.4), 2) + -30 * (37 + 7.4) + 97) * (1 if index == 4 else -1))
            if button_clicked is not None:
                shifted_timer = menu_transition_timer[1] - (8 if menu_transition_timer[0] == "backward" else 0)
                backbutton.position_offset[1] = ((-0.07 * pow((shifted_timer + 7.4), 3) + 2.8 * pow((shifted_timer + 7.4), 2) + -30 * (shifted_timer + 7.4) + 97) * -0.3) if not menu_transition_timer == ["forward", 37] and not shifted_timer < 0 else 0
            if submode in ("help", "level select") and button_clicked is not None:
                menu_transition_timer[1] += 1 if menu_transition_timer[0] == "forward" else -1
                help_offset = ((-0.07 * pow((menu_transition_timer[1] + 7.4), 3) + 2.8 * pow((menu_transition_timer[1] + 7.4), 2) + -30 * (menu_transition_timer[1] + 7.4) + 97) * (1 if index == 4 else -1)) if not menu_transition_timer[1] == ["forward", 36] else 0
                if menu_transition_timer == ["backward", 0]:
                    button_clicked = None
                    menu_timer = 42
                elif menu_transition_timer == ["forward", 36]:
                    submode = "menu"
                    menu_transition_timer = ["backward", 36]

        # draw stuff
        for i in range(3):  # draw background and manage background particles
            if i == 1:
                for item in background_robots:
                    if not paused:
                        item.iterate(None, None)
                        if item.position[0] - (camera[0] - camera_shake[0] - spawnpoint[0] + width / 2) / 30 > width + 100:
                            item.position = (item.position[0] - 2200, randint(int(height * 0.3), int(height * 0.7)))
                    res_scale_blit(item.texture, (item.position[0] - (camera[0] - camera_shake[0] - spawnpoint[0] + width / 2) / 30, item.position[1] - (camera[1] - camera_shake[1] - spawnpoint[1] + height / 2) / 30))
            res_scale_blit(bg[i]["bg"], ((width - bg[i]["width"] / scale_mult[0]) / 2 - (camera[0] - spawnpoint[0] - camera_shake[0] + width / 2) / (20 * (bg_slices - (i - 1))), (height - bg[i]["height"] / scale_mult[1]) / 2 - (camera[1] - spawnpoint[1] - camera_shake[1] + height / 2) / (20 * (bg_slices - (i - 1)))))
        if submode == "menu" or (submode == "intro" and not intro_timer < 85):
            if not button_clicked:
                menubar = pygame.transform.scale(levelwinbar.copy(), (470 + (25 * math.sin(0.07 * menu_timer)), true_res[1]))
            else:
                menubar = pygame.transform.scale(levelwinbar.copy(), (470 + (-0.7 * pow(menu_transition_timer[1], 2) + 12 * menu_transition_timer[1]) if 470 + (-0.7 * pow(menu_transition_timer[1], 2) + 12 * menu_transition_timer[1]) > 0 else 0, true_res[1]))
            menubar.set_alpha(140)
            res_scale_blit(menubar, (width / 2 - menubar.get_width() / 2, 0))
            for button in menubuttons:
                res_scale_blit(button.texture, (button.position[0] + button.position_offset[0] - (button.texture.get_width() / scale_mult[0]) / 2, button.position[1] + button.position_offset[1] - (button.texture.get_height() / scale_mult[1]) / 2))
        elif submode == "level select":
            if not button_clicked:
                menubar = pygame.transform.scale(levelwinbar.copy(), (1200 + (25 * math.sin(0.07 * menu_timer)), true_res[1]))
            else:
                menubar = pygame.transform.scale(levelwinbar.copy(), (1200 + ((-0.7 * pow(menu_transition_timer[1], 2) + 12 * menu_transition_timer[1]) * 2.55319) if 1200 + ((-0.7 * pow(menu_transition_timer[1], 2) + 12 * menu_transition_timer[1]) * 2.55319) > 0 else 0, true_res[1]))
            menubar.set_alpha(140)
            res_scale_blit(menubar, (width / 2 - menubar.get_width() / 2, 0))
            res_scale_blit(menubuttontextures[8], (width / 2 - (menubuttontextures[8].get_width() / scale_mult[0]) / 2, 25 + help_offset * -1))  # 26
            for index, button in enumerate(levelbuttons):
                res_scale_blit(button.texture, (button.position[0] + button.position_offset[0] - (button.texture.get_width() / scale_mult[0]) / 2 + help_offset * pow(-1, int(index / 5)), button.position[1] + button.position_offset[1] - (button.texture.get_height() / scale_mult[1]) / 2))
                drawnumber(index + 1, (button.position[0] + button.position_offset[0] - (5 if 8 < index < 19 or index == 0 else 0) + help_offset * pow(-1, int(index / 5)), button.position[1] + button.position_offset[1] - 5), 0.35 * button.size_offset)
        elif submode == "help":
            if not button_clicked:
                menubar = pygame.transform.scale(levelwinbar.copy(), (1000 + (25 * math.sin(0.07 * menu_timer)), true_res[1]))
            else:
                menubar = pygame.transform.scale(levelwinbar.copy(), (1000 + ((-0.7 * pow(menu_transition_timer[1], 2) + 12 * menu_transition_timer[1]) * 2.12765) if 1000 + ((-0.7 * pow(menu_transition_timer[1], 2) + 12 * menu_transition_timer[1]) * 2.12765) > 0 else 0, true_res[1]))
            menubar.set_alpha(140)
            res_scale_blit(menubar, (width / 2 - menubar.get_width() / 2, 0))
            res_scale_blit(menubuttontextures[9], (width / 2 - menubuttontextures[9].get_width() / 2, 25 + help_offset))
        if submode in ("level select", "help"):
            res_scale_blit(backbutton.texture, (backbutton.position[0] + backbutton.position_offset[0] - (backbutton.texture.get_width() / scale_mult[0]) / 2, backbutton.position[1] + backbutton.position_offset[1] - (backbutton.texture.get_height() / scale_mult[1]) / 2))
        if submode == "intro":
            animation_frame = introanimationtextures[int((intro_timer - 1) / 2) if int((intro_timer - 1) / 2) <= 7 else 7]
            animation_frame = pygame.transform.scale(animation_frame, (int(animation_frame.get_width() * (0.84 + (0.001 * intro_timer))), int(animation_frame.get_height() * (0.84 + (0.001 * intro_timer)))))
            if intro_timer >= 85:
                animation_frame.set_alpha(255 - 10.2 * (intro_timer - 85))
            res_scale_blit(animation_frame, (width / 2 - (animation_frame.get_width() / scale_mult[0]) / 2, height / 2 - (animation_frame.get_height() / scale_mult[1]) / 2))
        if (not submode == "intro") or intro_timer >= 85:
            res_scale_blit(vignette_texture, (0, 0))

    if mode == "play" or mode == "editor":
        # check for pause / end game event
        if keys[K_ESCAPE] and not keystrokes["esc"] and not victory:
            if not paused:
                paused, paused_mousepos = True, mousepos
                pygame.mixer.pause()
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                if sound_settings[0]:
                    for i in range(5, 8):
                        if pygame.mixer.Channel(i).get_busy:
                            pygame.mixer.Channel(i).stop()
                    pygame.mixer.Sound.play(sound_library["hover"])
                    pygame.mixer.Sound.play(sound_library["place"])
                submode = "paused"
                if mode == "editor":
                    editor.remove_preview(True)
            else:
                unpause()
                if sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library["place"])

        # check for key inputs
        if keys[K_ESCAPE]:
            if not keystrokes["esc"]:
                keystrokes["esc"] = True
        else:
            keystrokes["esc"] = False
        if not paused:
            for entity in entities:
                if entity.alive and not entity.won and mode == "play":
                    entity.process_user_inputs(mousepos, mouse)
            if keys[K_z]:
                if not keystrokes["z"]:
                    keystrokes["z"] = True
            else:
                keystrokes["z"] = False
            if keys[K_x]:
                if not keystrokes["x"]:
                    keystrokes["x"] = True
            else:
                keystrokes["x"] = False
            if keys[K_RIGHT]:
                if not keystrokes["right"]:
                    keystrokes["right"] = True
            else:
                keystrokes["right"] = False
            if keys[K_LEFT]:
                if not keystrokes["left"]:
                    keystrokes["left"] = True
            else:
                keystrokes["left"] = False
            if keys[K_UP]:
                if not keystrokes["up"]:
                    keystrokes["up"] = True
            else:
                keystrokes["up"] = False
            if keys[K_DOWN]:
                if not keystrokes["down"]:
                    keystrokes["down"] = True
            else:
                keystrokes["down"] = False
            if keys[K_w]:
                if not keystrokes["w"]:
                    keystrokes["w"] = True
            else:
                keystrokes["w"] = False
            if keys[K_a]:
                if not keystrokes["a"]:
                    keystrokes["a"] = True
            else:
                keystrokes["a"] = False
            if keys[K_s]:
                if not keystrokes["s"]:
                    keystrokes["s"] = True
            else:
                keystrokes["s"] = False
            if keys[K_d]:
                if not keystrokes["d"]:
                    keystrokes["d"] = True
            else:
                keystrokes["d"] = False
            if mode == "editor":
                buttonsheldtimer = [(buttonsheldtimer[0] + 1) if keys[K_w] or keys[K_UP] else 0, (buttonsheldtimer[1] + 1) if keys[K_a] or keys[K_LEFT] else 0,
                                    (buttonsheldtimer[2] + 1) if keys[K_s] or keys[K_DOWN] else 0, (buttonsheldtimer[3] + 1) if keys[K_d] or keys[K_RIGHT] else 0, 0, 0, 0, 0, 0, 0]
                if (buttonsheldtimer[0] == 1 or buttonsheldtimer[1] == 1 or buttonsheldtimer[2] == 1 or buttonsheldtimer[3] == 1) and sound_settings[0]:
                    pygame.mixer.Sound.play(sound_library["drag"])
                for i in [(0, "w", "up"), (1, "a", "left"), (2, "s", "down"), (3, "d", "right")]:
                    if buttonsheldtimer[i[0]] > 8:
                        buttonsheldtimer[i[0]], keystrokes[i[1]], keystrokes[i[2]] = 0, False, False

        # pause buttons
        if paused:
            res_scale_blit(pause_bg if not mode == "editor" else editor_pause_bg, (0, -2))
            if submode == "paused":
                for index, button in enumerate(pausedbuttons):
                    shifted_timer = pause_timer - index * 3
                    if shifted_timer == 0 and sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library["preview"])
                    button.zoom_offset = (-0.9 if shifted_timer < 0 else pow(0.7, shifted_timer - 11.478) * -0.015) if shifted_timer < 20 else 0
                    button_sound = button.iterate(get_mouse_pos(), mouse[0])
                    res_scale_blit(button.texture, (button.position[0] - (button.texture.get_width() / scale_mult[0]) / 2, button.position[1] - (button.texture.get_height() / scale_mult[1]) / 2))
                    if index == 1 and button.clickscan():
                        if mode == "editor":
                            editor.mousedown, editor.rightmousedown, editor.timer, editor.mouseheldpos = [False, False, False], [False, False], 0, [(), ()]
                        unpause()
                    elif index == 2 and button.clickscan():
                        if mode == "play" and not playing_level == "editor":
                            setup_level(open(str("leveldata/level" + str(playing_level)), "r"), True)
                        elif mode == "play" and playing_level == "editor":
                            setup_level(open("leveldata/editorsavefile", "r"), True)
                        else:
                            editor.setup_editor()
                            fillrect = None
                        unpause()
                        pygame.mixer.stop()
                        buttonsheldtimer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    elif index == 3 and button.clickscan():
                        submode = "settings"
                    elif index == 4 and button.clickscan():
                        pygame.mixer.stop()
                        unpause()
                        victory = False
                        spawnpoint, camera = [632.5, 1127.5], (492.5, 457.5)
                        if playing_level == "editor" and not mode == "editor":
                            mode, camera, camera_shake, fillrect = "editor", (0, 0), (0, 0), None
                            editor.setup_editor()
                            editor.leveldata = set_block_orientation(editor.leveldata, 30, False)[0]
                            new_texture = editorsettingstextures[0].copy()
                            editorsettingsbuttons[0].source_texture, editorsettingsbuttons[0].texture = editorsettingstextures[0], editorsettingstextures[0]
                            editorsettingsbuttons[0].reload_texture()
                            for i, k in enumerate([None, (540, 32), (660, 32), (990, 32), (1100, 32), (1455, 32), (1575, 32)]):
                                if not i == 0:
                                    editorsettingsbuttons[i].position = (k[0], editorsettingsbuttons[i].position[1])
                            resize_textures(editor.editorsize, num_3d_slices)
                            editor.load_level()
                        else:
                            if not mode == "editor":
                                pygame.mixer.music.load("sfx/ups_and_downs.wav")
                                pygame.mixer.music.play(-1)
                            else:
                                editor.save_level()
                            mode, submode, camera, camera_shake, fillrect, menu_timer, menu_transition_timer, button_clicked, help_offset = "menu", "level select", (0, 0), (0, 0), None, 0, ["forward", 0], None, 0
                            backbutton.position_offset[1] = 0
                            for i in levelbuttons:
                                i.held = False
                                i.position_offset = [0, 0]
                    elif index == 5 and button.clickscan():
                        run = False
                    if (button_sound == "hover" or button_sound == "select") and sound_settings[0]:
                        pygame.mixer.Sound.play(sound_library[button_sound])
            elif submode == "settings":
                res_scale_blit(pausedbuttons[0].texture, (pausedbuttons[0].position[0] - (pausedbuttons[0].texture.get_width() / scale_mult[0]) / 2,
                                          pausedbuttons[0].position[1] - (pausedbuttons[0].texture.get_height() / scale_mult[1]) / 2))
                for index, button in enumerate(settingsbuttons):
                    button_sound = button.iterate(get_mouse_pos(), mouse[0])
                    res_scale_blit(button.texture, (button.position[0] - (button.texture.get_width() / scale_mult[0]) / 2,
                                              button.position[1] - (button.texture.get_height() / scale_mult[1]) / 2))
                    if index == 0 and button.clickscan():
                        with open("game_settings", "w") as r:
                            for i in range(4):
                                r.write("1 " if graphics_settings[i] else "0 ")
                            for i in range(2):
                                r.write("1 " if sound_settings[i] else "0 ")
                            r.write(str(num_3d_slices))
                        submode = "paused"
                    if (button_sound == "hover" or button_sound == "select") and sound_settings[0]:
                        if not ((index == 1 and num_3d_slices == 5) or (index == 2 and num_3d_slices == 15)) and sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["place" if button_sound == "select" and not index == 0 else button_sound])
                        elif sound_settings[0]:
                            pygame.mixer.Sound.play(sound_library["error"])
                    if button.clickscan():
                        if index == 1 and not num_3d_slices == 5:
                            num_3d_slices -= 1
                            resize_textures(blocksize if not mode == "editor" else editor.editorsize, num_3d_slices)
                        elif index == 2 and not num_3d_slices == 15:
                            num_3d_slices += 1
                            resize_textures(blocksize if not mode == "editor" else editor.editorsize, num_3d_slices)
                        elif index == 3 or index == 4:
                            graphics_settings[0] = True if not graphics_settings[0] else False
                        elif index == 5 or index == 6:
                            graphics_settings[1] = True if not graphics_settings[1] else False
                        elif index == 7 or index == 8:
                            graphics_settings[2] = True if not graphics_settings[2] else False
                        elif index == 9 or index == 10:
                            graphics_settings[3] = True if not graphics_settings[3] else False
                            if graphics_settings[3]:
                                win = pygame.display.set_mode((width, height), FULLSCREEN)
                            else:
                                win = pygame.display.set_mode((width, height))
                        elif index == 11 or index == 12:
                            sound_settings[1] = True if not sound_settings[1] else False
                            pygame.mixer.music.set_volume(0.45 if sound_settings[1] else 0.0)
                        elif index == 13 or index == 14:
                            sound_settings[0] = True if not sound_settings[0] else False
                            if sound_settings[0]:
                                pygame.mixer.unpause()
                            else:
                                pygame.mixer.stop()
                for index, i in enumerate([(width / 2 - 310, 517), (width / 2 - 310, 557), (width / 2 - 310, 597), (width / 2 - 310, 637), (width / 2 - 310, 677), (width / 2 + 120, 577), (width / 2 + 120, 617)]):
                    res_scale_blit(settingswordstextures[(index if not index == 4 else 9) if not index > 4 else index - 1], (i[0] - (settingswordstextures[index if not index == 4 else 9].get_width() / scale_mult[0]) / 2 + (7 if index == 6 else 0), i[1] - (settingswordstextures[index if not index == 4 else 9].get_height() / scale_mult[1]) / 2))
                    if index == 0:
                        drawnumber(num_3d_slices, (i[0] + 209, i[1]), 0.2)
                    elif index in (1, 2, 3):
                        res_scale_blit(settingswordstextures[6 if graphics_settings[index - 1] else 7], (i[0] + 209 - (settingswordstextures[6 if graphics_settings[index - 1] else 7].get_width() / scale_mult[0]) / 2.03, i[1] - (settingswordstextures[6 if graphics_settings[index - 1] else 7].get_height() / scale_mult[1]) / 2.03))
                    elif index == 4:
                        res_scale_blit(settingswordstextures[10 if graphics_settings[3] else 11], (i[0] + 209 - (settingswordstextures[10 if graphics_settings[3] else 11].get_width() / scale_mult[0]) / 2.03, i[1] - (settingswordstextures[10 if graphics_settings[3] else 11].get_height() / scale_mult[1]) / 2.03))
                    elif index in (5, 6):
                        res_scale_blit(settingswordstextures[6 if sound_settings[0 if index == 6 else 1] else 7], (i[0] + 157 - (settingswordstextures[6 if sound_settings[0 if index == 6 else 1] else 7].get_width() / scale_mult[0]) / 2.03, i[1] - (settingswordstextures[6 if sound_settings[0 if index == 6 else 1] else 7].get_height() / scale_mult[1]) / 2.03))
            pause_timer += 1

    for player_event in pygame.event.get():
        if player_event.type == pygame.QUIT:
            run = False
    pygame.display.update()
    clock.tick(60)
pygame.quit()
