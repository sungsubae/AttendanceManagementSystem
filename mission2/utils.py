from constants import DAY_TO_NUM_DICT


def day_to_number(day_of_week: str) -> int:
    return DAY_TO_NUM_DICT[day_of_week]
