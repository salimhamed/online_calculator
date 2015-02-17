import re
from textwrap import dedent


# define page template
RESULT_PAGE = dedent("""
    <h1>{value1} {operator} {value2} = {result}</h1>
    <a href="/">Go home</a>
""")


def home():
    body = ['<h1>Online Calculator</h1>', 'Avalible Operators Are:', '<ul>']
    item_template = '<li>{}</li>'
    operators = ['add', 'substract', 'multiply', 'divide']
    for operator in operators:
        body.append(item_template.format(operator))
    body.append('</ul>')
    return '\n'.join(body)


def multiply(kwargs):
    """Return multiply page."""
    kwargs['operator'] = r'*'
    kwargs['result'] = kwargs['value1'] * kwargs['value2']
    return RESULT_PAGE.format(**kwargs)


def divide(kwargs):
    """Return divide page."""
    kwargs['operator'] = r'/'
    try:
        kwargs['result'] = kwargs['value1'] / kwargs['value2']
    except ZeroDivisionError:
        raise NameError
    return RESULT_PAGE.format(**kwargs)


def add(kwargs):
    """Return add page."""
    kwargs['operator'] = r'+'
    kwargs['result'] = kwargs['value1'] + kwargs['value2']
    return RESULT_PAGE.format(**kwargs)


def subtract(kwargs):
    """Return subtract page."""
    kwargs['operator'] = r'-'
    kwargs['result'] = kwargs['value1'] - kwargs['value2']
    return RESULT_PAGE.format(**kwargs)


def resolve_path(path):
    urls = [(r'^$', home),
            (r'^multiply/([\d]+)/([\d]+)$', multiply),
            (r'^divide/([\d]+)/([\d]+)$', divide),
            (r'^add/([\d]+)/([\d]+)$', add),
            (r'^subtract/([\d]+)/([\d]+)$', subtract)]
    matchpath = path.lstrip('/')
    for regexp, func in urls:
        match = re.match(regexp, matchpath)
        if match is None:
            continue
        args = match.groups()
        kwargs = {}
        if args:
            kwargs = {'value1': float(args[0]), 'value2': float(args[1])}
        return func, kwargs
    # we get here if no url matches
    raise NameError


def application(environ, start_response):
    headers = [("Content-type", "text/html")]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError
        func, kwargs = resolve_path(path)
        body = func(kwargs)
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1>Internal Server Error</h1>"
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
