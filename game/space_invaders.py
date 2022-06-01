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
alien_models = {"cod": {"launcher": projectile_launchers["cod"], "hp": 1, "speed": 0.5}}


class Alien:
    """represents an alien"""

    def __init__(
        self, level, x: int, y: int, model=alien_models["cod"], dmg_multi=1
    ) -> None:
        self.level = level
        self.pos = (x, y)
        self.model = model
        self.dmg_multi = dmg_multi
        self.speed = model["speed"]

    async def update(self):
        x, y = self.pos
        """
        alien movement
        """
        if x == 0 and self.pos[1] % 2 or x == self.level.x - 1 and not self.pos[1] % 2:
            self.pos = (int(self.pos[0]), int(self.pos[1] + 1))
        elif self.pos[1] % 2:
            self.pos = (int(self.pos[0] - 1), int(self.pos[1]))
        else:
            self.pos = (int(self.pos[0] + 1), int(self.pos[1]))

    async def hit(self, dmg):
        """to be run when a projectile and alien are in same tile"""
        self.model["hp"] -= dmg
        if self.model["hp"] <= 0:
            return self.level.aliens_to_despawn.append(self)


class Projectile:
    """represents a bullet"""

    def __init__(
        self,
        level,
        x: int,
        y: int,
        launcher=projectile_launchers["gun"],
        dmg_multi=1,
    ) -> None:
        self.level = level
        self.pos = (x, y - 1)
        self.launcher = launcher
        self.dmg_multi = dmg_multi

    async def update(self):
        if self.pos[1] == 0:
            return self.level.projectiles_to_despawn.append(self)
        self.pos = (self.pos[0], int(self.pos[1] - self.launcher["speed"]))


class Level:
    """
    represents a running game
    """

    def __init__(self, launcher: dict, lvl: int, x: int = 10, y: int = 5):
        self.lvl = lvl
        self.aliens = []
        self.projectiles = []
        self.x, self.y = x, y
        self.launcher = launcher
        self.firerate = launcher["firerate"]
        self.waves = 1
        self.hp = launcher["hp"]
        self.alien_speed = 0.5
        self.ship = (0, 0)
        self.projectiles_to_despawn = []
        self.aliens_to_despawn = []
        self.spawn_alien()
        self.spawn_ship()

    async def get_board(self) -> dict:
        """dynamically generate a board with details of the ongoing game

        Returns:
            dict: board
        """
        board = []
        for x in range(self.x):
            board.append([])
            for y in range(self.y):
                board[x].append({})
        for alien in self.aliens:
            x, y = alien.pos
            board[x][y] = {"alien": True}
        for bullet in self.projectiles:
            x, y = bullet.pos
            print("bullet: ", x, ",", y)
            board[x][y].update({"bullet": True})
        x, y = self.ship
        board[x][y] = {"ship": True}
        return {"board": board}

    def spawn_alien(self):
        self.aliens.append(Alien(self, 0, 0))

    async def spawn_projectile(self):
        """spawn a bullet at the position of ship"""
        self.projectiles.append(
            Projectile(
                self,
                self.ship[0],
                self.ship[1] + 1,
                self.launcher,
            )
        )

    async def update(self) -> dict:
        """update 1 frame and return the updated board

        Returns:
            dict: board
        """
        if self.waves == self.lvl and self.aliens == []:
            return {"win": True,"level": self.lvl}
        elif self.hp <= 0:
            return {"lose": True}
        """
        update/spawn projectiles
        """
        if self.firerate >= 1:
            self.firerate -= 1
            await self.spawn_projectile()
        else:
            self.firerate += self.launcher["firerate"]
        for projectile in self.projectiles:
            await projectile.update()
        """
        update/spawn aliens
        """
        for alien in self.aliens:
            await alien.update()
        if self.waves < self.lvl:
            if random.choice([True, False, True, True]):
                self.spawn_alien()
                self.waves += 1
        """
        prepare to despawn projectiles and aliens
        """
        for alien in self.aliens:
            for projectile in self.projectiles:
                if alien.pos == projectile.pos:
                    self.aliens_to_despawn.append(alien)
                    if projectile.launcher["pen"] <= 0:
                        self.projectiles_to_despawn.append(projectile)
                    else:
                        projectile.launcher["pen"] -= 1
                        projectile.launcher["dmg"] -= 1
            if alien.pos[1] == self.y - 1:
                self.hp -= 1
                self.aliens_to_despawn.append(alien)
        for alien in self.aliens_to_despawn:
            try:
                self.aliens.remove(alien)
            except ValueError:
                pass
        for projectile in self.projectiles_to_despawn:
            try:
                self.projectiles.remove(projectile)
            except ValueError:
                pass
        self.aliens_to_despawn, self.projectiles_to_despawn = [], []
        return await self.get_board()

    def spawn_ship(self):
        """spawn ship at center of x axis and at the last row of board"""
        ship_x = self.x // 2
        self.ship = (ship_x, self.y - 1)
        print("ship_pos ", self.ship)

    async def control_ship(self, way: str) -> dict:
        """change ship pos, update 1 frame and return the updated board

        Args:
            way (str): "left" | "right"

        Returns:
            dict: board
        """
        if way == "left":
            if self.ship[0] == 0:
                self.ship = (int(self.x - 1), int(self.y - 1))
            else:
                self.ship = (int(self.ship[0] - 1), int(self.y - 1))
        elif way == "right":
            if self.ship[0] == self.x - 1:
                self.ship = (0, self.y - 1)
            else:
                self.ship = (int(self.ship[0] + 1), int(self.y - 1))
        return await self.update()


def new(launcher: dict, lvl: int, x: int, y: int) -> Level:
    """start a new game

    Args:
        launcher (dict): player ship stats
        lvl (int): level/difficulty of the game
        x (int): len of x axis
        y (int): len of y axis

    Returns:
        Level : game
    """
    return Level(launcher, lvl, x, y)
