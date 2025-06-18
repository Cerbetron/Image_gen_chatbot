from datetime import date
import os, sys
sys.path.insert(0, os.path.abspath('.'))
import advisor_chat.data_source as ds


ds.store_csv(open('tests/fixtures/sample.csv','rb').read())


def test_get_scores():
    scores = ds.get_scores(date(2024,6,1), date(2024,6,5))
    assert len(scores) == 5
    assert list(scores.values())[0] == 80
