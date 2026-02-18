from concurrent.futures import ThreadPoolExecutor


def parallel_all(tasks, max_workers=None):
    """
    Execute multiple functions in parallel, similar to Promise.all().
    Returns results in the same order as the input tasks.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task) for task in tasks]
        return [f.result() for f in futures]


def preview(item, length=60):
    """Truncate an item's value for readable log output."""
    if item is None:
        return "None"
    s = str(item["value"]) if isinstance(item, dict) and "value" in item else str(item)
    return s[:length] + "..." if len(s) > length else s


def inteli_sort(items, comp, n, log=print):
    """
    Tournament-bracket sort that selects the top n items using a comparison function.

    Phase 1 builds a single-elimination bracket with parallel comparisons.
    Phase 2 extracts the top n by removing each champion and backfilling the bracket.

    Args:
        items: List of {id, value} dicts to sort.
        comp: Comparison function (a, b) -> winner. a and b are {id, value} dicts.
        n: Number of top items to select.
        log: Logging callable that receives a single string message. Defaults to print.

    Returns:
        List of top n items as {id, value} dicts, ranked best to worst.
    """

    levels = [items]
    sorted_items = []
    current_level = 0

    # index_map[level][item_id] -> position in that level
    index_map = [{item["id"]: i for i, item in enumerate(items)}]

    log(f"InteliSort: {len(items)} items, selecting top {n}")

    # ── Phase 1: Build tournament bracket ─────────────────────────
    log("Phase 1: Building tournament bracket")

    while True:
        current_level_items = levels[current_level]

        if len(current_level_items) == 1:
            log(f"  Bracket complete ({len(levels)} levels). Champion: {preview(current_level_items[0])}")
            break

        winners = []
        levels.append(winners)

        match_count = 0
        bye_count = 0
        tasks = []

        for i in range(0, len(current_level_items), 2):
            left = current_level_items[i]
            right = current_level_items[i + 1] if i + 1 < len(current_level_items) else None

            if right is None:
                # Bye round: auto-advance without invoking the compare function
                tasks.append(lambda l=left: l)
                bye_count += 1
            else:
                tasks.append(lambda l=left, r=right: comp(l, r))
                match_count += 1

        results = parallel_all(tasks)
        winners.extend(results)

        # Build index map for the new level
        index_map.append({item["id"]: i for i, item in enumerate(winners)})

        log(f"  Level {current_level}: {len(current_level_items)} items -> {match_count} matches, {bye_count} byes -> {len(winners)} winners")

        current_level += 1

    # ── Phase 2: Extract top n via backfill ───────────────────────
    log(f"Phase 2: Extracting top {n} via backfill")

    while True:
        winner = levels[-1][0]
        sorted_items.append(winner)

        log(f"  #{len(sorted_items)} selected: {preview(winner)}")

        if len(sorted_items) == n:
            break

        # Track removed positions per level for backfill
        level_to_removed_pos = {}

        # Remove winner from all levels
        for level_num in range(len(levels)):
            if winner["id"] in index_map[level_num]:
                winner_pos = index_map[level_num][winner["id"]]
                level_to_removed_pos[level_num] = winner_pos
                levels[level_num][winner_pos] = None
                del index_map[level_num][winner["id"]]

        # Backfill the bracket from bottom to top
        for level_num in range(len(levels) - 1):
            if level_num not in level_to_removed_pos:
                continue

            removed_pos = level_to_removed_pos[level_num]
            current_level_items = levels[level_num]

            if removed_pos % 2 == 0:
                left_index = removed_pos
                right_index = removed_pos + 1
            else:
                left_index = removed_pos - 1
                right_index = removed_pos

            left = current_level_items[left_index]
            right = current_level_items[right_index] if right_index < len(current_level_items) else None

            # Handle byes without invoking the compare function
            if left is None and right is None:
                new_winner = None
            elif left is None:
                new_winner = right
            elif right is None:
                new_winner = left
            else:
                new_winner = comp(left, right)

            next_level_pos = level_to_removed_pos[level_num + 1]
            levels[level_num + 1][next_level_pos] = new_winner

            if new_winner is not None:
                index_map[level_num + 1][new_winner["id"]] = next_level_pos

    log(f"InteliSort complete: top {n} selected")

    return sorted_items
