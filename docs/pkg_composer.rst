Composer
********

.. module::stonemason.renderer.cartographer.imagery.composer

Map composing.

Image
=====

.. autoclass:: stonemason.renderer.cartographer.imagery.composer.Composer
    :members:

ImageMagick
-----------

.. autodata:: stonemason.renderer.cartographer.imagery.HAS_IMAGEMAGICK
    :annotation:

.. autoclass:: stonemason.renderer.cartographer.imagery.imagemagick.ImageMagickComposer
    :members:

Sample
------

Below is a complex composer command which generates a `newspaper` effect
with variable depth label haloing from for mapnik rendered images:

.. code-block:: shell

    # Apply ordered dither to landbase, mimics 'halftone dither' effect
    ( {{base}} -ordered-dither o8x8,4 )

    (
        # Use a different dither for some variation
        ( {{road}} )
        # Fill halo with land color and only render on top of roads
        ( {{label}} -channel A -morphology Dilate Disk:4 +channel +level-colors #ebe9e6 ) -compose Atop -composite
        -ordered-dither o4x4,4
    ) -compose Over -composite

    (
        # Increase lightness of labels, Multiply later...
        {{label}}
        -brightness-contrast +10
        # Mimics 'typewriter' effect, only works on thin fonts.
        # Find line joins of labels and thicken/darken them.
        # Uses ImageMagick's morphology operation, slow!
        ( +clone -channel A
          -morphology HMT LineJunctions
          -morphology Dilate Disk:1
          +channel
        ) -compose Multiply -composite
    )  -compose Darken -composite

    # Make "real" duotone effect, not fake color tint.
    # Convert to grayscale then apply duotone lookup table.

    # The reference duotone images are converted from
    # Photoshop's classic 'Duotone' mode library.
    -brightness-contrast -12x-10
    -colorspace gray mapnik/res/duotone/Bl-for-dark-cg9-cg2.png -clut

    # Finally, convert to paletted PNG format
    -dither none
    -colors 128

.. figure:: _static/newspaper.png
   :width: 100 %
   :alt: "Newspaper" map sample render
   :align: center

   Sample render using 4 mapnik layers and imagemagick composer
