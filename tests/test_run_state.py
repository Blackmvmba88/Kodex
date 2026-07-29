from agent.run_state import RunState, RunStore


def test_run_state_round_trip(tmp_path):
    store = RunStore(tmp_path)
    state = RunState.create("demo task", tmp_path)
    state.update(phase="planned", status="paused", branch="kodex/demo-task")

    path = store.save(state)
    loaded = store.load(state.run_id)

    assert path.exists()
    assert loaded.run_id == state.run_id
    assert loaded.task == "demo task"
    assert loaded.phase == "planned"
    assert loaded.status == "paused"
    assert loaded.branch == "kodex/demo-task"


def test_latest_returns_most_recent_state(tmp_path):
    store = RunStore(tmp_path)
    first = RunState.create("first", tmp_path)
    second = RunState.create("second", tmp_path)
    store.save(first)
    store.save(second)

    latest = store.latest()

    assert latest is not None
    assert latest.run_id == second.run_id
