# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Make example datasets.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from ..psf import GaussianPSF
from astropy.table import Table
from astropy.modeling.models import Gaussian2D


__all__ = ['make_gaussian_image', 'make_gaussian_sources',
           'make_random_gaussians']


def make_gaussian_image(shape, table):
    """Make an image of Gaussian sources.

    The input table must contain parameters for one Gaussian
    source per row with column names matching the
    `~photutils.GaussianPSF` parameter names.

    Parameters
    ----------
    shape : tuple of int
        Output image shape
    table : `~astropy.table.Table`
        Gaussian source catalog

    Returns
    -------
    image : `numpy.array`
        Gaussian source model image

    Examples
    --------

    .. plot::
        :include-source:

        # Simulate a Gaussian source catalog
        from numpy.random import uniform
        from astropy.table import Table
        n_sources = 100
        shape = (100, 200) # axis order: (y, x)
        table = Table()
        table['sigma'] = uniform(1, 2, n_sources)
        table['amplitude'] = uniform(2, 3, n_sources)
        table['x_0'] = uniform(0, shape[1], n_sources)
        table['y_0'] = uniform(0, shape[0], n_sources)

        # Make an image of the sources
        from photutils.datasets import make_gaussian_image
        from photutils import CircularAperture
        image = make_gaussian_image(shape, table)

        # Plot the image
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1)
        ax.imshow(image, origin='lower', interpolation='nearest')
        for source in table:
            aperture = CircularAperture((source['x_0'], source['y_0']),
                                        3 * source['sigma'])
            aperture.plot(color='white')
    """

    y, x = np.indices(shape)
    image = np.zeros(shape, dtype=np.float64)

    for source in table:
        model = GaussianPSF(amplitude=source['amplitude'], x_0=source['x_0'],
                            y_0=source['y_0'], sigma=source['sigma'])
        image += model(x, y)

    return image


def make_gaussian_sources(image_shape, source_table, noise_stddev=None,
                          seed=None):
    """
    Make an image containing 2D Gaussian sources.

    Parameters
    ----------
    image_shape : 2-tuple of int
        Shape of the output 2D image.

    source_table : `astropy.table.Table`
        Table of parameters for Gaussian sources.  The table must
        contain parameters for one Gaussian source per row with column
        names matching the `astropy.modeling.functional_models.Gaussian2D`
        parameter names.

    noise_stddev : float, optional
        The standard deviation of the noise to add to the output image.
        The default is `None`, meaning no noise will be added to the
        output image.

    seed : `None`, int, or array_like, optional
        Random seed initializing the pseudo-random number generator used
        to generate the noise image.  ``seed`` can be an integer, an
        array (or other sequence) of integers of any length, or `None`
        (the default).  Separate function calls with the same
        ``noise_stddev`` and ``seed`` will generate the identical noise
        image.  If ``seed`` is `None`, then a new random noise image
        will be generated each time.

    Returns
    -------
    image : `numpy.ndarray`
        Image containing 2D Gaussian sources and optional noise.

    Examples
    --------

    .. plot::
        :include-source:

        # make a table of Gaussian sources
        from astropy.table import Table
        table = Table()
        table['amplitude'] = [50, 70, 150, 210]
        table['x_mean'] = [160, 25, 150, 90]
        table['y_mean'] = [70, 40, 25, 60]
        table['x_stddev'] = [15.2, 5.1, 3., 8.1]
        table['y_stddev'] = [2.6, 2.5, 3., 4.7]
        table['theta'] = np.array([145., 20., 0., 60.]) * np.pi / 180.

        # make an image of the sources with and without noise
        from photutils.datasets import make_gaussian_sources
        shape = (100, 200)
        image1 = make_gaussian_sources(shape, table)
        image2 = make_gaussian_sources(shape, table, noise_stddev=5.,
                                       seed=12345)

        # make an image of the sources with and without noise
        # plot the images
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.imshow(image1, origin='lower', interpolation='nearest')
        ax2.imshow(image2, origin='lower', interpolation='nearest')
    """

    image = np.zeros(image_shape, dtype=np.float64)
    y, x = np.indices(image_shape)

    for source in source_table:
        model = Gaussian2D(amplitude=source['amplitude'],
                           x_mean=source['x_mean'], y_mean=source['y_mean'],
                           x_stddev=source['x_stddev'],
                           y_stddev=source['y_stddev'], theta=source['theta'])
        image += model(x, y)

    if noise_stddev is not None:
        if seed:
            prng = np.random.RandomState(seed)
        else:
            prng = np.random
        image += prng.normal(loc=0.0, scale=noise_stddev, size=image_shape)
    return image


