import pytest
from pytest_mock import MockerFixture
from _pytest.capture import CaptureFixture
import attendance_golden as golden_module
import attendance as sut_module
from player import Player, PlayerManager
from ranks import Normal, Silver, Gold
from utils import day_to_number

from constants import (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY,
                       SATURDAY, SUNDAY)


def test_gold_master(capsys: CaptureFixture):
    golden_module.input_file()
    expected = capsys.readouterr()
    sut_module.run_attendance_system()
    actual = capsys.readouterr()
    assert actual.out == expected.out


def test_read_attendance_file(mocker: MockerFixture):
    raw_data = ("A monday\n"
                "B tuesday\n"
                "C wednesday\n"
                "D thursday\n"
                "E friday\n"
                "F saturday\n"
                "G sunday\n"
                "B monday")
    expected = [["A", "monday"],
                ["B", "tuesday"],
                ["C", "wednesday"],
                ["D", "thursday"],
                ["E", "friday"],
                ["F", "saturday"],
                ["G", "sunday"],
                ["B", "monday"]]
    mocked_file = mocker.mock_open(read_data=raw_data)
    mocker.patch("builtins.open", mocked_file)

    actual = sut_module.read_attendance_file("any")

    assert actual == expected


@pytest.mark.parametrize(
    "player_names",
    [(["A"]),
     (["A", "B"]),
     (["A", "B", "C"]), ]
)
def test_get_player(player_names):
    manager = sut_module.PlayerManager()
    for player_name in player_names:
        player = manager.get_player(player_name)
        assert player.name == player_name

    assert len(manager.players) == len(player_names)


def test_get_player_max():
    manager = sut_module.PlayerManager()
    with pytest.raises(Exception):
        for count in range(101):
            player_name = str(count)
            player = manager.get_player(player_name)
            assert player.name == player_name


@pytest.mark.parametrize(
    "player_names, day_of_weeks",
    [(["A"], ["monday"],),
     (["A", "B"], ["tuesday", "wednesday"],),
     (["A", "B", "C"], ["friday", "saturday", "sunday"]), ]
)
def test_update_attendance(player_names, day_of_weeks):
    manager = sut_module.PlayerManager()
    for player_name, day_of_week in zip(player_names, day_of_weeks):
        manager.update_attendance(player_name, day_of_week)
        player = manager.get_player(player_name)
        day_number = day_to_number(day_of_week)
        assert player.weekly_attend_counts[day_number] == 1


@pytest.mark.parametrize(
    "player_name, day_of_week, expected_added_point",
    [("A", "monday", 1),
     ("A", "tuesday", 1),
     ("B", "wednesday", 3),
     ("B", "thursday", 1),
     ("C", "friday", 1),
     ("C", "saturday", 2),
     ("A", "sunday", 2), ]
)
def test_add_basic_points(player_name, day_of_week, expected_added_point):
    player_number = 1
    player = Player(player_name, player_number)

    player.add_basic_points(day_of_week)

    day_number = day_to_number(day_of_week)
    assert player.point == expected_added_point


@pytest.mark.parametrize(
    "day_string, expected_day_number",
    [("monday", MONDAY),
     ("tuesday", TUESDAY),
     ("wednesday", WEDNESDAY),
     ("thursday", THURSDAY),
     ("friday", FRIDAY),
     ("saturday", SATURDAY),
     ("sunday", SUNDAY), ]
)
def test_day_to_number(day_string, expected_day_number):
    actual_day_number = day_to_number(day_string)

    assert actual_day_number == expected_day_number


@pytest.mark.parametrize(
    "attend_counts, expected_point",
    [([0, 0, 9, 0, 0, 4, 5], 0),
     ([0, 0, 0, 0, 0, 0, 0], 0),
     ([0, 0, 10, 0, 0, 0, 0], 10),
     ([0, 0, 0, 0, 0, 10, 0], 10),
     ([0, 0, 0, 0, 0, 0, 10], 10),
     ([0, 0, 0, 0, 0, 5, 5], 10),
     ([0, 0, 10, 0, 0, 5, 5], 20), ]
)
def test_add_bonus_points(attend_counts, expected_point):
    player_name = "A"
    player_number = 1
    player = Player(player_name, player_number)
    player.weekly_attend_counts = attend_counts

    player.add_bonus_points()

    actual_point = player.point
    assert actual_point == expected_point


