from pygame import Rect
from possible_adjacent_combinations import indexloop, set_solid_block_texture


class Block:
    def __init__(self, position, blocktype, blocksize, transparent=False):
        self.position = position
        self.size = blocksize
        self.bordering_blocks = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
        self.hitbox = Rect(position[0], position[1], blocksize, blocksize)
        self.type = {
            "0": "air",
            "1": "solid",
            "i": "nonstickysolid",
            "2": "spike",
            "3": "lava",
            "x": "spawnpoint",
            "X": "spawnpoint",
            "e": "end",
        }[blocktype]
        if self.type in ("spike", "lava"):
            self.hitbox = Rect(position[0] + blocksize / 4, position[1] + blocksize / 4, blocksize - ((blocksize / 4) * 2), blocksize / 0.75)
            self.bordering_blocks, self.index = "none", None
            self.ripple_offset = []
        elif self.type in "solid, nonstickysolid, lava":
            self.draw_3d_threshold = [False, False, False, False]  # upper, lower, rightmost, leftmost
        self.render3D = True if self.type in ("spike", "solid", "nonstickysolid") else False
        self.transparent = transparent

    def __repr__(self):
        return f"{self.type} Block at {self.position} ({self.transparent})"

    def get_lava_offset(self, lava_timer):
        val = indexloop(indexloop(self.index * 1.4 + lava_timer, 79), 79)
        val = ((((pow(val, 2) * 0.05) + (val * -2) + 0.1) if val < 40 else ((pow(val - 40, 2) * 0.05) + ((val - 40) * -2) + 0.1) * -1) / 2 - 10) * (self.size / 50)
        val2 = (((((20 * pow(0.65, self.ripple_offset[1]) - 20) if self.ripple_offset[1] < 10 else (0.31 * pow(1.28, (self.ripple_offset[1] - 10)) - 20.2)) if self.ripple_offset[1] < 25 else (-8.7 * pow(0.778, (self.ripple_offset[1] - 25)) - 0.7)) / 10) * abs(self.ripple_offset[0])) * (self.size / 50)
        if self.bordering_blocks == "up" or self.bordering_blocks == "down":
            pos = (self.position[0], self.position[1] - (val + val2) * (1 if self.bordering_blocks == "up" else -1))
        else:
            pos = (self.position[0] - (val + val2) * (1 if self.bordering_blocks == "left" else -1), self.position[1])
        return pos


