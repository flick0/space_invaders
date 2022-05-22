import random


class Level:
    def __init__(self, lvl: int, row: int = 5, col: int = 5):
        self.lvl = lvl
        self.board = []
        self.row = row
        self.col = col
        for r in range(row):
            line = []
            for c in range(col):
                if r <= row // 2:
                    line.append({"alien": True})
            self.board.append(line)

        """example board

        [
            [
                {"alien":True},{"alien":True},{"alien":True,"bullet":True}
            ],
            [
                {},{},{}
            ],
            [
                {},{},{"ship":True}
            ]
        ]

        3 rows 3 columns
        
        (alien)(alien)(injured alien) 
        (     )(     )(     ) 
        (     )(     )(ship ) 

        """
        self.spawn_ship()

    def get_board(self):
        return self.board

    def spawn_ship(self):
        ship_x = random.randrange(self.col)
        self.board[-1] = [
            {"ship": True} if x == ship_x else {} for x in range(self.col)
        ]
        self.ship = (len(self.board) - 1, ship_x)
        print("ship_pos ", self.ship)
        """
        (y_pos,x_pos)
        """

    def control_ship(dir: str):
        ...


def new(lvl: int, rows: int, cols: int):
    return Level(lvl, rows, cols)
