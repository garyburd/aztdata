import typing
import re
from typing import Any

_escapes = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
}

_escape_re = re.compile(f'[{"".join(_escapes.keys())}]')


def escape(s: str) -> str:
    return _escape_re.sub(lambda m: _escapes[m.group(0)], s)


def _keyvalue(key: str, value: Any) -> str:
    if value is False or value is None:
        return ''
    if value is True:
        return f' {key}'
    value = str(value).replace('&', '&amp;')
    if not "'" in value:
        return f" {key}='{value}'"
    value = value.replace('"', '&quot;')
    return f' {key}="{value}"'


# To improve output readability, insert newline before these tags.
_nl_tags = {
    # Block Tags
    'address',
    'article',
    'aside',
    'blockquote',
    'canvas',
    'dd',
    'div',
    'dl',
    'dt',
    'fieldset',
    'figcaption',
    'figure',
    'footer',
    'form',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'header',
    'hr',
    'li',
    'main',
    'nav',
    'noscript',
    'ol',
    'p',
    'pre',
    'section',
    'table',
    'tfoot',
    'ul',
    'video',
    # Other
    'html',
    'head',
    'body',
    'link',
    'meta',
    'br',
    'option',
}

_void_tags = {
    'area',
    'base',
    'br',
    'col',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
}


class TagContext:
    __slots__ = ('_doc', '_text')
    _doc: 'Document'
    _text: str

    def __init__(self, doc, text):
        self._doc = doc
        self._text = text

    def __enter__(self) -> None:
        doc = self._doc
        assert doc._ctx == self
        doc._ctx = None

    def __exit__(self, type, value, traceback):
        _, _, _ = type, value, traceback
        doc = self._doc
        if doc._ctx:
            doc._ctx._close()
        doc._write(self._text)

    def __call__(self, v: Any) -> None:
        doc = self._doc
        assert doc._ctx == self
        doc._write(f'{escape(str(v))}{self._text}')
        doc._ctx = None

    def _close(self):
        doc = self._doc
        doc._write(self._text)
        doc._ctx = None


