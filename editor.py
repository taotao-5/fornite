import pygame
from block import Block, set_block_orientation
from copy import deepcopy
pygame.init()

leveldata, non_preview_block, entities, editormode, timer, end_placed, end_direction = [], None, [], ("1", "solid"), 0, False, None
editorsize = 30
blocksize = 50
width, height = 64, 36
mousedown = [False, False, False]
rightmousedown = [False, False]
mouseheldpos = [(), ()]
firstheldmousepos, prev_non_preview_block = (), None
clickmode = "click"
entity_settings = ["normal", 50, "down"]
entity_attributes_order = [[0, 0], ["normal", "doublejump", "gravityswitch", "groundpound", "nogravity", "mitosis"], ["down", "right", "up", "left"]]


def setup_editor():
    global leveldata, entities, entity_settings, mousedown, editormode, clickmode, non_preview_block, timer, end_placed, mouseheldpos, firstheldmousepos, prev_non_preview_block, entity_attributes_order, width, height, end_direction
    mousedown, rightmousedown = [False, False, False], [False, False]
    entity_attributes_order = [[0, 0], ["normal", "doublejump", "gravityswitch", "groundpound", "nogravity", "mitosis"], ["down", "right", "up", "left"]]
    clickmode = "click"
    width, height = 64, 36
    leveldata, non_preview_block, entities, entity_settings, editormode, end_placed, end_direction, mouseheldpos, firstheldmousepos, prev_non_preview_block = [], None, [], ["normal", 50, "down"], ("1", "solid"), False, None, [(), ()], (), None
    for i in range(36):
        leveldata.append([])
        for j in range(64):
            leveldata[i].append(Block((j * editorsize, i * editorsize), "0", editorsize))
    load_level()


def copy_leveldata(leveldata):
    leveldata_copy = []
    for row in leveldata:
        leveldata_copy.append(row)
    return leveldata_copy


