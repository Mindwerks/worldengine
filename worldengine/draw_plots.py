import numpy
import matplotlib.pyplot as plot


def draw_hypsographic_plot(world):
    # Will draw a Hypsograhpic plot that contains information about the distribution of elevations in the world.
    # y-axis shows the elevation, x-axis shows how often a certain elevation occurs.
    # For further details see:
    #   https://en.wikipedia.org/wiki/Elevation#Hypsography
    #   http://www.ngdc.noaa.gov/mgg/global/etopo1_surface_histogram.html

    # Set up variables.
    sea_level = world.sea_level()
    fig = plot.figure()
    p = fig.add_subplot(111)

    # Prepare a list of available elevations by putting them into a sorted list, smallest point to highest.
    # 0 will refer to sea-level.
    y = world.elevation['data'] - sea_level
    y = numpy.sort(y, axis=None)  # flatten the array and order values by height

    # Corresponding x-values. Inverted so the highest values are left instead of right. x refers to %, hence [0, 100].
    x = numpy.arange(100, 0, -100.0 / y.size)

    # Plot the data.
    p.plot(x, y)

    # Cosmetics.
    p.set_ylim(y.min(), y.max())
    p.fill_between(x, y.min(), y, color='0.8')
    p.set_xlabel("Cumulative Area (% of World's Surface)")
    p.set_ylabel("Elevation (no units)")
    p.set_title("Hypsographic Curve - %s" % world.name)

    # Draw lines for sea-level, hill-level etc. The lines will get lighter with increasing height.
    th = world.elevation['thresholds']  # see generation.py->initialize_ocean_and_thresholds() for details
    for i in range(len(th)):
        if th[i][1] is None:
            continue
        color = numpy.interp(i, [0, len(th)], [0, 1.0])  # grayscale values, black to white; white will never be used
        p.axhline(th[i][1] - sea_level, color=str(color), linewidth=0.5)
        p.text(99, th[i][1] - sea_level, th[i][0], fontsize=8, horizontalalignment='right', verticalalignment='bottom' if th[i][1] - sea_level > 0 else 'top')

    p.set_xticks(range(0, 101, 10))

    return fig


def draw_hypsographic_plot_on_file(world, filename):
    fig = draw_hypsographic_plot(world)
    fig.savefig(filename)
    plot.close(fig)
