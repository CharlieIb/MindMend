from collections import namedtuple
from app.utils.General import get_emotions_info_from_logs

# Stub for emotion logs
Log = namedtuple('Log', ['emotion'])


def test_no_logs():
    info = get_emotions_info_from_logs([])
    assert info['total_emotion_logs'] == 0
    assert info['max_num'] == [None, 0]
    # all percentage == 0
    assert all(e == 0 for e in info['emotions_percentage'].values())


def test_single_happy_log():
    logs = [Log('Happy')]
    info = get_emotions_info_from_logs(logs)
    # one log total == 1
    assert info['total_emotion_logs'] == 1

    # one log == 100%, bar units -> 100 / 2 == 50
    assert info['max_num'] == ['Happy', 1]
    assert info['emotions_percentage']['Happy'] == 50


def test_multiple_logs():
    # 2 Sad, 1 Anger
    logs = [Log('Sad'), Log('Sad'), Log('Anger')]
    info = get_emotions_info_from_logs(logs)

    # total logs == 3
    assert info['total_emotion_logs'] == 3

    # half-scaled bar units: round((2/3)*50) == 33
    expected_bar = round((2 / 3) * 50)
    assert info['emotions_percentage']['Sad'] == expected_bar

    # max_num returns raw count == 2
    assert info['max_num'] == ['Sad', 2]


def test_tie_breaker_order():
    # 1 Happy, 1 Calm → both tied
    logs = [Log('Happy'), Log('Calm')]
    info = get_emotions_info_from_logs(logs)

    # Tie goes to the first emotion in your default order
    assert info['max_num'][0] == 'Happy'

    # And max_num[1] is the raw count (1), not 50
    assert info['max_num'][1] == 1

    # If you also want to check the bar-unit percentage:
    expected_bar = round((1 / info['total_emotion_logs']) * 50)
    assert info['emotions_percentage']['Happy'] == expected_bar


def test_segments():
    logs = [Log('Happy'), Log('Calm')]
    info = get_emotions_info_from_logs(logs)
    segments = info['segments']

    # Last cumulative must be 50
    assert segments[-1]['cumulative'] == 50

    # Earlier ones still match running sums (capped)
    running = 0
    for seg in segments[:-1]:
        running += seg['value']
        running = min(50, running)
        assert seg['cumulative'] == running
