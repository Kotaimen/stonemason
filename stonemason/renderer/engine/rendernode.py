# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.engine.rendernode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The basic interface and components of renderer nodes.
"""

__author__ = 'ray'
__date__ = '4/19/15'


class RenderNode(object):  # pragma: no cover
    """Render Node Interface

    The `RenderNode` renders a specified area of geographic features from a
    given data source into a requested representation, such as `image` or
    `vector`. Transformation and Composition could be performed by chaining
    various `RenderNode` together.

    :param name: A string literal that identifies the node.
    :type name: str

    """

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """Get name of the node."""
        return self._name

    def render(self, context):
        """Render a specified area of geographic features requested by the
        context.

        :param context: The context of the  rendering process.
        :type context: :class:`~stonemason.renderer.RenderContext`

        :return: The representation of specified features.
        :rtype: :class:`~stonemason.renderer.Feature`
        """
        raise NotImplementedError


class TermNode(RenderNode):  # pragma: no cover
    """Terminal Render Node Interface

    A `TermNode` acts as a leaf node in a render tree or a entire rendering
    process. It renders input datasource into the requested representation.
    It could also be transformed by :class:`~stonemason.renderer.engine.TransformNode`
    or composed with other nodes by :class:`~stonemason.renderer.engine.CompositeNode`.

    :param name: A string literal that identifies the node.
    :type name: str

    """

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)


class TransformNode(RenderNode):  # pragma: no cover
    """Transform Render Node Interface

    A `TransformNode` make transformation to the data of its parent node, such
    as filtering, formatting.

    :param name: A string literal that identifies the node.
    :type name: str

    :param node: A parent render node.
    :type node: :class:`~stonemason.renderer.RenderNode`

    """

    def __init__(self, name, node):
        RenderNode.__init__(self, name)
        self._node = node

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.name, self._node)


class CompositeNode(RenderNode):  # pragma: no cover
    """Composite Render Node Interface

    A `CompositeNode` compose results of parent nodes into one result. It could
    composes not only :class:`~stonemason.renderer.TermNode` but also
    :class:`~stonemason.renderer.TransformNode`, and even
    :class:`~stonemason.renderer.CompositeNode` itself.

    :param name: A string literal that identifies the node.
    :type name: str

    :param nodes: A list of render nodes.
    :type nodes: list

    """

    def __init__(self, name, nodes):
        RenderNode.__init__(self, name)
        self._nodes = nodes

    def __repr__(self):
        components = ', '.join('%r' % l for l in self._nodes)
        return '%s(%r, %s)' % (self.__class__.__name__, self.name, components)


class NullTermNode(TermNode):
    """Null Terminal Node

    Dummy terminal node that produce ```None``` result.

    """

    def render(self, context):
        return None


class NullTransformNode(TransformNode):
    """Null Transform Node

    Dummy transform node that transform any input into ```None```.

    """

    def render(self, context):
        return None


class NullCompositeNode(CompositeNode):
    """Null Transform Node

    Dummy transform node that compose any inputs into ```None```.

    """

    def render(self, context):
        return None
