from abc import ABC


class Rank(ABC):
    def get_rank_string(self):
        ...


class Normal(Rank):
    def get_rank_string(self):
        return "NORMAL"


class Gold(Rank):
    def get_rank_string(self):
        return "GOLD"


class Silver(Rank):
    def get_rank_string(self):
        return "SILVER"


class RankCreator():
    @staticmethod
    def create_rank(point: int):
        if point >= 50:
            return Gold()
        if point >= 30:
            return Silver()
        return Normal()