class Document:
    __slots__ = ('_write', '_ctx')

    # Write to output using this function.
    _write: typing.Callable[[str], Any]

    _ctx: TagContext | None

    def __init__(self, write: typing.Callable[[str], Any]):
        self._write = write
        self._ctx = None

    def printr(self, v: Any) -> None:
        """Print value to putput as is (raw)."""
        if self._ctx:
            self._ctx._close()
        self._write(str(v))

    def print(self, v: Any) -> None:
        """Print escaped value to putput."""
        if self._ctx:
            self._ctx._close()
        self._write(escape(str(v)))

    def _tag(
        self,
        name: str,
        tattrs: tuple[tuple[str, Any], ...],
        dattrs: dict[str, Any],
    ) -> TagContext:
        if self._ctx:
            self._ctx._close()
        parts = []
        if name in _nl_tags:
            parts.append('\n')
        parts.append(f'<{name}')
        for key, value in tattrs:
            parts.append(_keyvalue(key, value))
        for key, value in dattrs.items():
            if key.endswith('_'):
                key = key[:-1]
            key = key.replace('_', '-')
            parts.append(_keyvalue(key, value))
        parts.append('>')
        self._write(''.join(parts))
        ctx = TagContext(self, f'</{name}>' if name not in _void_tags else '')
        self._ctx = ctx
        return ctx

    def tag(
        self,
        name: str,
        /,
        *tattrs: tuple[str, Any],
        **dattrs: Any,
    ) -> TagContext:
        return self._tag(name, tattrs, dattrs)

    def A(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('a', t, d)

    def ABBR(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('abbr', t, d)

    def ACRONYM(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('acronym', t, d)

    def ADDRESS(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('address', t, d)

    def APPLET(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('applet', t, d)

    def AREA(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('area', t, d)

    def ARTICLE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('article', t, d)

    def ASIDE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('aside', t, d)

    def AUDIO(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('audio', t, d)

    def B(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('b', t, d)

    def BASE(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('base', t, d)

    def BASEFONT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('basefont', t, d)

    def BDI(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('bdi', t, d)

    def BDO(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('bdo', t, d)

    def BGSOUND(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('bgsound', t, d)

    def BIG(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('big', t, d)

    def BLINK(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('blink', t, d)

    def BLOCKQUOTE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('blockquote', t, d)

    def BODY(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('body', t, d)

    def BR(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('br', t, d)

    def BUTTON(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('button', t, d)

    def CANVAS(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('canvas', t, d)

    def CAPTION(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('caption', t, d)

    def CENTER(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('center', t, d)

    def CITE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('cite', t, d)

    def CODE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('code', t, d)

    def COL(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('col', t, d)

    def COLGROUP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('colgroup', t, d)

    def CONTENT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('content', t, d)

    def DATA(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('data', t, d)

    def DATALIST(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('datalist', t, d)

    def DD(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('dd', t, d)

    def DEL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('del', t, d)

    def DETAILS(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('details', t, d)

    def DFN(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('dfn', t, d)

    def DIALOG(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('dialog', t, d)

    def DIR(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('dir', t, d)

    def DIV(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('div', t, d)

    def DL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('dl', t, d)

    def DT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('dt', t, d)

    def EM(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('em', t, d)

    def EMBED(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('embed', t, d)

    def FIELDSET(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('fieldset', t, d)

    def FIGCAPTION(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('figcaption', t, d)

    def FIGURE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('figure', t, d)

    def FONT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('font', t, d)

    def FOOTER(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('footer', t, d)

    def FORM(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('form', t, d)

    def FRAME(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('frame', t, d)

    def FRAMESET(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('frameset', t, d)

    def H1(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('h1', t, d)

    def H2(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('h2', t, d)

    def H3(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('h3', t, d)

    def H4(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('h4', t, d)

    def H5(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('h5', t, d)

    def H6(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('h6', t, d)

    def HEAD(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('head', t, d)

    def HEADER(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('header', t, d)

    def HGROUP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('hgroup', t, d)

    def HR(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('hr', t, d)

    def HTML(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('html', t, d)

    def I(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('i', t, d)

    def IFRAME(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('iframe', t, d)

    def IMAGE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('image', t, d)

    def IMG(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('img', t, d)

    def INPUT(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('input', t, d)

    def INS(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('ins', t, d)

    def ISINDEX(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('isindex', t, d)

    def KBD(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('kbd', t, d)

    def KEYGEN(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('keygen', t, d)

    def LABEL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('label', t, d)

    def LEGEND(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('legend', t, d)

    def LI(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('li', t, d)

    def LINK(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('link', t, d)

    def LISTING(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('listing', t, d)

    def MAIN(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('main', t, d)

    def MAP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('map', t, d)

    def MARK(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('mark', t, d)

    def MARQUEE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('marquee', t, d)

    def MATH(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('math', t, d)

    def MENU(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('menu', t, d)

    def MENUITEM(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('menuitem', t, d)

    def META(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('meta', t, d)

    def METER(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('meter', t, d)

    def MULTICOL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('multicol', t, d)

    def NAV(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('nav', t, d)

    def NEXTID(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('nextid', t, d)

    def NOBR(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('nobr', t, d)

    def NOEMBED(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('noembed', t, d)

    def NOFRAMES(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('noframes', t, d)

    def NOSCRIPT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('noscript', t, d)

    def OBJECT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('object', t, d)

    def OL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('ol', t, d)

    def OPTGROUP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('optgroup', t, d)

    def OPTION(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('option', t, d)

    def OUTPUT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('output', t, d)

    def P(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('p', t, d)

    def PARAM(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('param', t, d)

    def PICTURE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('picture', t, d)

    def PLAINTEXT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('plaintext', t, d)

    def PORTAL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('portal', t, d)

    def PRE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('pre', t, d)

    def PROGRESS(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('progress', t, d)

    def Q(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('q', t, d)

    def RB(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('rb', t, d)

    def RP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('rp', t, d)

    def RT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('rt', t, d)

    def RTC(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('rtc', t, d)

    def RUBY(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('ruby', t, d)

    def S(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('s', t, d)

    def SAMP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('samp', t, d)

    def SCRIPT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('script', t, d)

    def SECTION(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('section', t, d)

    def SELECT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('select', t, d)

    def SHADOW(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('shadow', t, d)

    def SLOT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('slot', t, d)

    def SMALL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('small', t, d)

    def SOURCE(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('source', t, d)

    def SPACER(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('spacer', t, d)

    def SPAN(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('span', t, d)

    def STRIKE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('strike', t, d)

    def STRONG(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('strong', t, d)

    def STYLE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('style', t, d)

    def SUB(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('sub', t, d)

    def SUMMARY(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('summary', t, d)

    def SUP(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('sup', t, d)

    def SVG(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('svg', t, d)

    def TABLE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('table', t, d)

    def TBODY(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('tbody', t, d)

    def TD(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('td', t, d)

    def TEMPLATE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('template', t, d)

    def TEXTAREA(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('textarea', t, d)

    def TFOOT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('tfoot', t, d)

    def TH(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('th', t, d)

    def THEAD(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('thead', t, d)

    def TIME(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('time', t, d)

    def TITLE(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('title', t, d)

    def TR(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('tr', t, d)

    def TRACK(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('track', t, d)

    def TT(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('tt', t, d)

    def U(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('u', t, d)

    def UL(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('ul', t, d)

    def VAR(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('var', t, d)

    def VIDEO(self, /, *t: tuple[str, Any], **d: Any) -> TagContext:
        return self._tag('video', t, d)

    def WBR(self, /, *t: tuple[str, Any], **d: Any) -> None:
        self._tag('wbr', t, d)


class XTagContext:
    __slots__ = ('_doc', '_name')
    _doc: 'XDocument'
    _name: str

    def __init__(self, doc, name):
        self._doc = doc
        self._name = name

    def __enter__(self) -> None:
        doc = self._doc
        assert doc._ctx == self
        doc._write('>')
        doc._ctx = None

    def __exit__(self, type, value, traceback):
        _, _, _ = type, value, traceback
        doc = self._doc
        if doc._ctx:
            doc._ctx._close()
        doc._write(f'</{self._name}>')

    def __call__(self, v: Any) -> None:
        doc = self._doc
        assert doc._ctx == self
        doc._write(f'>{escape(str(v))}</{self._name}>')
        doc._ctx = None

    def _close(self):
        doc = self._doc
        doc._write('/>')
        doc._ctx = None


def _xkeyvalue(key: str, value: Any) -> str:
    if value is None:
        return ''
    value = str(value).replace('&', '&amp;')
    if not "'" in value:
        return f" {key}='{value}'"
    value = value.replace('"', '&quot;')
    return f' {key}="{value}"'


class XDocument:
    __slots__ = ('_write', '_ctx')

    _write: typing.Callable[[str], Any]
    _ctx: XTagContext | None

    def __init__(self, write: typing.Callable[[str], Any]):
        self._write = write
        self._ctx = None

    def printr(self, v: Any) -> None:
        if self._ctx:
            self._ctx._close()
        self._write(str(v))

    def print(self, v: Any) -> None:
        if self._ctx:
            self._ctx._close()
        self._write(escape(str(v)))

    def tag(
        self,
        name: str,
        /,
        *tattrs: tuple[str, Any],
        **dattrs: Any,
    ) -> XTagContext:
        if self._ctx:
            self._ctx._close()
        parts = []
        parts.append(f'<{name}')
        for key, value in tattrs:
            parts.append(_xkeyvalue(key, value))
        for key, value in dattrs.items():
            if key.endswith('_'):
                key = key[:-1]
            key = key.replace('__', ':')
            key = key.replace('_', '-')
            parts.append(_xkeyvalue(key, value))
        self._write(''.join(parts))
        ctx = XTagContext(self, name)
        self._ctx = ctx
        return ctx