def manage(mouse, mousepos):  # spaghetti code :(
    global leveldata, mousedown, rightmousedown, clickmode, non_preview_block, mouseheldpos, timer, end_placed, firstheldmousepos, prev_non_preview_block, end_direction
    return_sound_trigger = None
    timer += 1
    if clickmode == "click" and not mouse[0] and mousedown[0] and editormode[1] == "end":
        end_placed = True
    mousedown[1] = True if mouse[0] and not mousedown[0] else False
    mousedown[0] = True if mouse[0] else False
    mousedown[2] = True if not mouse[0] else mousedown[2]
    rightmousedown[1] = True if mouse[2] and not rightmousedown[0] else False
    rightmousedown[0] = True if mouse[2] else False
    clickmode = "click" if not mouse[2] else "drag"
    mouse_index = (int(mousepos[0] / editorsize), int(mousepos[1] / editorsize))
    mouse_index = ((mouse_index[0] if not mouse_index[0] < 0 else 0) if not mouse_index[0] > width - 1 else width - 1, (mouse_index[1] if not mouse_index[1] < 0 else 0) if not mouse_index[1] > height - 1 else height - 1)
    item_end_direction = "down" if mouse_index[1] == 0 else "up" if mouse_index[1] == (len(leveldata) - 1) else "right" if mouse_index[0] == 0 else "left"
    if not (editormode[1] == "spike" and (
            leveldata[mouse_index[1]][mouse_index[0]].type in ("solid", "nonstickysolid", "lava", "end") or
            (((mouse_index[1] == (len(leveldata) - 1)) or leveldata[mouse_index[1] + 1][mouse_index[0]].type not in ("solid", "nonstickysolid")) and
            ((mouse_index[1] == 0) or leveldata[mouse_index[1] - 1][mouse_index[0]].type not in ("solid", "nonstickysolid")) and
            ((mouse_index[0] == (len(leveldata[0]) - 1)) or leveldata[mouse_index[1]][mouse_index[0] + 1].type not in ("solid", "nonstickysolid")) and
            ((mouse_index[0] == 0) or leveldata[mouse_index[1]][mouse_index[0] - 1].type not in ("solid", "nonstickysolid"))))):
        if not (editormode[1] == "end" and not (
                mouse_index[0] == 0 or
                mouse_index[1] == 0 or
                mouse_index[0] == (len(leveldata[0]) - 1) or
                mouse_index[1] == (len(leveldata) - 1))):
            if clickmode == "click" and mouseheldpos == [(), ()] and not ((mouse_index[0] > width - 1) or (mouse_index[1] > height - 1) or (mouse_index[0] < 0) or (mouse_index[1] < 0)):
                if ((not editormode[1] == "spawnpoint" and mousedown[0] and mousedown[2]) or
                    (editormode[1] == "spawnpoint" and mousedown[1] and mousedown[2])) and (editormode[1] == "spawnpoint" or not leveldata[mouse_index[1]][
                                                                                  mouse_index[0]].type == editormode[1]):
                    new_block = Block((mouse_index[0] * editorsize, mouse_index[1] * editorsize), editormode[0], editorsize)
                    if leveldata[mouse_index[1]][mouse_index[0]].type == "end":
                        remove_end_gradient()
                    elif leveldata[mouse_index[1]][mouse_index[0]].type == "spawnpoint":
                        for index, entity in enumerate(entities):
                            if entity[3] == (mouse_index[0] * editorsize, mouse_index[1] * editorsize):
                                entities.pop(index)
                    if editormode[1] == "spawnpoint":
                        entities.append((entity_settings[0], entity_settings[1], entity_settings[2], (mouse_index[0] * editorsize, mouse_index[1] * editorsize)))
                    elif editormode[1] == "end":
                        if end_direction is None and not end_placed:
                            end_direction = item_end_direction
                        elif not item_end_direction == end_direction:
                            end_placed = True
                    if not (editormode[1] == "end" and not item_end_direction == end_direction):
                        leveldata[mouse_index[1]][mouse_index[0]] = new_block
                        return_sound_trigger = "place"
                    firstheldmousepos = mousepos
                    wait_thats_illegal()
                elif ((not leveldata[mouse_index[1]][mouse_index[0]].type == editormode[1]) or editormode[1] in ("air", "spawnpoint")) and not (editormode[1] == "end" and not item_end_direction == end_direction and end_placed):
                    non_preview_block = leveldata[mouse_index[1]][mouse_index[0]]
                    leveldata[mouse_index[1]][mouse_index[0]] = Block((mouse_index[0] * editorsize, mouse_index[1] * editorsize), editormode[0], editorsize, True)
                    firstheldmousepos = mousepos
                    if not non_preview_block == prev_non_preview_block:
                        return_sound_trigger = "preview"
                    prev_non_preview_block = non_preview_block
            elif clickmode == "drag" or not mouseheldpos == [(), ()]:
                mousepos = ((mousepos[0] if not mousepos[0] < 0 else 0) if not mousepos[0] > width * editorsize - ((editorsize / 2) if width % 2 == 0 else 0) else width * editorsize - ((editorsize / 2) if width % 2 == 0 else 0),
                            (mousepos[1] if not mousepos[1] < 0 else 0) if not mousepos[1] > height * editorsize - ((editorsize / 2) if height % 2 == 0 else 0) else height * editorsize - ((editorsize / 2) if height % 2 == 0 else 0))
                if not editormode[1] in ("spawnpoint", "spike", "end"):
                    if rightmousedown[1]:
                        mouseheldpos = [(round((mousepos[0] - 15) / editorsize) * editorsize, round((mousepos[1] - 15) / editorsize) * editorsize), ()]
                        firstheldmousepos = mouseheldpos[0]
                    if rightmousedown[0]:
                        box_direction = ["right" if mouseheldpos[0][0] <= mousepos[0] else "left", "down" if mouseheldpos[0][1] <= mousepos[1] else "up"]
                        if not [(round((firstheldmousepos[0] + (30 if box_direction[0] == "left" else 0)) / editorsize) * editorsize, round((firstheldmousepos[1] + (30 if box_direction[1] == "up" else 0)) / editorsize) * editorsize), (round(mousepos[0] / editorsize) * editorsize, round(mousepos[1] / editorsize) * editorsize)] == mouseheldpos:
                            return_sound_trigger = "drag"
                        mouseheldpos = [(round((firstheldmousepos[0] + (30 if box_direction[0] == "left" else 0)) / editorsize) * editorsize, round((firstheldmousepos[1] + (30 if box_direction[1] == "up" else 0)) / editorsize) * editorsize), (round(mousepos[0] / editorsize) * editorsize, round(mousepos[1] / editorsize) * editorsize)]
                        if mouseheldpos[0] == ():
                            mouseheldpos = [(round((mousepos[0] - 15) / editorsize) * editorsize, round((mousepos[1] - 15) / editorsize) * editorsize), ()]
                            firstheldmousepos = mouseheldpos[0]
                    elif not rightmousedown[0] and not mouseheldpos == [(), ()]:
                        mouseheldpos[1] = (int(mousepos[0] / editorsize) * editorsize, int(mousepos[1] / editorsize) * editorsize)
                        return_sound_trigger = "place"
                        if editormode[1] == "end":
                            end_placed = True
                        mouseheldpos = [(), ()]
    leveldata = set_block_orientation(leveldata, 30, False)[0]
    return return_sound_trigger


def remove_preview(optimize_leveldata=False):
    global leveldata, mousedown, clickmode, non_preview_block
    if non_preview_block is not None:
        leveldata[int(non_preview_block.position[1] / editorsize)][
            int(non_preview_block.position[0] / editorsize)] = non_preview_block
        non_preview_block = None
    if optimize_leveldata:
        leveldata = set_block_orientation(leveldata, 30, False)[0]


