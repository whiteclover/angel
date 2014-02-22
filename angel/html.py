#! coding: utf-8

import re

from cgi import htmlunesacpe



def html_unescape(html):

    return htmlunescape(html)


    


def xml_escape(xml):
    def escape_gsub(re_str, text):
        ore, rre = re_str.split('/')
        return re.sub(ore, rre, text, flags=re.M)

    xml = escape_gsub(r'&/&amp', xml)
    xml = escape_gsub(r'</&lt', xml)
    xml = escape_gsub(r'>/&gt', xml)
    xml = escape_gsub(r'</&lt', xml)
    xml = escape_gsub(r"'/#39", xml)
    xml = escape_gsub(r'"/&quot', xml)
    return xml


def re_match(text_re, text):
    return re.match(text_re, text)


class HTML(object):

    ATTR_RE = r"""
        ([^<>=\s]+)          # Key
        (?:
            \s*=\s*
            (?:
                "([^"]*?)"   # Quotation marks
            |
                '([^']*?)'   # Apostrophes
            |
                ([^>\s]*)    # Unquoted
            )
        )?
        \s*"""
    END_RE = r'^\s*/\s*(.+)\s*'
    TOKEN_RE = r"""
      ([^<]+)?                                          # Text
      (?:
        <!--(.*?)--\s*>                                 # Comment
      |
        <!\[CDATA\[(.*?)\]\]>                           # CDATA
      |
        <!DOCTYPE(
          \s+\w+
          (?:(?:\s+\w+)?(?:\s+(?:"[^"]*"|'[^']*'))+)?   # External ID
          (?:\s+\[.+?\])?                               # Int Subset
          \s*
        )>
      |
        <(
          \s*
          [^<>\s]+                                      # Tag
          \s*
          (?:%s)*                                       # Attributes
        )>
      |
        (<)                                             # Runaway "<"
      )""" % (ATTR_RE)

    PARAGRAPH = [
        'address', 'article', 'aside', 'blockquote', 'dir',
        'div', 'dl', 'fieldset', 'footer', 'form', 'h1', 'h2',
        'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'main', 'menu', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'ul']

    END = dict(body=['head'],
               dd=['dt', 'dd'],
               dt=['dt', 'dd'],
               rp=['rt', 'rp'],
               rt=['rt', 'rp'],
               optgroup=['optgroup'],
               option=['option'])

    END.update({_: ['p'] for _ in PARAGRAPH})
    TABLE = {_: 1 for _ in ['colgroup', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr']}
    VOID = {_: 1 for _ in [
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'keygen', 'link', 'menuitem', 'meta', 'param', 'source', 'track', 'wbr']}

    _PHRASING = [
        'a', 'abbr', 'area', 'audio', 'b', 'bdi', 'bdo', 'br', 'button', 'canvas',
        'cite', 'code', 'data', 'datalist', 'del', 'dfn', 'em', 'embed', 'i', 'iframe', 'img',
        'input', 'ins', 'kbd', 'keygen', 'label', 'link', 'map', 'mark', 'math', 'meta', 'meter',
        'noscript', 'object', 'output', 'progress', 'q', 'ruby', 's', 'samp', 'script', 'select',
        'small', 'span', 'strong', 'sub', 'sup', 'svg', 'template', 'textarea', 'time', 'u', 'var',
        'video', 'wbr']

    OBSOLETE = ['acronym', 'applet', 'basefont', 'big', 'font', 'strike', 'tt']

    PHRASING = {_: 1 for _ in _PHRASING + OBSOLETE}

    del _PHRASING
    del OBSOLETE

    def parse(self, html):
        self.current = self.tree = ['root']
        token_re = re.compile('%s' % self.TOKEN_RE, re.X | re.S)
        token_iter = token_re.finditer(html)
        for m in token_iter:
            _ = m.group
            text,  comment, cdata, doctype, tag, runaway = \
                (_(1), _(2), _(3), _(4), _(5), _(10))

            if runaway:
                text += '<'
            if text:

                self.current.append(['text', html_unescape(text)])

            if tag:
                xml = False
                match = re.match(self.END_RE, tag)
                if match:

                    self._end(match.group(1)
                              if xml else match.group(1).lower(), xml)
                else:
                    match = re.match(r'([^\s/]+)([\s\S]*)', tag)
                    if match:

                        start = match.group(
                            1) if xml else match.group(1).lower()
                        attr = match.group(2)
                        attrs = {}
                        attr_re = re.compile(self.ATTR_RE, re.X)
                        attr_iter = attr_re.finditer(attr)

                        for m in attr_iter:
                            _ = m.group
                            k = _(1) if xml else _(1).lower()
                            value = _(2) or _(3) or _(4)

                            if k == '/':
                                continue
                            attrs[k] = html_unescape(value) if value else value
                        self._start(start, attrs, xml)
                        if (xml == False and self.VOID.get(start)) or re.match(r'\s*$', attr):
                            self._end(start, xml)

                        if start != 'script' and start != 'style':
                            continue
                        m = re.match(r'(.*?)<\s*%s\s*>' %
                                     (start), html, re.S | re.I)
                        if not m:
                            continue

                        self.current.append(['raw', m.group(1)])
                        self._end(start, xml)
            elif doctype:
                self.current.append(['doctype', doctype])

            elif comment:

                self.current.append(['comment', comment])
            elif cdata:
                self.current.append(['cdata', cdata])

        return self.tree

    def tree():
        doc = "The tree property."

        def fget(self):
            return self._tree

        def fset(self, value):
            self._tree = value

        def fdel(self):
            del self._tree
        return locals()
    tree = property(**tree())

    def render(self, tree, xml):
        self._render(tree, xml)

    def _close(self, xml, allowed, scope):
        parent = self.current
        while parent[0] != 'root' and parent[1] != scope:
            if allowed.get(parent[1]):
                self._end(parent[1], xml)
            parent = parent[3]

    def _end(self, end, xml):
        found = False
        next = self.current
        while next[0] != 'root':
            if next[1] == end:
                found = True
                break
            if not xml and self.PHRASING.get(end) and self.PHRASING.get(next[1]):
                return
            next = next[3]

        if not found:
            return

        next = self.current
        while next and self.current[0] != 'root':
            self.current = next
            next = self.current[3]
            if end == self.current[1]:
                self.current = self.current[3]
                return
            elif end == 'table':
                self._close(xml, self.TABLE, end)

            self._end(self.current[1], xml)

    def _render(self, tree, xml):
        _type = tree[0]
        if _type == 'text':
            return tree[1]

        if _type == 'raw':
            return tree[1]

        if _type == 'doctype':
            return '<DOCTYPE ' + tree[1] + '>'

        if _type == 'comment':
            return '<!--' + text[1] + '-->'

        if _type == 'cdata':
            return '<![CDATA[' + tree[1] + ']]>'

        start = 1
        content = ''
        if _type == 'tag':
            start = 4
            tag = tree[1]
            content += '<' + tag
            attrs = []
            for k in sorted(tree[2].keys()):
                value = tree[2][k]
                if not value:
                    attrs.append(k)
                    continue
                attrs.append(key + '="' + value + '"')
            content += ' '.join(attrs)
            if not tree[4]:
                return content + (' />' if xml or self.VOID.get(tag) else '></' + tag + '>')
            content += '>'

        for _ in range(start, len(tree)):
            content += self._render(tree[_], xml)

        if _type == 'tag':
            content += '<' + tree[1] + '>'

        return content

    def _start(self, start, attrs, xml):
        if not xml and self.current[0] != 'root':
            if self.END.get(start):
                [self._end(_, False) for _ in self.END.get(start)]
            elif start != 'li':
                self._close(False,  dict(li=True), 'ul')
            elif [_ for _ in ['colgroup', 'thead', 'tbody', 'tfoot'] if _ != start]:
                self._close(False, self.TABLE, 'table')
            elif start == 'tr':
                self._close(False, {'tr': True}, 'table')
            elif start in ['th', 'td']:
                [self._close(False, {_: True}, 'table')
                 for _ in ['th', 'td']]
        _new = ['tag', start, attrs, self.current]
        self.current.append(_new)
        self.current = _new


DATA =\
"""<head><script async="" src="http://ihi.xiami.com/listen/talents?callback=jQuery19107316461594309658_1389445002480&amp;_=1389445002481"></script><script async="" src="http://ihi.xiami.com/friends/list?callback=jQuery19107316461594309658_1389445002477&amp;_=1389445002479"></script>

<meta charset="UTF-8">
<meta name="renderer" content="webkit">
<meta content="a1z1s" name="data-spm">
<title>虾米音乐网(xiami.com) - 高品质音乐 发现 分享   </title>
<meta name="verify-v1" content="gNntuhTm2rH7Qa/GPp6lf0mIp9KQsjejNs+i1LZhG7U=">
<meta name="keywords" content="虾米网,在线音乐网站,在线听歌,音乐网站,在线音乐试听,音乐搜索,音乐下载,APE,数字音乐,高品质音乐,mp3下载,高品质mp3,音乐P2P分享,音乐社区,音乐互动平台,音乐分享,乐评,高品质音乐社区,网络电台,老歌,无损音乐,P2P下载,音乐SNS,320K,320Kbps  ">
<meta name="description" content="提供高品质音乐MP3的个性化推荐、发布、P2P下载服务，以及线下音乐活动等互动内容">
<meta name="apple-itunes-app" content="app-id=595594905">

<link href="http://res.xiami.net/??static/lib/jquery.jscrollpane.css,static/js/plug/poshytip-1.2/src/tip-twitter/tip-twitter.css,static/relation/css/name_card.css?ver=20140109-160920" media="all" rel="stylesheet">

<script type="text/javascript" async="" src="http://www.google-analytics.com/ga.js"></script><script type="text/javascript" src="http://res.xiami.net/??static/lib/jquery-1.9.1.min.js,static/lib/jquery-ui-1.10.3.custom.min.js,static/lib/jquery.tools.tabs.min.js,static/lib/jqmodal.js,res/js/jquery/jqDnR.js,res/js/jquery/jquery.form.js,res/js/jquery/jquery.cookie.js,static/js/lib/jquery.tmpl.min.js?ver=20140109-160920"></script><style type="text/css"></style>

<script type="text/javascript" src="http://res.xiami.net/??static/lib/jquery.mousewheel.js,static/lib/jquery.jscrollpane.min.js,static/js/plug/poshytip-1.2/src/jquery.poshytip.js,static/js/app/relation.js,static/js/app/nameCard-1.9.js,static/music/common/MusicPlay.js?ver=20140109-160920"></script>


<link href="http://res.xiami.net/??static/common/reset.css,static/common/base.css,static/common/old.css,static/common/song.css,static/common/album.css,static/common/artist.css,static/common/collect.css,static/common/header.css,static/common/footer.css?ver=20140109-160920" media="all" rel="stylesheet">

<script type="text/javascript" src="http://res.xiami.net/??static/common/base.js,static/common/song.js,static/common/album.js,static/common/artist.js,static/common/collect.js,static/common/header.js,static/common/footer.js?ver=20140109-160920"></script>


<script>
var _xiamitoken = $.cookie('_xiamitoken'),
    _xiamiimg = 'http://img.xiami.net',
    _xiamiuser = $.cookie('user');
</script>

<link href="http://res.xiami.net/??static/index/index.css,static/index/modules/slider.css,static/index/modules/recommend.css,static/index/modules/albums.css,static/index/modules/collects.css,static/index/modules/charts.css,static/index/modules/login.css,static/index/modules/user.css,static/index/modules/newbie.css?ver=20140109-160920" media="all" rel="stylesheet">
<link href="http://res.xiami.net/??static/index/common/album.css,static/index/common/collect.css,static/index/common/song.css?ver=20140109-160920" media="all" rel="stylesheet">
<link href="http://res.xiami.net/??static/index/modules/timeline.css,static/index/modules/scene.css,static/index/modules/task.css,static/index/modules/friend.css,static/index/modules/group.css,static/index/modules/personalnav.css,static/index/modules/personalblock.css,static/index/modules/follow.css?ver=20140109-160920" media="all" rel="stylesheet">

<script type="text/javascript" src="http://res.xiami.net/??static/index/index.js,static/index/modules/slider.js,static/index/modules/recommend.js,static/index/modules/albums.js,static/index/modules/collects.js,static/index/modules/charts.js,static/index/modules/login.js,static/index/modules/newbie.js,static/lib/jquery.carouFredSel.js?ver=20140109-160920"></script>
<script type="text/javascript" src="http://res.xiami.net/??static/index/modules/user.js,static/index/modules/timeline.js,static/lib/jquery.autoSuggest.js,static/index/modules/scene.js,static/index/modules/task.js,static/index/modules/friend.js,static/index/modules/group.js,static/index/modules/personalnav.js,static/index/modules/personalblock.js?ver=20140109-160920"></script>


<!-- google ads -->
<script type="text/javascript" src="http://partner.googleadservices.com/gampad/google_service.js?v=201307175516"></script>
<script type="text/javascript">GS_googleAddAdSenseService("ca-pub-2784367241150493");GS_googleEnableAllServices();</script>
<script type="text/javascript">
GA_googleAddSlot("ca-pub-2784367241150493", "Home-Apps-Promotion");</script>
<script type="text/javascript">GA_googleFetchAds();</script>
<!-- end -->

<script type="text/javascript" async="" id="tb-beacon-aplus" exparams="category=&amp;userid=&amp;aplus&amp;member_auth=1jmcT9xN4z9mg%252FeQT4E4IHEYtezVGDnQxIhZhuEos1QkdoldYoP7x6uXQg5L3CWUkY%252B6jw" src="http://a.tbcdn.cn/s/aplus_v2.js"></script><style id="poshytip-css-tip-twitter" type="text/css">div.tip-twitter{visibility:hidden;position:absolute;top:0;left:0;}div.tip-twitter table.tip-table, div.tip-twitter table.tip-table td{margin:0;font-family:inherit;font-size:inherit;font-weight:inherit;font-style:inherit;font-variant:inherit;vertical-align:middle;}div.tip-twitter td.tip-bg-image span{display:block;font:1px/1px sans-serif;height:10px;width:10px;overflow:hidden;}div.tip-twitter td.tip-right{background-position:100% 0;}div.tip-twitter td.tip-bottom{background-position:100% 100%;}div.tip-twitter td.tip-left{background-position:0 100%;}div.tip-twitter div.tip-inner{background-position:-10px -10px;}div.tip-twitter div.tip-arrow{visibility:hidden;position:absolute;overflow:hidden;font:1px/1px sans-serif;}</style></head>"""

if __name__ == '__main__':
    from angel.css import CSS
    import pprint
    html = HTML()
    # print '<div id="value"><p id="info">hello</p><h2
    # id="warn">warn</h2></div>'
    tree = html.parse(
        '<div id="foo"><p id="info" class="error">hello</p><p id="info2" class="error">last</p><h2 id="warn">warn</h2></div>')
    # tree = html.parse(DATA)
    css = CSS(tree)
    pprint.pprint(css.select('p:nth-last-of-type(2)'))
