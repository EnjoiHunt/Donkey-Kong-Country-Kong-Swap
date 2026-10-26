"""8x8 HUD tiles for the world-map stats: digits 0-9, '/', a banana and a K."""
FONT = {
 '0': ["0110", "1001", "1001", "1001", "1001", "1001", "0110"],
 '1': ["0010", "0110", "0010", "0010", "0010", "0010", "0111"],
 '2': ["0110", "1001", "0001", "0010", "0100", "1000", "1111"],
 '3': ["1110", "0001", "0001", "0110", "0001", "0001", "1110"],
 '4': ["0010", "0110", "1010", "1010", "1111", "0010", "0010"],
 '5': ["1111", "1000", "1110", "0001", "0001", "1001", "0110"],
 '6': ["0110", "1000", "1000", "1110", "1001", "1001", "0110"],
 '7': ["1111", "0001", "0010", "0010", "0100", "0100", "0100"],
 '8': ["0110", "1001", "1001", "0110", "1001", "1001", "0110"],
 '9': ["0110", "1001", "1001", "0111", "0001", "0001", "0110"],
 '/': ["0001", "0001", "0010", "0010", "0100", "0100", "1000"],
}
BANANA = ["........",
          "......d.",
          ".....yd.",
          "....yyd.",
          "..yyyd..",
          "yyyyd...",
          ".ddd....",
          "........"]
KLET = ["dddd.ddd",
        "dyyd.dyd",
        "dyydyyd.",
        "dyyyyd..",
        "dyyyyd..",
        "dyydyyd.",
        "dyyd.dyd",
        "dddd.ddd"]


def grid_char(rows, fg, outline):
    """centre a 4x7 glyph in 8x8 with a one-pixel outline"""
    g = [[0] * 8 for _ in range(8)]
    pts = [(r, c) for r, row in enumerate(rows) for c, ch in enumerate(row) if ch == '1']
    oy, ox = 0, 2
    for r, c in pts:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                y, x = r + oy + dy, c + ox + dx
                if 0 <= y < 8 and 0 <= x < 8 and g[y][x] == 0:
                    g[y][x] = outline
    for r, c in pts:
        g[r + oy][c + ox] = fg
    return g


def grid_pic(rows, cmap):
    return [[cmap.get(ch, 0) for ch in row] for row in rows]


def tile_bytes(g):
    b = bytearray(32)
    for y in range(8):
        for x in range(8):
            v = g[y][x]; s = 7 - x
            for bit, o in ((0, 0), (1, 1), (2, 16), (3, 17)):
                if v >> bit & 1:
                    b[y * 2 + o] |= 1 << s
    return bytes(b)


def make(white, black, yellow, dark):
    tiles = [grid_char(FONT[c], white, black) for c in '0123456789/']
    tiles.append(grid_pic(BANANA, {'y': yellow, 'd': dark}))
    tiles.append(grid_pic(KLET, {'y': yellow, 'd': dark}))
    return b''.join(tile_bytes(g) for g in tiles), tiles
