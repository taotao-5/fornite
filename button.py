from pygame import Rect, transform


class Button:
    def __init__(self, texture, position, shadow_offset=1, position_offset=None, notrigger=False):
        if position_offset is None:
            position_offset = [0, 0]
        self.position = position
        self.position_offset = position_offset
        self.texture, self.source_texture = texture, texture
        self.shadow_offset = shadow_offset
        self.width, self.height = self.texture.get_width() * self.shadow_offset, self.texture.get_height() * self.shadow_offset
        self.hitbox = None
        self.size_offset = 0.9
        self.zoom_offset = 0
        self.texture = transform.smoothscale(self.source_texture, (int(self.source_texture.get_width() * self.size_offset), int(self.source_texture.get_height() * self.size_offset)))
        self.mouse_touching_timer = 0
        self.update_hitbox()
        self.clicked, self.held = True, False
        self.notrigger = notrigger

    def iterate(self, mousepos, mousedown, scale=False):
        if not self.zoom_offset == 0:
            self.size_offset = 0.9 + self.zoom_offset
            self.texture = transform.smoothscale(self.source_texture, (int(self.source_texture.get_width() * self.size_offset), int(self.source_texture.get_height() * self.size_offset)))
        if not self.notrigger:
            self.update_hitbox()
            if self.zoom_offset == 0 and self.hitbox.collidepoint(mousepos):
                self.mouse_touching_timer = (self.mouse_touching_timer + 1) if self.mouse_touching_timer < 15 else 15
                self.size_offset = 0.9 + (0.000029629 * pow((self.mouse_touching_timer - 15), 3) + 0.1)
                self.texture = transform.smoothscale(self.source_texture, (int(self.source_texture.get_width() * self.size_offset), int(self.source_texture.get_height() * self.size_offset)))
                self.held = True if mousedown and not self.clicked else False
                self.clicked = True if mousedown else False
                if self.mouse_touching_timer == 1 and self.clicked:
                    self.clicked, self.held = True, False
                if self.clicked and self.held:
                    return "select"
                elif self.mouse_touching_timer == 1:
                    return "hover"
            elif self.zoom_offset == 0 and not self.hitbox.collidepoint(mousepos) and not self.mouse_touching_timer == 0:
                self.mouse_touching_timer = (self.mouse_touching_timer - 1) if self.mouse_touching_timer > 0 else 0
                self.size_offset = 0.9 + (0.000029629 * pow(self.mouse_touching_timer, 3))
                self.texture = transform.smoothscale(self.source_texture, (int(self.source_texture.get_width() * self.size_offset), int(self.source_texture.get_height() * self.size_offset)))
                self.clicked = False

    def update_hitbox(self):
        self.width, self.height = self.texture.get_width() * self.shadow_offset, self.texture.get_height() * self.shadow_offset
        self.hitbox = Rect(self.position[0] - self.width / 2 + self.position_offset[0], self.position[1] - self.height / 2 + self.position_offset[1], self.width, self.height)

    def clickscan(self):
        return True if self.clicked and self.held and not self.mouse_touching_timer == 0 else False

    def reload_texture(self):
        self.texture = transform.smoothscale(self.source_texture, (int(self.source_texture.get_width() * self.size_offset), int(self.source_texture.get_height() * self.size_offset)))
