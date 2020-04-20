from gradient import PerceptualGradient


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))


def get_gd_colors(cl_stop_1, cl_stop_2, N=4):
    output = []

    gd = PerceptualGradient(hex2rgb(cl_stop_1), hex2rgb(cl_stop_2))

    for j in range(N):
        rgb = gd.color(j / N)
        output.append(rgb2hex(*rgb))

    return output


def get_colors(stops, N=4):
    output = []

    for i in range(len(stops) - 1):
        output += get_gd_colors(stops[i], stops[i + 1], N)

    return output