@pytest.mark.parametrize(
    "point, expected_rank",
    [(29, Normal),
     (0, Normal),
     (30, Silver),
     (49, Silver),
     (50, Gold),
     (9999999, Gold)]
)
def test_set_attendance_rank(point, expected_rank):
    player_name = "A"
    player_number = 1
    player = Player(player_name, player_number)
    player.point = point

    player.set_attendance_rank()

    assert isinstance(player.rank, expected_rank)


@pytest.mark.parametrize(
    "player_name, player_number, points, rank",
    [("A", 1, 29, Normal()),
     ("B", 2, 30, Silver()),
     ("C", 4, 60, Gold())]
)
def test_print_player_info(capsys, player_name, player_number, points, rank):
    player = Player(player_name, player_number)
    player.point = points
    player.rank = rank
    expected_out = f"NAME : {player_name}, POINT : {points}, GRADE : {rank.get_rank_string()}\n"

    player.print_info()

    actual_out = capsys.readouterr().out
    assert actual_out == expected_out


@pytest.mark.parametrize(
    "player_names, bad_players",
    [(["A", "B", "C"], [False, False, False]),
     (["A", "B", "C"], [True, False, False]),
     (["A", "B", "C"], [False, True, False]),
     (["A", "B", "C"], [True, True, False]),
     (["A", "B", "C"], [False, False, True]),
     (["A", "B", "C"], [True, True, True]), ]
)
def test_print_removed_players(player_names, bad_players, capsys: CaptureFixture, mocker: MockerFixture):
    mock_is_bad_player = mocker.patch("player.Player.is_bad_player", side_effect=bad_players)
    expected_out = ("\nRemoved player\n"
                    "==============\n")
    for player_name, is_bad in zip(player_names, bad_players):
        if is_bad:
            expected_out += f"{player_name}\n"
    manager = PlayerManager()
    for player_number, player_name in enumerate(player_names, 1):
        manager.players[player_name] = Player(player_name, player_number)
    manager.print_removed_players()
    actual_out = capsys.readouterr().out

    assert actual_out == expected_out
    assert mock_is_bad_player.call_count == 3


@pytest.mark.parametrize(
    "weekly_attend_counts, rank, expected_is_bad",
    [([1, 1, 0, 1, 1, 0, 0], Normal, True),
     ([1, 1, 0, 1, 1, 0, 0], Silver, False),
     ([1, 1, 0, 1, 1, 0, 0], Gold, False),
     ([0, 0, 0, 0, 0, 1, 0], Normal, False),
     ([0, 0, 0, 0, 0, 0, 1], Normal, False),
     ([0, 0, 1, 0, 0, 0, 0], Normal, False), ]
)
def test_is_bad_player(weekly_attend_counts, rank, expected_is_bad):
    player = Player("A", 1)
    player.weekly_attend_counts = weekly_attend_counts
    player.rank = rank()
    assert player.is_bad_player() == expected_is_bad


def test_evaluate_players_info(mocker: MockerFixture):
    mock_add_bonus_points = mocker.patch("player.Player.add_bonus_points")
    mock_set_attendance_rank = mocker.patch("player.Player.set_attendance_rank")
    manager = PlayerManager()
    manager.players = {
        "A": Player("A", 1),
        "B": Player("B", 2),
        "C": Player("C", 3),
    }
    manager.evaluate_players_info()

    assert mock_add_bonus_points.call_count == 3
    assert mock_set_attendance_rank.call_count == 3


def test_print_players_info(mocker: MockerFixture):
    mock_print_info = mocker.patch("player.Player.print_info")
    manager = PlayerManager()
    manager.players = {
        "A": Player("A", 1),
        "B": Player("B", 2),
        "C": Player("C", 3),
    }

    manager.print_players_info()

    assert mock_print_info.call_count == 3