def make_random_gaussians(image_shape, n_sources, amplitude_range,
                          xstddev_range, ystddev_range, noise_stddev=None,
                          seed=None):
    """
    Make an image containing random 2D Gaussian sources whose parameters
    are drawn from a uniform distribution.

    Parameters
    ----------
    image_shape : 2-tuple of int
        Shape of the output 2D image.

    n_sources : float
        The number of random Gaussian sources to add to the image.

    amplitude_range : array-like
        The lower and upper boundaries input as ``(lower, upper)`` over
        which draw source amplitudes from a uniform distribution.

    xstddev_range : array-like
        The lower and upper boundaries input as ``(lower, upper)`` over
        which draw source x_stddev from a uniform distribution.

    ystddev_range : array-like
        The lower and upper boundaries input as ``(lower, upper)`` over
        which draw source y_stddev from a uniform distribution.

    noise_stddev : float, optional
        The standard deviation of the noise to add to the output image.
        The default is `None`, meaning no noise will be added to the
        output image.

    seed : `None`, int, or array_like, optional
        Random seed initializing the pseudo-random number generator used
        to generate the Gaussian source parameters and noise image.
        ``seed`` can be an integer, an array (or other sequence) of
        integers of any length, or `None` (the default).  Separate
        function calls with the same ``seed`` will generate the
        identical sources and noise image.

    Returns
    -------
    image : `numpy.ndarray`
        Image containing 2D Gaussian sources and optional noise.

    Examples
    --------

    .. plot::
        :include-source:

        from photutils.datasets import make_random_gaussians
        shape = (300, 500)
        n_sources = 100
        amplitude_range = [50, 100]
        xstddev_range = [1, 5]
        ystddev_range = [1, 5]

        # make an image of random sources with and without noise.
        # seed is used here to generate the same random sources across
        # function calls.
        image1 = make_random_gaussians(shape, n_sources, amplitude_range,
                                       xstddev_range, ystddev_range,
                                       seed=12345)
        image2 = make_random_gaussians(shape, n_sources, amplitude_range,
                                       xstddev_range, ystddev_range,
                                       noise_stddev=5., seed=12345)

        # plot the images
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.imshow(image1, origin='lower', interpolation='nearest')
        ax2.imshow(image2, origin='lower', interpolation='nearest')
    """

    if seed:
        prng = np.random.RandomState(seed)
    else:
        prng = np.random
    sources = Table()
    sources['amplitude'] = prng.uniform(amplitude_range[0],
                                        amplitude_range[1], n_sources)
    sources['x_mean'] = prng.uniform(0, image_shape[1], n_sources)
    sources['y_mean'] = prng.uniform(0, image_shape[0], n_sources)
    sources['x_stddev'] = prng.uniform(xstddev_range[0], xstddev_range[1],
                                       n_sources)
    sources['y_stddev'] = prng.uniform(ystddev_range[0], ystddev_range[1],
                                       n_sources)
    sources['theta'] = prng.uniform(0, 2.*np.pi, n_sources)
    return make_gaussian_sources(image_shape, sources,
                                 noise_stddev=noise_stddev, seed=seed)
