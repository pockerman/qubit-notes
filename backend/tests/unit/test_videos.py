import pytest

from qubit_notes.domain.videos import duration_seconds
from tests.videos import make_mp4, make_webm


@pytest.mark.parametrize("make", [make_mp4, make_webm])
def test_the_duration_of_a_video(make):
    assert duration_seconds(make(2700)) == pytest.approx(2700)


def test_a_file_that_is_not_a_video_has_no_duration():
    assert duration_seconds(b"Notes on aeronautics.") is None


def test_a_truncated_video_has_no_duration():
    assert duration_seconds(make_mp4(60)[:30]) is None
