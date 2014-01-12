from angel.html import HTML
from angel.css import CSS
from angel.dom import DOM


__version__ = '0.1.0'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = ['HTML', 'CSS', 'DOM']

