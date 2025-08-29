from pathlib import Path

MAX_PLAYER_COUNT = 100

NORMAL = 0
GOLD = 1
SILVER = 2

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

ATTENDANCE_FILE_NAME = "attendance_weekday_500.txt"

player_to_num_dict = {}
player_count = 0

# weekly_attend_counts[사용자ID][요일]
weekly_attend_counts = [[0] * 100 for _ in range(MAX_PLAYER_COUNT)]
points = [0] * MAX_PLAYER_COUNT
ranks = [0] * MAX_PLAYER_COUNT
names = [''] * MAX_PLAYER_COUNT


def day_to_number(day_of_week: str) -> int:
    day_to_num_dict = {
        "monday": MONDAY,
        "tuesday": TUESDAY,
        "wednesday": WEDNESDAY,
        "thursday": THURSDAY,
        "friday": FRIDAY,
        "saturday": SATURDAY,
        "sunday": SUNDAY,
    }
    return day_to_num_dict[day_of_week]


def get_player_number(player_name: str) -> int:
    global player_count

    if player_name not in player_to_num_dict:
        player_count += 1
        player_to_num_dict[player_name] = player_count
        names[player_count] = player_name
    return player_to_num_dict[player_name]


def add_basic_points(player_number: int, day_of_week: str):
    add_point = 1
    day_number = day_to_number(day_of_week)
    if day_number == WEDNESDAY:
        add_point = 3
    if day_number in (SATURDAY, SUNDAY):
        add_point = 2

    weekly_attend_counts[player_number][day_number] += 1
    points[player_number] += add_point


def print_removed_players():
    print("\nRemoved player")
    print("==============")
    for player_number in range(1, player_count + 1):
        if is_bad_player(player_number):
            print(names[player_number])


def is_bad_player(player_number: int):
    player_weekly_attend_count = weekly_attend_counts[player_number]
    return (ranks[player_number] not in (GOLD, SILVER)
            and player_weekly_attend_count[WEDNESDAY] == 0
            and player_weekly_attend_count[SATURDAY] == 0
            and player_weekly_attend_count[SUNDAY] == 0)


def print_player_info(player_number: int):
    print(f"NAME : {names[player_number]}, POINT : {points[player_number]}, GRADE : ", end="")
    if ranks[player_number] == GOLD:
        print("GOLD")
    elif ranks[player_number] == SILVER:
        print("SILVER")
    else:
        print("NORMAL")


def set_attendance_rank(player_number: int):
    if points[player_number] >= 50:
        ranks[player_number] = GOLD
    elif points[player_number] >= 30:
        ranks[player_number] = SILVER
    else:
        ranks[player_number] = NORMAL


def add_bonus_points(player_number: int):
    if weekly_attend_counts[player_number][WEDNESDAY] >= 10:
        points[player_number] += 10
    if weekly_attend_counts[player_number][SATURDAY] + weekly_attend_counts[player_number][SUNDAY] >= 10:
        points[player_number] += 10


def read_attendance_file(file_name: str) -> list[list[str]]:
    current_dir = Path(__file__).parent
    attendance_list = []
    try:
        with open(current_dir / file_name, encoding='utf-8') as f:
            for line in f.readlines():
                if not line:
                    break
                parts = line.strip().split()
                if len(parts) == 2:
                    attendance_list.append(parts)
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    return attendance_list


def run_attendance_system():
    attendance_data = read_attendance_file(ATTENDANCE_FILE_NAME)
    for player_name, day_of_week in attendance_data:
        player_number = get_player_number(player_name)
        add_basic_points(player_number, day_of_week)

    for player_number in range(1, player_count + 1):
        add_bonus_points(player_number)

        set_attendance_rank(player_number)

        print_player_info(player_number)

    print_removed_players()


if __name__ == "__main__":
    run_attendance_system()
