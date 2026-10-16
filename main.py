class Vector:
    def __init__(self, x_1, y_1, x_2, y_2):
        self.x_1 = x_1
        self.y_1 = y_1
        self.x_2 = x_2
        self.y_2 = y_2
        self.claimed = False
        self.ownership = ""
    def __repr__(self):
        return (
            f"Vector(({self.x_1}, {self.y_1})"
            f" -> ({self.x_2}, {self.y_2}))"
        )
    def claim(self, playerId):
        self.claimed = True
        self.ownership = playerId


class GameEngine:
    def __init__(self):
        self.grid_size = 5
        self.claimed_boxes = set()
        self.player_one_boxes = 0
        self.player_two_boxes = 0
        self.player_one_symbol = "@"
        self.player_two_symbol = "!"
        self.player_one_turn = True
        self.grid_vectors = {}
        self.total_boxes = (self.grid_size - 1 )**2
        self.running = True
        self.possible_actions = ["QUIT", "CLAIM", "RESTART"]

    def generate_grid(self):
        vector_id = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size - 1):
                key = "H" + str(vector_id)
                self.grid_vectors[key] = Vector(x, y, x + 1, y)
                vector_id += 1

        for y in range(self.grid_size - 1):
            for x in range(self.grid_size):
                key = "V" + str(vector_id)
                self.grid_vectors[key] = Vector(x, y, x, y + 1)
                vector_id += 1

    def draw_grid(self):
        for y in range(self.grid_size):
            line = ""
            for x in range(self.grid_size):
                line += "#"

                if x < self.grid_size - 1:
                    vector_id = y * (self.grid_size - 1) + x
                    vector_name = "H" + str(vector_id)

                    vector = self.grid_vectors[vector_name]
                    line += f" {3* vector.ownership} " if vector.claimed else f" {vector_name} "

            print(line)

            # Draw Vertical lines
            if y < self.grid_size - 1:
                line = ""
                for x in range(self.grid_size):
                    vector_id = (
                        self.grid_size * (self.grid_size - 1) + y * self.grid_size + x
                    )
                    vector_name = "V" + str(vector_id)

                    vector = self.grid_vectors[vector_name]
                    line += f"{vector.ownership}   " if vector.claimed else f"{vector_name} "

                print(line)

    def is_box_complete(self, x, y):

        # Horizontal lines: top and bottom
        top_id = "H" + str(y * (self.grid_size - 1) + x)
        bottom_id = "H" + str((y + 1) * (self.grid_size - 1) + x)

        # Vertical lines: left and right
        vertical_start = self.grid_size * (self.grid_size - 1)
        left_id = "V" + str(vertical_start + y * self.grid_size + x)
        right_id = "V" + str(vertical_start + y * self.grid_size + x + 1)

        sides = [
            self.grid_vectors[top_id],
            self.grid_vectors[bottom_id],
            self.grid_vectors[left_id],
            self.grid_vectors[right_id]
        ]

        return all(vector.claimed for vector in sides)

    def check_for_box(self, claim_id):

        vector = self.grid_vectors[claim_id]

        x1, y1 = vector.x_1, vector.y_1
        x2, y2 = vector.x_2, vector.y_2

        # check for horizontal
        if y1 == y2:
            x = min(x1, x2)
            y = y1

            candidates = []

            # check above
            if y > 0:
                candidates.append((x, y - 1))

            # check below
            if y < self.grid_size - 1:
                candidates.append((x, y))

        else:  # check if vertical
            x = x1
            y = min(y1, y2)

            candidates = []

            # check left
            if x > 0:
                candidates.append((x - 1, y))

            # check right
            if x < self.grid_size - 1:
                candidates.append((x, y))

        boxes_completed = 0

        for box_x, box_y in candidates:
            box = (box_x, box_y)

            if box not in self.claimed_boxes and self.is_box_complete(
                    box_x, box_y
            ):
                self.claimed_boxes.add(box)
                boxes_completed += 1

                if vector.ownership == self.player_one_symbol:
                    self.player_one_boxes += 1
                else:
                    self.player_two_boxes += 1

                print(
                    f"Player {vector.ownership} claimed box "
                )

        return boxes_completed

    def validate_game(self):
        if len(self.claimed_boxes) == self.total_boxes:
            print(f"Total Score \n PlayerOne: {self.player_one_boxes} \n PlayerTwo: {self.player_two_boxes}")
            if self.player_one_boxes > self.player_two_boxes:
                print("Player one wins!")
            elif self.player_two_boxes > self.player_one_boxes:
                print("Player two wins!")
            else:
                print("It's a draw!")
            self.running = False

    def game_loop(self):
        while(self.running):
            self.validate_game()
            if (self.player_one_turn):
                player_symbol = self.player_one_symbol
            else:
                player_symbol = self.player_two_symbol

            print(f"Player {player_symbol} turn")
            action = input(f"What do you want to do? {self.possible_actions}")
            if (action not in self.possible_actions):
                print("Invalid action")
            elif (action == "QUIT"):
                break
            elif (action == "CLAIM"):
                claim_id = input("Which line do you wish to claim?")
                if (claim_id in self.grid_vectors and not self.grid_vectors[claim_id].claimed):
                    self.grid_vectors[claim_id].claim(player_symbol)
                    self.check_for_box(claim_id)
                    self.draw_grid()
                    self.player_one_turn = not self.player_one_turn
                else:
                    print("Vector already claimed or does not exist")




if __name__ == '__main__':
    Game = GameEngine()
    Game.generate_grid()
    Game.draw_grid()
    Game.game_loop()




