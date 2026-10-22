from datetime import date, datetime

from generate import (
    TIMEZONE, compute_calendar, compute_rhythm, compute_streaks, compute_top_languages, heat_level, is_vendored,
)


def commit(when: datetime, files: list[tuple[str, int]] = ()) -> dict:
    return {"repo": "me/repo", "when": when, "additions": 0, "deletions": 0, "files": list(files)}


def test_longest_streak_counts_weekends():
    # Fri, Sat, Sun, Mon in a row, then a gap.
    days = {date(2026, 10, 9), date(2026, 10, 10), date(2026, 10, 11), date(2026, 10, 12), date(2026, 10, 15)}
    assert compute_streaks(days, today=date(2026, 10, 20)) == (0, 4)


def test_current_streak_still_alive_when_last_active_yesterday():
    days = {date(2026, 10, 19), date(2026, 10, 20), date(2026, 10, 21)}
    assert compute_streaks(days, today=date(2026, 10, 22)) == (3, 3)


def test_current_streak_includes_today():
    days = {date(2026, 10, 21), date(2026, 10, 22)}
    assert compute_streaks(days, today=date(2026, 10, 22)) == (2, 2)


def test_no_activity_has_no_streak():
    assert compute_streaks(set(), today=date(2026, 10, 22)) == (0, 0)


def test_calendar_covers_365_days_in_sunday_first_weeks():
    weeks = compute_calendar([], today=date(2026, 10, 25))  # a Sunday
    days = [day for week in weeks for day in week]
    assert len(days) == 365
    assert days[-1]["date"] == date(2026, 10, 25)
    assert all(week[0]["weekday"] == 0 for week in weeks[1:])
    assert weeks[-1] == [{"date": date(2026, 10, 25), "weekday": 0, "count": 0}]


def test_calendar_counts_commits_per_local_day():
    commits = [
        commit(datetime(2026, 10, 22, 9, 0, tzinfo=TIMEZONE)),
        commit(datetime(2026, 10, 22, 23, 30, tzinfo=TIMEZONE)),
        commit(datetime(2025, 1, 1, tzinfo=TIMEZONE)),  # older than a year
    ]
    days = [day for week in compute_calendar(commits, today=date(2026, 10, 25)) for day in week]
    assert sum(day["count"] for day in days) == 2
    assert next(day for day in days if day["date"] == date(2026, 10, 22))["count"] == 2


def test_heat_levels_spread_ordinary_days_on_log_scale():
    assert [heat_level(count, peak=34) for count in [0, 1, 2, 3, 9, 10, 33, 34]] == [0, 1, 1, 2, 2, 3, 3, 4]


def test_rhythm_buckets_by_weekday_and_local_hour():
    commits = [
        commit(datetime(2026, 10, 19, 21, 5, tzinfo=TIMEZONE)),  # Monday 21h
        commit(datetime(2026, 10, 19, 21, 50, tzinfo=TIMEZONE)),
        commit(datetime(2026, 10, 25, 9, 0, tzinfo=TIMEZONE)),  # Sunday 9h
    ]
    grid = compute_rhythm(commits)
    assert grid[0][21] == 2
    assert grid[6][9] == 1
    assert sum(map(sum, grid)) == 3


def test_top_languages_weighted_by_added_lines():
    commits = [
        commit(datetime(2026, 10, 19, tzinfo=TIMEZONE), [("game.py", 300), ("README.md", 500)]),
        commit(datetime(2026, 10, 20, tzinfo=TIMEZONE), [("app.ts", 100)]),
    ]
    assert compute_top_languages(commits) == [("Python", 0.75), ("TypeScript", 0.25)]


def test_vendored_and_generated_paths_are_ignored():
    for path in ["venv/lib/python3.9/site.py", "server/node_modules/x/index.js", "build/app/out.dex",
                 "web/canvaskit/canvaskit.js", "web/assets/NOTICES", "client/package-lock.json", "pubspec.lock"]:
        assert is_vendored(path), path


def test_own_code_is_kept():
    for path in ["pokeidle/game.py", "lib/frontend/home.dart", "src/build_tools.ts", "web/index.html"]:
        assert not is_vendored(path), path
