from pathlib import Path

from constants import ATTENDANCE_FILE_NAME
from player import PlayerManager


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
    manager = PlayerManager()
    for player_name, day_of_week in attendance_data:
        try:
            manager.update_attendance(player_name, day_of_week)
        except Exception as e:
            print(e)

    manager.evaluate_players_info()
    manager.print_players_info()
    manager.print_removed_players()


if __name__ == "__main__":
    run_attendance_system()
