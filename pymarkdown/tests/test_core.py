from pymarkdown.core import process, separate_code_braces, parser, step
import doctest

text = """
Title
=====

Some prose

```
>>> x = 1
>>> x + 1
```
""".rstrip()

desired = """
Title
=====

Some prose

```
>>> x = 1
>>> x + 1
2
```
""".rstrip()


parts = parser.parse(separate_code_braces(text))


def test_process():
    assert process(text) == desired


def test_separate_code_braces():
    assert separate_code_braces(text).split('\n')[-2:] == ['', '```']


class Shout(object):
    def __init__(self, data):
        self.data = data

    def __repr_html__(self):
        return "<h1>%s</h1>" % self.data

def test_step():
    out, scope, state = step("prose", {'x': 1}, {})
    assert (out, scope, state) == (["prose"], {'x': 1}, {})

    out, scope, state = step("```Python", {'x': 1}, {})
    assert (out, scope, state) == (["```Python"], {'x': 1}, {'code': '```Python'})

    # Remove code state
    out, scope, state = step("```", {'x': 1}, {'code': '```Python'})
    assert (out, scope, state) == (["```"], {'x': 1}, {})

    a = doctest.Example("x + 1", "3")
    b = doctest.Example("x + 1", "2")
    out, scope, state = step(a, {'x': 1}, {'code': '```Python'})
    assert (out, scope, state) == ([b], {'x': 1}, {'code': '```Python'})

    a = doctest.Example("y = x + 1", "")
    out, scope, state = step(a, {'x': 1}, {'code': '```Python'})
    assert (out, scope, state) == ([a], {'x': 1, 'y': 2}, {'code': '```Python'})

    a = doctest.Example("Shout('Hello!')", '')
    out, scope, state = step(a, {'Shout': Shout}, {'code': '```Python'})
    assert out == ['```', Shout('Hello!').__repr_html__(), '```Python']
    assert state == {'code': '```Python'}


    a = doctest.Example("print(5)", '')
    b = doctest.Example("print(5)", '5')
    out, scope, state = step(a, {}, {'code': '```Python'})
    assert (out, scope, state) == ([b], {}, {'code': '```Python'})