def remove_end_gradient():
    global leveldata, end_placed, end_direction
    for rowindex, row in enumerate(leveldata):
        for itemindex, item in enumerate(row):
            if item.type == "end":
                leveldata[rowindex][itemindex] = Block((itemindex * editorsize, rowindex * editorsize), "0", editorsize)
    end_placed, end_direction = False, None
    leveldata = set_block_orientation(leveldata, 30, False)[0]


def fill_rect(rect):
    global leveldata, entities
    if not rect.x > (width - 1) * editorsize and not rect.y > (height - 1) * editorsize:
        for rowindex in range(int(rect.h / editorsize)):
            for itemindex in range(int(rect.w / editorsize)):
                if leveldata[int(rect.y / editorsize + rowindex)][int(rect.x / editorsize + itemindex)].type == "end":
                    remove_end_gradient()
                elif leveldata[int(rect.y / editorsize + rowindex)][int(rect.x / editorsize + itemindex)].type == "spawnpoint":
                    for index, entity in enumerate(entities):
                        if entity[3] == (int(rect.x / editorsize + itemindex) * editorsize, int(rect.y / editorsize + rowindex) * editorsize):
                            entities.pop(index)
                leveldata[int(rect.y / editorsize + rowindex)][int(rect.x / editorsize + itemindex)] = Block(
                    (rect.x + (itemindex * editorsize), rect.y + (rowindex * editorsize)), editormode[0], editorsize)

        wait_thats_illegal()
        leveldata = set_block_orientation(leveldata, 30, False)[0]


def wait_thats_illegal():
    global leveldata
    for rowindex, row in enumerate(leveldata):
        for itemindex, item in enumerate(row):
            if item.type == "spike":
                if (((rowindex == (len(leveldata) - 1)) or not leveldata[rowindex + 1][itemindex].type in ("solid", "nonstickysolid")) and
                 ((rowindex == 0) or not leveldata[rowindex - 1][itemindex].type in ("solid", "nonstickysolid")) and
                 ((itemindex == (len(leveldata[0]) - 1)) or not leveldata[rowindex][itemindex + 1].type in ("solid", "nonstickysolid")) and
                 ((itemindex == 0) or not leveldata[rowindex][itemindex - 1].type in ("solid", "nonstickysolid"))):
                    leveldata[rowindex][itemindex] = Block(item.position, "0", item.size)


def save_level():
    global blocksize, entities
    converter_key = {
            "air": "0",
            "solid": "1",
            "nonstickysolid": "i",
            "spike": "2",
            "lava": "3",
            "spawnpoint": "x",
            "end": "e"
        }
    with open("leveldata/editorsavefile", "w") as f:
        f.write(str(blocksize) + "\n")
        for row in leveldata:
            for item in row:
                if item.type == "spawnpoint":
                    for entity in entities:
                        if entity[3] == item.position:
                            f.write(entity[0] + " " + str(entity[1]) + " " + entity[2] + "\n")
        for rowindex, row in enumerate(leveldata):
            for item in row:
                f.write(converter_key[item.type] + " ")
            if not rowindex == len(leveldata) - 1:
                f.write("\n")


def load_level():
    global leveldata, blocksize, entities, end_placed, end_direction, width, height
    txt = open("leveldata/editorsavefile", "r").read()
    level, leveldata, entitydata, entities, end_placed = txt.split("\n"), [], [], [], False
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
    for rowindex, row in enumerate(leveldata):  # convert strings to block class
        for itemindex, item in enumerate(row):
            leveldata[rowindex][itemindex] = Block((itemindex * editorsize, rowindex * editorsize), item, editorsize)
            if leveldata[rowindex][itemindex].type == "spawnpoint":
                entities.append((entitydata[0][0], entitydata[0][1], entitydata[0][2], (itemindex * editorsize, rowindex * editorsize)))
                entitydata.pop(0)
            elif leveldata[rowindex][itemindex].type == "end":
                end_placed = True
                end_direction = "down" if rowindex == 0 else "up" if rowindex == (len(leveldata) - 1) else "right" if itemindex == 0 else "left"
    width, height = len(leveldata[0]), len(leveldata)


def adjust_dimensions():
    global width, height
    if width > len(leveldata[0]):
        for rowindex, row in enumerate(leveldata):
            row.append(Block(((width - 1) * editorsize, rowindex * editorsize), "0", editorsize))
    elif width < len(leveldata[0]):
        for row in leveldata:
            row.pop(-1)
    if height > len(leveldata):
        leveldata.append([])
        for index in range(width):
            leveldata[-1].append(Block((index * editorsize, (height - 1) * editorsize), "0", editorsize))
    elif height < len(leveldata):
        leveldata.pop(-1)
