from constants import (WEDNESDAY,
                       SATURDAY, SUNDAY)
from constants import MAX_PLAYER_COUNT
from ranks import RankCreator, Normal
from utils import day_to_number


class Player:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.point = 0
        self.weekly_attend_counts = [0] * 7
        self.rank = RankCreator.create_rank(0)

    def add_basic_points(self, day_of_week: str):
        add_point = 1
        day_number = day_to_number(day_of_week)
        if day_number == WEDNESDAY:
            add_point = 3
        if day_number in (SATURDAY, SUNDAY):
            add_point = 2

        self.weekly_attend_counts[day_number] += 1
        self.point += add_point

    def add_bonus_points(self):
        if self.weekly_attend_counts[WEDNESDAY] >= 10:
            self.point += 10
        if self.weekly_attend_counts[SATURDAY] + self.weekly_attend_counts[SUNDAY] >= 10:
            self.point += 10

    def set_attendance_rank(self):
        self.rank = RankCreator().create_rank(self.point)

    def print_info(self):
        print(f"NAME : {self.name}, POINT : {self.point}, GRADE : ", end="")
        rank_string = self.rank.get_rank_string()
        print(rank_string)

    def is_bad_player(self):
        return (isinstance(self.rank, Normal)
                and self.weekly_attend_counts[WEDNESDAY] == 0
                and self.weekly_attend_counts[SATURDAY] == 0
                and self.weekly_attend_counts[SUNDAY] == 0)


class PlayerManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PlayerManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.players = dict()

    def get_player(self, player_name):
        if player_name not in self.players:
            if len(self.players) == MAX_PLAYER_COUNT:
                raise Exception(f"Max player count reached, new player {player_name} can not be added")
            player = Player(player_name, len(self.players) + 1)
            self.players[player_name] = player
        return self.players[player_name]

    def update_attendance(self, player_name, day_of_week):
        player = self.get_player(player_name)
        player.add_basic_points(day_of_week)

    def evaluate_players_info(self):
        for player in self.players.values():
            player.add_bonus_points()
            player.set_attendance_rank()

    def print_players_info(self):
        for player in self.players.values():
            player.print_info()

    def print_removed_players(self):
        print("\nRemoved player")
        print("==============")
        for player in self.players.values():
            if player.is_bad_player():
                print(player.name)
