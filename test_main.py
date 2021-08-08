from main import *


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
    assert world.robby == [0, 0]
    world.respond_to_action(ACTION_UP)
    assert world.robby == [0, 0]
    world.respond_to_action(ACTION_DOWN)
    assert world.robby == [0, 0]
    world.respond_to_action(ACTION_LEFT)
    assert world.robby == [0, 0]
    world.respond_to_action(ACTION_RIGHT)
    assert world.robby == [0, 0]


def test_create_world_can():
    world_side = 1
    num_cans = 1
    world = World(world_side, num_cans)
    assert world.state[0][0]
    assert world.num_cans_picked_up() == 0
    assert world.get_current_view() == (WALL, WALL, WALL, WALL, CAN)
    world.respond_to_action(ACTION_PICK_UP)
    assert not world.state[0][0]
    assert world.num_cans_picked_up() == 1
    assert world.get_current_view() == (WALL, WALL, WALL, WALL, EMPTY)


def test_create_default_strat():
    strat = Strategy.from_func(default_strat)
    assert len(strat.actions) == 3**5
    assert sum(a == ACTION_PICK_UP for a in strat.actions.values()) == 3**4
    assert sum(a == ACTION_RANDOM_MOVE for a in strat.actions.values()) == 2**5


def test_full_world():
    world_side = 10
    num_cans = world_side*world_side
    world = World(world_side, num_cans)
    strat = Strategy.from_func(default_strat)

    assert world.num_cans_picked_up() == 0
    cans_picked_up = run_strategy(world, strat, 100000)
    assert cans_picked_up == world_side**2


def test_mutate_strat():
    strat = Strategy.from_func(lambda _: ACTION_NOTHING)
    num_actions = len(strat.actions)
    assert sum(a == ACTION_NOTHING for a in strat.actions.values()) == num_actions
    strat_mutated = strat.mutate()
    assert sum(a == ACTION_NOTHING for a in strat_mutated.actions.values()) == num_actions - 1


if __name__ == "__main__":
    test_create_world()
    test_create_default_strat()
    test_create_world_empty()
    test_create_world_can()
    test_full_world()
    test_mutate_strat()
