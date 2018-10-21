
class PlayerFactory:

    def __init__(self):
        self.player_list = []

    def create(self):
        new_player = Player()
        new_player.player_num = len(self.player_list)
        self.player_list.append(new_player)

class Player:

    def __init__(self):
        self.player_num = None