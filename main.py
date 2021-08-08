import random
import itertools


def create_world(world_side, num_cans):
    world = [
        [False for i in range(world_side)]
        for j in range(world_side)
    ]

    can_indices = []
    while len(can_indices) < num_cans:
        row = random.randint(0, world_side - 1)
        col = random.randint(0, world_side - 1)
        if (row, col) not in can_indices:
            can_indices.append((row, col))

    for (row, col) in can_indices:
        world[row][col] = True
    return world


WALL = 0
EMPTY = 1
CAN = 2

ACTION_UP = 0
ACTION_DOWN = 1
ACTION_LEFT = 2
ACTION_RIGHT = 3
ACTION_RANDOM_MOVE = 4
ACTION_PICK_UP = 5
ACTION_NOTHING = 6

LEFT = 0
TOP = 1
RIGHT = 2
BOTTOM = 3
MIDDLE = 4


ALL_STATES = itertools.product(range(3), range(3), range(3), range(3), range(3))


def can_in_middle(state):
    return state[MIDDLE] == CAN


def any_cans(state):
    return bool(sum(s == CAN for s in state))


def default_strat(state):
    if can_in_middle(state):
        return ACTION_PICK_UP
    elif not any_cans(state):
        return ACTION_RANDOM_MOVE
    elif state[LEFT] == CAN:
        return ACTION_LEFT
    elif state[TOP] == CAN:
        return ACTION_UP
    elif state[RIGHT] == CAN:
        return ACTION_RIGHT
    elif state[BOTTOM] == CAN:
        return ACTION_DOWN
    else:
        raise Exception()


class Strategy:
    def __init__(self, actions):
        self.actions = actions

    def act(self, state):
        return self.actions[state]

    @staticmethod
    def default_strat():
        default_actions = {state: default_strat(state) for state in ALL_STATES}
        return Strategy(default_actions)


def test_create_world():
    world_side = 10
    num_cans = 10
    world = create_world(world_side, num_cans)
    assert len(world) == world_side
    assert len(world[0]) == world_side
    assert sum(sum(square for square in row) for row in world) == num_cans


def test_create_default_strat():
    strat = Strategy.default_strat()
    assert len(strat.actions) == 3**5
    assert sum(a == ACTION_PICK_UP for a in strat.actions.values()) == 3**4
    assert sum(a == ACTION_RANDOM_MOVE for a in strat.actions.values()) == 2**5


if __name__ == "__main__":
    test_create_world()    
    test_create_default_strat()    
