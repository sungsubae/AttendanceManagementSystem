import pytest
from pytest_mock import MockerFixture
from _pytest.capture import CaptureFixture
import attendance_golden as golden_module
import attendance as sut_module

NORMAL = 0
GOLD = 1
SILVER = 2
NUM_TO_RANK_DICT = {NORMAL: "NORMAL", GOLD: "GOLD", SILVER: "SILVER"}

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

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
    "player_to_num_dict, player_name",
    [({}, "A"),
     ({"A": 1}, "A"),
     ({"A": 1}, "B")]
)
def test_get_player_number(player_to_num_dict, player_name):
    sut_module.player_to_num_dict = player_to_num_dict
    sut_module.player_count = len(player_to_num_dict)

    actual_player_number = sut_module.get_player_number(player_name)

    assert actual_player_number == player_to_num_dict[player_name]
    assert sut_module.player_count == len(player_to_num_dict)


@pytest.mark.parametrize(
    "player_number, day_of_week, expected_added_point",
    [(1, MONDAY, 1),
     (2, TUESDAY, 1),
     (3, WEDNESDAY, 3),
     (4, THURSDAY, 1),
     (5, FRIDAY, 1),
     (6, SATURDAY, 2),
     (7, SUNDAY, 2),]
)
def test_add_basic_points(mocker: MockerFixture, player_number, day_of_week, expected_added_point):
    original_point = sut_module.points[player_number]
    mock_day_to_number = mocker.patch("attendance.day_to_number", return_value=day_of_week)

    sut_module.add_basic_points(player_number, "day")

    actual_added_point = sut_module.points[player_number] - original_point
    assert actual_added_point == expected_added_point
    assert mock_day_to_number.call_count == 1

@pytest.mark.parametrize(
    "day_string, expected_day_number",
    [("monday", MONDAY),
     ("tuesday", TUESDAY),
     ("wednesday", WEDNESDAY),
     ("thursday", THURSDAY),
     ("friday", FRIDAY),
     ("saturday", SATURDAY),
     ("sunday", SUNDAY),]
)
def test_day_to_number(day_string, expected_day_number):

    actual_day_number = sut_module.day_to_number(day_string)

    assert actual_day_number == expected_day_number

@pytest.mark.parametrize(
    "attend_counts, player_number, expected_point",
    [([0, 0, 9, 0, 0, 4, 5], 1, 0),
     ([0, 0, 0, 0, 0, 0, 0], 1, 0),
     ([0, 0, 10, 0, 0, 0, 0], 1, 10),
     ([0, 0, 0, 0, 0, 10, 0], 1, 10),
     ([0, 0, 0, 0, 0, 0, 10], 1, 10),
     ([0, 0, 0, 0, 0, 5, 5], 1, 10),
     ([0, 0, 10, 0, 0, 5, 5], 1, 20),]
)
def test_add_bonus_points(attend_counts, player_number, expected_point):
    for day in range(MONDAY, SUNDAY + 1):
        sut_module.weekly_attend_counts[player_number][day] = attend_counts[day]
    original_point = sut_module.points[player_number]

    sut_module.add_bonus_points(player_number)

    actual_point = sut_module.points[player_number] - original_point
    assert actual_point == expected_point

@pytest.mark.parametrize(
    "player_number, points, expected_rank",
    [(1, 29, NORMAL),
     (1, 0, NORMAL),
     (2, 30, SILVER),
     (3, 49, SILVER),
     (4, 50, GOLD),
     (5, 9999999, GOLD)]
)
def test_set_attendance_rank(player_number, points, expected_rank):
    sut_module.points[player_number] = points

    sut_module.set_attendance_rank(player_number)
    actual_rank = sut_module.ranks[player_number]

    assert actual_rank == expected_rank

@pytest.mark.parametrize(
    "player_name, player_number, points, rank",
    [("A", 1, 29, NORMAL),
     ("B", 2, 30, SILVER),
     ("C", 4, 60, GOLD)]
)
def test_print_player_info(capsys, player_name, player_number, points, rank):
    sut_module.names[player_number] = player_name
    sut_module.points[player_number] = points
    sut_module.ranks[player_number] = rank
    expected_out = f"NAME : {player_name}, POINT : {points}, GRADE : {NUM_TO_RANK_DICT[rank]}\n"

    sut_module.print_player_info(player_number)

    actual_out = capsys.readouterr().out
    assert actual_out == expected_out

@pytest.mark.parametrize(
    "player_names, bad_players",
    [(["A", "B", "C"], [False, False, False]),
     (["A", "B", "C"], [True, False, False]),
     (["A", "B", "C"], [False, True, False]),
     (["A", "B", "C"], [True, True, False]),
     (["A", "B", "C"], [False, False, True]),
     (["A", "B", "C"], [True, True, True]),]
)
def test_print_removed_players(player_names, bad_players, capsys: CaptureFixture, mocker: MockerFixture):
    mock_is_bad_player = mocker.patch("attendance.is_bad_player", side_effect=bad_players)
    sut_module.player_count = len(player_names)
    for player_number, player_name in enumerate(player_names, 1):
        sut_module.names[player_number] = player_name
    expected_out = ("\nRemoved player\n"
                    "==============\n")
    for player_name, is_bad in zip(player_names, bad_players):
        if is_bad:
            expected_out += f"{player_name}\n"

    sut_module.print_removed_players()
    actual_out = capsys.readouterr().out

    assert actual_out == expected_out
    assert mock_is_bad_player.call_count == 3