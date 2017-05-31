import sqlite3 as sql
from collections import Counter, defaultdict, namedtuple

from color import Color

QUERY = 'SELECT colorname, r, g, b FROM answers;'

Answer = namedtuple('Answer', ('name', 'r', 'g', 'b'))

conn = sql.connect('color-survey.sqlite')
conn.row_factory = (lambda cursor, row: Answer(*row))
cursor = conn.cursor()

colors = defaultdict(Counter)
for answer in cursor.execute(QUERY):
    colors[answer.name.replace('-', ' ')].update([Color(answer.r, answer.g, answer.b)])
centroids = {}
for name, rgbs in colors.items():
    count = sum(rgbs.values())
    r = round(sum(value.r * count for value, count in rgbs.items()) / count)
    g = round(sum(value.g * count for value, count in rgbs.items()) / count)
    b = round(sum(value.b * count for value, count in rgbs.items()) / count)
    centroids[name] = Color(r, g, b)
with open('color-centroids.tsv', 'w') as fd:
    for name, rgbs in sorted(colors.items(), key=(lambda kv: len(kv[1])), reverse=True):
        count = sum(rgbs.values())
        if count >= 1000:
            centroid = centroids[name]
            fd.write('{}\t{}\t{}\n'.format(count, name, centroid))
