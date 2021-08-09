import random
import copy
import itertools
import multiprocessing
import json


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

ALL_STATES = list(itertools.product(range(3), range(3), range(3), range(3), range(3)))


class World:
    def __init__(self, world_side=10, num_cans=10):
        self.world_side = world_side
        self.num_cans = num_cans

        row = random.randint(0, world_side - 1)
        col = random.randint(0, world_side - 1)
        self.robby = [row, col]

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

    def get_current_view(self):
        row, col = self.robby
        if col == 0:
            left = WALL
        else:
            left = CAN if self.state[row][col - 1] else EMPTY

        if col == (self.world_side - 1):
            right = WALL
        else:
            right = CAN if self.state[row][col + 1] else EMPTY

        if row == 0:
            top = WALL
        else:
            top = CAN if self.state[row - 1][col] else EMPTY

        if row == (self.world_side - 1):
            bottom = WALL
        else:
            bottom = CAN if self.state[row + 1][col] else EMPTY

        middle = CAN if self.state[row][col] else EMPTY
        return (left, top, right, bottom, middle)

    def num_cans_picked_up(self):
        cans_left = sum(sum(is_can for is_can in row) for row in self.state)
        return self.num_cans - cans_left

    def __str__(self):
        value = ''
        for i, row in enumerate(self.state):
            for j, is_can in enumerate(row):
                is_robby = self.robby == [i, j]
                if is_can and is_robby:
                    value += 'R'
                elif is_can and not is_robby:
                    value += 'c'
                elif not is_can and is_robby:
                    value += 'r'
                else:
                    value += '_'
            value += '\n'
        return value


class Strategy:
    def __init__(self, actions):
        self.actions = actions

    def __eq__(self, other):
        return self.actions == other.actions

    def act(self, state):
        return self.actions[state]

    @staticmethod
    def from_func(strat_func):
        actions = {state: strat_func(state) for state in ALL_STATES}
        return Strategy(actions)

    def mutate(self, num_mutations=1):
        mutated = Strategy(copy.deepcopy(self.actions))
        for _ in range(num_mutations):
            action_index = random.randint(0, len(ALL_STATES) - 1)
            action_key = ALL_STATES[action_index]
            mutated.actions[action_key] = random.choice([
                ACTION_PICK_UP,
                ACTION_RANDOM_MOVE,
                ACTION_LEFT,
                ACTION_UP,
                ACTION_RIGHT,
                ACTION_DOWN,
            ])
        return mutated

    def __repr__(self):
        actions_jsonifiable = {str(k): v for k, v in self.actions.items()}
        return json.dumps(actions_jsonifiable, indent=4)


def run_strategy(world, strat, num_steps):
    for step in range(num_steps):
        view = world.get_current_view()
        action = strat.act(view)
        world.respond_to_action(action)
    return world.num_cans_picked_up()


def evolve_strategies(starting_strat, num_iterations):
    num_strats = 10
    strats = [starting_strat.mutate(i) for i in range(num_strats)]

    pool = multiprocessing.Pool(8)

    for i in range(num_iterations):
        scores = pool.map(evaluate_strat, strats)
        strats_and_scores = list(zip(strats, scores))
        get_score = lambda pair: pair[1]
        strats_and_scores.sort(key=get_score, reverse=True)
        best_strat, best_score = strats_and_scores[0]

        strats = [best_strat.mutate(i) for i in range(num_strats)]
        print(i, best_score)
    return strats[0]


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


def pick_up_groups_strat(state):
    if state[MIDDLE] == CAN and state[LEFT] == CAN and state[RIGHT] == CAN:
        return ACTION_LEFT
    elif state[MIDDLE] == CAN and state[TOP] == CAN and state[BOTTOM] == CAN:
        return ACTION_UP
    else:
        return default_strat(state)


def evaluate_strat(strat, num_cans=10):
    num_runs = 1000
    num_time_steps = 150

    cans_picked_up = []
    for i in range(num_runs):
        world_side = 10
        world = World(world_side, num_cans)
        cans_picked_up_now = run_strategy(world, strat, num_time_steps)
        cans_picked_up.append(cans_picked_up_now)
    return sum(cans_picked_up) / (num_cans*num_runs)


def evaluate_default_strat():
    strat = Strategy.from_func(default_strat)
    percent_picked_up = evaluate_strat(strat, num_cans=10)
    print(percent_picked_up)  # matches 69% from the book!


def compare_default_and_group_strats():
    for num_cans in [10, 20, 30, 40, 50]:
        print("num cans", num_cans)

        strat = Strategy.from_func(default_strat)
        percent_picked_up = evaluate_strat(strat, num_cans)
        print("default strat", percent_picked_up)

        strat = Strategy.from_func(pick_up_groups_strat)
        percent_picked_up = evaluate_strat(strat, num_cans)
        print("pick up groups strat", percent_picked_up)


if __name__ == "__main__":
    starting_strat = Strategy.from_func(default_strat)
    num_iterations = 2500
    winning_strat = evolve_strategies(starting_strat, num_iterations)
    print(winning_strat)
