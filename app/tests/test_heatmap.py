import pytest
from datetime import datetime, timedelta
import app.utils.build_heatmap as heatmap_module
from app.utils import HeatMap

Log = lambda date, emotion: {'date': date, 'emotion': emotion, 'colour': None}


@pytest.fixture(autouse=True)
def freeze_now(monkeypatch):
    # freeze at 15 Apr 2025 12:00
    fixed = datetime(2025, 4, 15, 12, 0, 0)

    class DummyDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed.replace(tzinfo=tz)

    monkeypatch.setattr(heatmap_module, 'datetime', DummyDateTime, raising=False)
    return fixed


def test_group_emotions_filter_and_adds_colours():
    data_log = [
        {'date': datetime(2025, 4, 10), 'emotion': 'Happy'},
        {'date': datetime(2025, 4, 11), 'emotion': 'Unknown'},
    ]
    hm = HeatMap(10, 4, 2025, data_log)
    grouped = hm.group_emotions()

    assert len(grouped) == 1
    assert grouped[0]['emotion'] == 'Happy'
    assert grouped[0]['colour'] == 'bright_yellow'
    assert grouped[0]['date'] == datetime(2025, 4, 10)


def test_create_logs_mapping_excludes_future_dates(freeze_now):
    today = freeze_now
    future = today + timedelta(days=1)
    logs = [
        {'date': today, 'emotion': 'Sad', 'colour': 'dark_blue'},
        {'date': future, 'emotion': 'Sad', 'colour': 'dark_blue'},
    ]
    mapping = HeatMap._create_logs_mapping(logs)

    key = (today.day, today.month, today.year)
    assert key in mapping
    assert (future.day, future.month, future.year) not in mapping
    assert mapping[key]['emotion'] == 'Sad'
    assert mapping[key]['colour'] == 'dark_blue'


def test_month_display_marks_logged_days(freeze_now):
    log_date = datetime(2025, 4, 5)
    logs = [{'date': log_date, 'emotion': 'Anger', 'colour': 'dark_red'}]
    hm = HeatMap(5, 4, 2025, logs)

    header, matrix = hm.month_display()
    # header should be [4, 2025]
    assert header == [4, 2025]

    found = False
    for week in matrix:
        for cell in week:
            if isinstance(cell, list):
                day, info = cell
                if day == 5:
                    found = True
                    assert info == {'emotion': 'Anger', 'colour': 'dark_red'}
    assert found, 'Day 5 should be annotated in the April heatmap'


def test_year_display_marks_each_month_correctly(freeze_now):
    log_date = datetime(2025, 1, 20)
    logs = [{'date': log_date, 'emotion': 'Love', 'colour': 'hot_pink'}]
    hm = HeatMap(1, 1, 2025, logs)

    year_info = hm.year_display()
    # each entry is [[month, year], matrix]
    jan_entry = next(entry for entry in year_info if entry[0] == [1, 2025])
    _, jan_matrix = jan_entry

    found = False
    for week in jan_matrix:
        for cell in week:
            if isinstance(cell, list):
                day, info = cell
                if day == 20:
                    found = True
                    assert info == {'emotion': 'Love', 'colour': 'hot_pink'}
    assert found, 'Day 20 in June should be annotated in the yearly heatmap'
