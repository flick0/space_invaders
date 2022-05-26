import random
import time

projectile_launchers = {
    "cod": {"dmg": 0, "collision_dmg": 5, "firerate": 0, "speed": 1, "pen": 0},
    "gun": {
        "dmg": 1,
        "collision_dmg": 5,
        "firerate": 0.5,
        "speed": 1,
        "pen": 0,
    },
}
alien_types = {
    "cod": {
        "launcher": projectile_launchers["cod"],
        "hp": 1,
    }
}


class Alien:
    def __init__(
        self, level, x: int, y: int, model=alien_types["cod"], dmg_multi=1
    ) -> None:
        self.level = level
        self.pos = (x, y)
        self.model = model
        self.dmg_multi = dmg_multi


class Projectile:
    def __init__(
        self,
        level,
        x: int,
        y: int,
        launcher=projectile_launchers["gun"],
        dmg_multi=1,
    ) -> None:
        self.level = level
        self.pos = (x, y)
        self.launcher = launcher
        self.dmg_multi = dmg_multi

    def update(self):
        self.pos = (self.pos[0], self.pos[1] - self.launcher["speed"])
        print("projectile:", self.pos)
        alien = self.contacted()
        if alien:
            # index = self.level.aliens.index(alien)
            # alien.hp - self.launcher["dmg"]
            # self.level.aliens[index] = alien
            self.level.aliens.remove(alien)
            if self.launcher["pen"] != 0:
                self.launcher["pen"] -= 1
            else:
                self.level.projectiles.remove(self)

    def contacted(self):
        for alien in self.level.aliens:
            if alien["pos"] == self.pos:
                return alien


class Level:
    def __init__(self, lvl: int, x: int = 10, y: int = 5):
        self.lvl = lvl
        self.aliens = []
        self.projectiles = []
        self.x = x
        self.launcher = projectile_launchers["gun"]
        self.firerate = self.launcher["firerate"]
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
        for bullet in self.projectiles:
            x, y = bullet.pos
            board[x][y].update({"bullet": True})
        x, y = self.ship
        board[x][y] = {"ship": True}
        return board

    def spawn_alien(self):
        dat = {"pos": (random.randrange(self.x), 0)}
        if dat not in self.aliens:
            self.aliens.append(dat)
        else:
            self.spawn_alien()

    def spawn_projectile(self):
        self.projectiles.append(
            Projectile(
                self,
                self.ship[0],
                self.ship[1] + 1,
                self.launcher,
            )
        )

    def update(self):
        if self.firerate == 1:
            self.firerate = self.launcher["firerate"]
            self.spawn_projectile()
        else:
            self.firerate += self.launcher["firerate"]
        for projectile in self.projectiles:
            projectile.update()

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
        self.ship = (ship_x, self.y - 1)
        print("ship_pos ", self.ship)

    def control_ship(self, way: str):
        if way == "left":
            if self.ship[0] == 0:
                self.ship = (self.x - 1, self.y - 1)
            else:
                self.ship = (self.ship[0] - 1, self.y - 1)
        elif way == "right":
            if self.ship[0] == self.x - 1:
                self.ship = (0, self.y - 1)
            else:
                self.ship = (self.ship[0] + 1, self.y - 1)
        print("ship_pos ", self.ship)
        return self.update()


def new(lvl: int, rows: int, cols: int):
    return Level(lvl, rows, cols)
