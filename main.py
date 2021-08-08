import random
import itertools


class World:
    def __init__(self, world_side=10, num_cans=10):
        self.world_side = world_side
        self.num_cans = num_cans

        row = random.randint(0, world_side - 1)
        col = random.randint(0, world_side - 1)
        self.robby = (row, col)

        self.state = [
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
            self.state[row][col] = True

    def respond_to_action(self, action):
        if action == ACTION_UP:
            self.move_robby_up()
        elif action == ACTION_DOWN:
            self.move_robby_down()
        elif action == ACTION_LEFT:
            self.move_robby_left()
        elif action == ACTION_RIGHT:
            self.move_robby_right()
        elif action == ACTION_RANDOM_MOVE:
            self.move_robby_randomly()
        elif action == ACTION_PICK_UP:
            self.pick_up_can()
        elif action == ACTION_NOTHING:
            pass
        else:
            raise Exception()

    def move_robby_up(self):
        if self.robby[0] > 0:
            self.robby[0] = self.robby[0] - 1

    def move_robby_down(self):
        if self.robby[0] < self.world_side - 1:
            self.robby[0] = self.robby[0] + 1

    def move_robby_left(self):
        if self.robby[1] > 0:
            self.robby[1] = self.robby[1] - 1

    def move_robby_right(self):
        if self.robby[1] < self.world_side - 1:
            self.robby[1] = self.robby[1] + 1

    def move_robby_randomly(self):
        action = random.choice([ACTION_UP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT])
        self.respond_to_action(action)

    def pick_up_can(self):
        row, col = self.robby
        if self.state[row][col]:
            self.state[row][col] = False


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
    world = World(world_side, num_cans)
    assert len(world.state) == world_side
    assert len(world.state[0]) == world_side
    assert sum(sum(square for square in row) for row in world.state) == num_cans


def test_create_world_empty():
    world_side = 1
    num_cans = 0
    world = World(world_side, num_cans)
    assert world.robby == (0, 0)
    world.respond_to_action(ACTION_UP)
    assert world.robby == (0, 0)
    world.respond_to_action(ACTION_DOWN)
    assert world.robby == (0, 0)
    world.respond_to_action(ACTION_LEFT)
    assert world.robby == (0, 0)
    world.respond_to_action(ACTION_RIGHT)
    assert world.robby == (0, 0)


def test_create_world_can():
    world_side = 1
    num_cans = 1
    world = World(world_side, num_cans)
    assert world.state[0][0]
    world.respond_to_action(ACTION_PICK_UP)
    assert not world.state[0][0]


def test_create_default_strat():
    strat = Strategy.default_strat()
    assert len(strat.actions) == 3**5
    assert sum(a == ACTION_PICK_UP for a in strat.actions.values()) == 3**4
    assert sum(a == ACTION_RANDOM_MOVE for a in strat.actions.values()) == 2**5


if __name__ == "__main__":
    test_create_world()    
    test_create_default_strat()    
    test_create_world_empty()
    test_create_world_can()