def set_block_orientation(leveldata, blocksize, return_endpoint_data=True):  # I hate this code
    solids, blocks_with_empty_space = ("solid", "nonstickysolid"), ("air", "spawnpoint", "spike", "end")
    endposavg, end_direction, end_hitboxes, lava_layer, bugfix_end_grad = [[], []], None, [], [[], []], []
    for rowindex, row in enumerate(leveldata):  # auto-orient spikes / other deco
        for itemindex, item in enumerate(row):  # I know this part is horribly written but it was the only thing i could come up with in such short notice that worked
            if item.type in solids:
                if type(item.bordering_blocks) == int:
                    item.bordering_blocks = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
                if rowindex == 0 or itemindex == 0 or leveldata[rowindex - 1][itemindex - 1].type in solids:
                    item.bordering_blocks[0][0] = 1
                if rowindex == 0 or leveldata[rowindex - 1][itemindex].type in solids:
                    item.bordering_blocks[0][1] = 1
                if rowindex == 0 or itemindex == len(row) - 1 or leveldata[rowindex - 1][itemindex + 1].type in solids:
                    item.bordering_blocks[0][2] = 1
                if itemindex == 0 or leveldata[rowindex][itemindex - 1].type in solids:
                    item.bordering_blocks[1][0] = 1
                if item.type in solids:
                    item.bordering_blocks[1][1] = 1
                if itemindex == len(row) - 1 or leveldata[rowindex][itemindex + 1].type in solids:
                    item.bordering_blocks[1][2] = 1
                if rowindex == len(leveldata) - 1 or itemindex == 0 or leveldata[rowindex + 1][itemindex - 1].type in solids:
                    item.bordering_blocks[2][0] = 1
                if rowindex == len(leveldata) - 1 or leveldata[rowindex + 1][itemindex].type in solids:
                    item.bordering_blocks[2][1] = 1
                if rowindex == len(leveldata) - 1 or itemindex == len(row) - 1 or leveldata[rowindex + 1][itemindex + 1].type in solids:
                    item.bordering_blocks[2][2] = 1
                if item.bordering_blocks == [[1, 1, 1], [1, 1, 1], [1, 1, 1]]:
                    item.render3D = False
                item.bordering_blocks = set_solid_block_texture(item.bordering_blocks)
            elif item.type == "spike":
                if not rowindex == len(leveldata) - 1 and leveldata[rowindex + 1][itemindex].type in solids:
                    item.bordering_blocks = "up"
                    item.hitbox = Rect(item.position[0] + blocksize / 4, item.position[1] + blocksize / 4, blocksize - ((blocksize / 4) * 2), blocksize * 0.75)
                elif not rowindex == 0 and leveldata[rowindex - 1][itemindex].type in solids:
                    item.bordering_blocks = "down"
                    item.hitbox = Rect(item.position[0] + blocksize / 4, item.position[1], blocksize - ((blocksize / 4) * 2), blocksize * 0.75)
                elif not itemindex == 0 and leveldata[rowindex][itemindex - 1].type in solids and (rowindex == len(leveldata) - 1 or not leveldata[rowindex + 1][itemindex].type in solids):
                    item.bordering_blocks = "right"
                    item.hitbox = Rect(item.position[0], item.position[1] + blocksize / 4, blocksize * 0.75, blocksize - ((blocksize / 4) * 2))
                elif (not itemindex == len(row) - 1) and leveldata[rowindex][itemindex + 1].type in solids and (rowindex == len(leveldata) - 1 or not leveldata[rowindex + 1][itemindex].type in solids):
                    item.bordering_blocks = "left"
                    item.hitbox = Rect(item.position[0] + blocksize / 4, item.position[1] + blocksize / 4, blocksize * 0.75, blocksize - ((blocksize / 4) * 2))
                if item.type == "spike" and item.bordering_blocks == 'none':
                    item.bordering_blocks = "up"
            elif item.type == "lava":
                item.bordering_blocks = "none"
                if not rowindex == 0 and leveldata[rowindex - 1][itemindex].type in blocks_with_empty_space:
                    item.bordering_blocks, item.hitbox = "up", Rect(item.position[0] + blocksize / 4, item.position[1] + blocksize / 4, blocksize - ((blocksize / 4) * 2), blocksize * 0.75)
                elif not rowindex == len(leveldata) - 1 and leveldata[rowindex + 1][itemindex].type in blocks_with_empty_space:
                    item.bordering_blocks, item.hitbox = "down", Rect(item.position[0] + blocksize / 4, item.position[1], blocksize - ((blocksize / 4) * 2), blocksize * 0.75)
                elif not itemindex == len(row) - 1 and leveldata[rowindex][itemindex + 1].type in blocks_with_empty_space and (rowindex == len(leveldata) - 1 or not leveldata[rowindex + 1][itemindex].type in blocks_with_empty_space):
                    item.bordering_blocks, item.hitbox = "right", Rect(item.position[0], item.position[1] + blocksize / 4, blocksize * 0.75, blocksize - ((blocksize / 4) * 2))
                elif not itemindex == 0 and leveldata[rowindex][itemindex - 1].type in blocks_with_empty_space and (rowindex == len(leveldata) - 1 or not leveldata[rowindex + 1][itemindex].type in blocks_with_empty_space):
                    item.bordering_blocks, item.hitbox = "left", Rect(item.position[0] + blocksize / 4, item.position[1] + blocksize / 4, blocksize * 0.75, blocksize - ((blocksize / 4) * 2))
                if not item.bordering_blocks == "none":
                    item.render3D, item.index, item.ripple_offset = True, itemindex if item.bordering_blocks == "down" or item.bordering_blocks == "up" else rowindex, [0, 0]
                    lava_layer[1].append(item)
                else:
                    lava_layer[0].append(item)
            elif item.type == "end":
                adjacents = (leveldata[rowindex - 1][itemindex].type if rowindex > 0 else "air", leveldata[rowindex + 1][itemindex].type if rowindex < len(leveldata) - 1 else "air",
                             leveldata[rowindex][itemindex - 1].type if itemindex > 0 else "air", leveldata[rowindex][itemindex + 1].type if itemindex < len(row) - 1 else "air")
                endposavg[0].append(item.position[0])
                endposavg[1].append(item.position[1])
                if "end" not in adjacents:
                    pass
                if rowindex == len(leveldata) - 1:
                    item.bordering_blocks, item.hitbox = "up", Rect(item.position[0], item.position[1] + blocksize * 2, blocksize, blocksize)
                elif rowindex == 0:
                    item.bordering_blocks, item.hitbox = "down", Rect(item.position[0], item.position[1] - blocksize * 2, blocksize, blocksize)
                elif itemindex == 0:
                    item.bordering_blocks, item.hitbox = "right", Rect(item.position[0] - blocksize * 2, item.position[1], blocksize, blocksize)
                elif itemindex == len(row) - 1:
                    item.bordering_blocks, item.hitbox = "left", Rect(item.position[0] + blocksize * 2, item.position[1], blocksize, blocksize)
                else:
                    raise Exception("invalid endpoint (not at edge)")
                end_direction = item.bordering_blocks
                end_hitboxes.append(item.hitbox)
    if return_endpoint_data:
        bugfix_end_grad = [Block((endposavg[0][0] - blocksize, endposavg[1][0]), "e", blocksize), Block((endposavg[0][len(endposavg[0]) - 1] + blocksize, endposavg[1][0]), "e", blocksize)] if end_direction == "up" or end_direction == "down" else [Block((endposavg[0][0], endposavg[1][0] - blocksize), "e", blocksize), Block((endposavg[0][0], endposavg[1][len(endposavg[1]) - 1] + blocksize), "e", blocksize)]
        bugfix_end_grad[0].bordering_blocks, bugfix_end_grad[1].bordering_blocks = end_direction, end_direction
        if leveldata[int(bugfix_end_grad[0].position[1] / blocksize)][int(bugfix_end_grad[0].position[0] / blocksize)].type in ("air" or "solid"):
            bugfix_end_grad.pop(0)
        if not (int(bugfix_end_grad[len(bugfix_end_grad) - 1].position[0] / blocksize) == len(leveldata[0])):
            if leveldata[int(bugfix_end_grad[len(bugfix_end_grad) - 1].position[1] / blocksize)][int(bugfix_end_grad[len(bugfix_end_grad) - 1].position[0] / blocksize)].type in ("air" or "solid"):
                bugfix_end_grad.pop(len(bugfix_end_grad) - 1)
    return leveldata if not return_endpoint_data else leveldata, endposavg, end_direction, end_hitboxes, lava_layer, bugfix_end_grad
