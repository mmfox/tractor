def get_rank_up(defending_points):
    attacking_rank_up = 0
    defending_rank_up = 0

    if defending_points == 0:
        attacking_rank_up = 3
    elif defending_points <= 35:
        attacking_rank_up = 2
    elif defending_points <= 75:
        attacking_rank_up = 1
    elif defending_points <= 115:
        pass
    elif defending_points <= 155:
        defending_rank_up = 1
    elif defending_points <= 195:
        defending_rank_up = 2
    else:
        defending_rank_up = 3

    return attacking_rank_up, defending_rank_up
