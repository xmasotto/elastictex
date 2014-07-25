import re

from bs4 import BeautifulSoup
from urlparse import urlparse
from elasticsearch import Elasticsearch


var_types = {
    "integer_constants": {
        'name': 'K',
        'value': [
            'i', 'j', 'k', 'n', 'm'
        ]
    },
    "continuous_constants": {
        'name': 'C',
        'value': [
            'a', 'b', 'c', 'p', 'q', 's', 't'
        ]
    },
    "variables": {
        "name": "X",
        'value': [
            'x', 'y', 'z', 'u', 'v', 'w'
        ]
    }
}
var_mapping = {}
for x in var_types.values():
    for val in x['value']:
        var_mapping[val] = x['name']


es = Elasticsearch(hosts=["localhost:9200"])


def init():
    es.indices.create(index="math", ignore=400)
    mapping = {
        "equation": {
            "properties": {
                "processed": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
    es.indices.put_mapping(index="math",
                           doc_type="equation",
                           body=mapping)


def search(s=None):
    term = canonicalize(s)
    print(term)
    query = {
        "query": {
            "in": {
                "processed": [term]
            }
        }
    }
    result = es.search(index="math", doc_type="equation", body=query,
                       size=20)

    docs = []
    for hit in result['hits']['hits']:
        doc = hit['_source']
        docs.append(doc)
    return docs


def store(title, url, equations):
    for eq in equations:
        processed = [canonicalize(x) for x in expand(eq)]
        doc = {
            "title": title,
            "url": url,
            "equation": eq,
            "processed": processed
        }
        es.index(index="math", doc_type="equation", body=doc)


def index(url, html):
    info = urlparse(url)
    domain = info.scheme + '://' + info.netloc
    bs = BeautifulSoup(html)
    title = get_title(bs)

    question = bs.find("div", {"class": "question"})
    store(title, url, get_equations(question))

    answers = bs.find_all("div", {"class": "answer"})
    for i, answer in enumerate(answers):
        answer_url = "%s/a/%s" % (
            domain, answer['id'].split('-')[1])
        store(title + "(answer %d)" % (i+1),
              answer_url, get_equations(answer))


def get_title(element):
    title = element.find("title").text
    parts = title.split('-', 1)
    if parts[0] == parts[0].lower():
        title = parts[1]
    return title.rsplit('-', 1)[0]


def get_equations(element):
    equations = []
    if element:
        pars = element.find_all("p")
        for par in pars:
            equations.extend(
                text for i, text in enumerate(par.text.split("$"))
                if i % 2 == 1 and len(text) > 12)
    return equations


def get_var_name(c):
    for x in var_types.values():
        if c in x['value']:
            return x['name']
    return c.upper()


def is_constant(name):
    for constant in constants:
        if name.startswith(constant):
            return True
    return False


def replace_vars(s):
    # Replace Variables
    var_re = re.compile(r"[a-z](_[0-9])?")
    counts = {}
    start = 0
    while True:
        m = var_re.search(s, start)
        if m is None:
            break

        name = m.group()
        var_name = var_mapping.get(name[:1], name.upper())
        count = counts.get(var_name, 0)
        s = re.sub(r"%s" % name,
                   "[%s%d]" % (var_name, count),
                   s)
        counts[var_name] = count + 1

    return s


def expand(s):
    parts = [s]
    stack = []
    expand_braces(parts, stack, s, 0)

    def split(c):
        n = len(parts)
        for i in range(n):
            if c in parts[i]:
                parts.extend(parts[i].split(c))

    split('=')
    split('+')
    split('-')

    return parts


def expand_braces(result, stack, s, i):
    expr = re.compile(r"[\{\}=]")
    m = expr.search(s, i)
    if not m:
        result.append(s)
        return len(s)

    c = m.group()
    j = m.start()

    if c == "}":
        if stack:
            result.append(s[stack.pop():j])
        return j+1

    if c == "{":
        result.append(s[i:j])
        stack.append(j+1)
        i = expand_braces(result, stack, s, j+1)
        if i < 0:
            i = len(s)
        return expand_braces(result, stack, s, i)


def canonicalize(s):
    # turn \sqrt -> [\SQRT]
    def sub_macro(match):
        return "[" + match.group(1).upper() + "]"
    s = re.sub(r"(\\\w+\d*)\b", sub_macro, s)

    # turn x_{1} -> x_1
    s = re.sub(r"_\{(\d)\}", r"_\1", s)

    # replace variables with canonical names
    s = replace_vars(s)

    # make sure single digit arguments are converted
    s = re.sub(r"\^(\d)", r"^{\1}", s)
    s = re.sub(r"\_(\d)", r"_{\1}", s)

    # remove spaces
    s = s.replace(" ", "")

    return s
