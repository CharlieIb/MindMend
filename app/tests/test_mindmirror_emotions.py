from collections import namedtuple
from app.helpers import get_emotions_info_from_logs

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
    assert info['max_num'] == ['Happy', 100]
    assert info['emotions_percentage']['Happy'] == 50


def test_multiple_logs():
    # 2 Sad, 1 Anger
    logs = [Log('Sad'), Log('Sad'), Log('Anger')]
    info = get_emotions_info_from_logs(logs)
    # one three total == 3
    assert info['total_emotion_logs'] == 3

    # Sad -> rounded(2/3) == 67, then divide by two to fit bar == ~33
    sad_percent = round((2 / 3) * 100 / 2)
    assert info['emotions_percentage']['Sad'] == sad_percent
    assert info['max_num'] == ['Sad', sad_percent * 2]


def test_tie_breaker_order():
    # 1 Happy, 1 Calm -> both 50% -> tie
    logs = [Log('Happy'), Log('Calm')]
    info = get_emotions_info_from_logs(logs)

    # Which ever appears first in dict order wins (Anger, Anxious, Sad, Happy, Love, Calm)
    assert info['max_num'][0] == 'Happy'
    assert info['max_num'][1] == info['emotions_percentage']['Happy'] * 2


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
