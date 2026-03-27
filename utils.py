OBJECT_EMPTY = None
OBJECT_HOUSE = "🏠"
OBJECT_HOSPITAL = "🏥"


MOVE_UP = (0, -1)
MOVE_DOWN = (0, 1)
MOVE_LEFT = (-1, 0)
MOVE_RIGHT = (1, 0)


def is_free_to_move(map, move):
    x, y = move
    return map[y][x]==None

    """
    Check whether a target position is empty and can be moved into.

    Args:
        map: Matrix (list of lists) representing the board.
        move: Position as (x, y), where x is horizontal and y is vertical.

    Returns:
        bool: True if the target cell is empty (None), False otherwise.
    """

    raise NotImplementedError("is_free_to_move is not implemented yet")


def is_valid_move(map, move):
    max_rows = len(map)
    max_columns = len(map[0])
    x, y=move

    if(x<0 or y<0):
        return False
    elif(x>max_columns-1):
        return False
    elif(y>max_rows-1):
        return False
    else:
        return True
    
    """
    Check whether a position is inside the matrix boundaries.
    Args:
        map: Matrix (list of lists) representing the board.
        move: Position as (x, y), where x is horizontal and y is vertical.

    Returns:
        bool: True if the position is within bounds, False otherwise.
    """

    raise NotImplementedError("is_valid_move is not implemented yet")


def find_objects(map, target_object_symbol):
    """
    Find all coordinates where a given object symbol appears.

    Args:
        map: Matrix (list of lists) representing the board.
        target_object_symbol: Symbol to search for (None, 🏠, or 🏥).

    Returns:
        list[tuple[int, int]]: All matching coordinates as (x, y).
    """

    raise NotImplementedError("find_objects is not implemented yet")


def result(map, hospital_coordinates, target_move):
    """
    Create and return a new map after moving one hospital to a target position.

    Args:
        map: Matrix (list of lists) representing the board.
        hospital_coordinates: Current hospital position as (x, y).
        target_move: Destination position as (x, y).

    Returns:
        list[list]: A deep-copied map with the move applied.
    """

    raise NotImplementedError("result is not implemented yet")


def manhattan(pos, pos_2):
    """
    Compute the Manhattan distance between two coordinates.

    Args:
        pos: First coordinate as (x, y).
        pos_2: Second coordinate as (x, y).

    Returns:
        int: Distance computed as abs(x2 - x1) + abs(y2 - y1).
    """

    raise NotImplementedError("manhattan is not implemented yet")


def cost(map):
    """
    Compute total cost as the sum of distances from each hospital to each house.

    Args:
        map: Matrix (list of lists) representing the board.

    Returns:
        int: Total Manhattan-distance cost.
    """

    raise NotImplementedError("cost is not implemented yet")


def move(pos, pos_2):
    """
    Add two coordinates component-wise.

    Args:
        pos: First coordinate as (x, y).
        pos_2: Second coordinate as (x, y).

    Returns:
        tuple[int, int]: New coordinate as (x1 + x2, y1 + y2).
    """

    raise NotImplementedError("move is not implemented yet")


def actions(map, hospital_position):
    """
    Return all valid adjacent moves for a hospital in up, down, left, right order.

    Args:
        map: Matrix (list of lists) representing the board.
        hospital_position: Hospital coordinate as (x, y).

    Returns:
        list[tuple[int, int]]: Valid neighboring positions that are in bounds and free.
    """

    raise NotImplementedError("actions is not implemented yet")
