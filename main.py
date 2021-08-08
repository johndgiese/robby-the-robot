import random


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


def test_create_world():
    world_side = 10
    num_cans = 10
    world = create_world(world_side, num_cans)
    assert len(world) == world_side
    assert len(world[0]) == world_side
    assert sum(sum(square for square in row) for row in world) == num_cans


if __name__ == "__main__":
    test_create_world()    
