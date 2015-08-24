Mason Renderer
**************

.. automodule:: stonemason.renderer


Render Engine
=============

Core components of mason render engine.

Exceptions
----------

.. autoclass:: stonemason.renderer.engine.RendererError

.. autoclass:: stonemason.renderer.engine.DependencyNotFound

.. autoclass:: stonemason.renderer.engine.TokenError

.. autoclass:: stonemason.renderer.engine.InvalidToken

.. autoclass:: stonemason.renderer.engine.GrammarError

.. autoclass:: stonemason.renderer.engine.SourceNotFound

.. autoclass:: stonemason.renderer.engine.UnknownPrototype


Render Grammar
--------------

.. autoclass:: stonemason.renderer.engine.Token
    :members:

.. autoclass:: stonemason.renderer.engine.TermToken
    :members:

.. autoclass:: stonemason.renderer.engine.TransformToken
    :members:

.. autoclass:: stonemason.renderer.engine.CompositeToken
    :members:

.. autoclass:: stonemason.renderer.engine.DictTokenizer
    :members:

.. autoclass:: stonemason.renderer.engine.RenderGrammar
    :members:


Render Nodes
------------

.. autoclass:: stonemason.renderer.engine.RenderNode
    :members:

.. autoclass:: stonemason.renderer.engine.TermNode
    :members:

.. autoclass:: stonemason.renderer.engine.TransformNode
    :members:

.. autoclass:: stonemason.renderer.engine.CompositeNode
    :members:

Render Node Factory
-------------------

.. autoclass:: stonemason.renderer.engine.RenderNodeFactory
    :members:


Render Context
--------------

.. autoclass:: stonemason.renderer.engine.RenderContext
    :members:


Render Feature
--------------

.. autoclass:: stonemason.renderer.engine.Feature
    :members:


Data Source
===========

Implementations of data sources used render nodes.

Raster Data Domain
------------------

.. autoclass:: stonemason.renderer.datasource.DataDomain
    :members:

.. autoclass:: stonemason.renderer.datasource.ElevationDomain
    :members:

.. autoclass:: stonemason.renderer.datasource.RGBDomain
    :members:

Raster Data Source
------------------

.. autoclass:: stonemason.renderer.datasource.RasterDataSource
    :members:

.. autoclass:: stonemason.renderer.datasource.ElevationData
    :members:

.. autoclass:: stonemason.renderer.datasource.RGBImageData
    :members:
