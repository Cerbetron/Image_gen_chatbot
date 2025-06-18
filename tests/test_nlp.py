from datetime import date
import os, sys
sys.path.insert(0, os.path.abspath('.'))
import advisor_chat.data_source as ds
from advisor_chat import nlp


ds.store_csv(open('tests/fixtures/sample.csv','rb').read())

nlp._today = lambda: date(2024,6,5)

phrases = [
    'last week',
    'this month',
    'yesterday',
    'today',
    'tomorrow',
    'past fortnight',
    'last 2 weeks',
    'from 2024-06-01 to 2024-06-05',
    'since 2024-06-02',
    'until 2024-06-03',
    'last 1 months'
]


def test_parse_request():
    for p in phrases:
        assert nlp.parse_request(p)
