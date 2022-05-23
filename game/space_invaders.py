import random
import time


class Level:
    def __init__(self, lvl: int, x: int = 10, y: int = 5):
        self.lvl = lvl
        self.aliens = []
        self.bullets = []
        self.x = x
        self.waves = 1
        self.y = y
        self.ship = (0, 0)
        for _ in range(self.x // 2):
            self.spawn_alien()
        self.spawn_ship()

    def get_board(self):
        board = []
        for x in range(self.x):
            board.append([])
            for y in range(self.y):
                board[x].append({})
        for alien in self.aliens:
            x, y = alien["pos"]
            board[x][y] = {"alien": True}
        x, y = self.ship
        board[x][y] = {"ship": True}
        return board

    def spawn_alien(self):
        dat = {"pos": (random.randrange(self.x), 0)}
        if dat not in self.aliens:
            self.aliens.append(dat)
        else:
            self.spawn_alien()

    def update(self):
        for i in range(len(self.aliens)):
            self.aliens[i]["pos"] = (
                self.aliens[i]["pos"][0],
                self.aliens[i]["pos"][1] + 1,
            )
        if self.waves < self.lvl:
            for _ in range(self.x // 2):
                self.spawn_alien()
            self.waves += 1
        return self.get_board()

    def spawn_ship(self):
        ship_x = self.x // 2
        self.ship = (ship_x, -1)
        print("ship_pos ", self.ship)

    def control_ship(self, way: str):
        if way == "left":
            if self.ship[0] == 0:
                self.ship = (self.x - 1, -1)
            else:
                self.ship = (self.ship[0] - 1, -1)
        elif way == "right":
            if self.ship[0] == self.x - 1:
                self.ship = (0, -1)
            else:
                self.ship = (self.ship[0] + 1, -1)
        print("ship_pos ", self.ship)
        return self.update()


def new(lvl: int, rows: int, cols: int):
    return Level(lvl, rows, cols)
