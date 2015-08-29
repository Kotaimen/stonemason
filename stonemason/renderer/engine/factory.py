# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.engine.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Factory interface that creates render nodes.
"""

__author__ = 'ray'
__date__ = '8/17/15'

from .rendernode import RenderNode
from .exceptions import UnknownPrototype, DependencyNotFound


class RenderNodeFactory(object):
    """Render Node Factory Interface

    The `RenderNodeFactory` creates various render nodes from prototype and
    related parameters. Subclass of :class:`~stonemason.renderer.engine.RenderNode`
    could be registered in the factory.

    The factory could create three different kinds of `RenderNode`,
    :class:`~stonemason.renderer.engine.TermNode`,
    :class:`~stonemason.renderer.engine.TransformNode` and
    :class:`~stonemason.renderer.engine.CompositeNode`.

    Subclass of this factory should take care of what kind of `RenderNode` to
    be registered.

    """

    def __init__(self):
        self._register = dict()

    def _lookup(self, prototype):
        try:
            init = self._register[prototype]
        except KeyError:
            raise UnknownPrototype('"%s"' % prototype)
        if init is None:
            raise DependencyNotFound(
                """Missing dependencies for: "%s"!""" % prototype)
        return init

    def register_node(self, prototype, node_class):
        """Register a render node with a prototype name.

        :param prototype: a string literal that identifies a render node.
        :type prototype: str

        :param node_class: class of render node.
        :type node_class: type
        """
        assert node_class is None or issubclass(node_class, RenderNode)
        self._register[prototype] = node_class

    def create_terminal_node(self, name, prototype, **parameters):
        """Create a terminal node.

        :param name: a string literal that identifies the node.
        :type name: str

        :param prototype: a string literal that identifies type of a render node.
        :type prototype: str

        :param parameters: related parameters used to create the node.
        :type parameters: dict
        """
        init = self._lookup(prototype)
        return init(name, **parameters)

    def create_transform_node(self, name, prototype, source, **parameters):
        """Create a transform node.

        :param name: a string literal that identifies the node.
        :type name: str

        :param prototype: a string literal that identifies type of a render node.
        :type prototype: str

        :param source: parent render node.
        :type source: :class:`~stonemason.renderer.engine.RenderNode`

        :param parameters: related parameters used to create the node.
        :type parameters: dict

        """
        init = self._lookup(prototype)
        return init(name, node=source, **parameters)

    def create_composite_node(self, name, prototype, sources, **parameters):
        """Create a composite node.

        :param name: a string literal that identifies the node.
        :type name: str

        :param prototype: a string literal that identifies type of a render node.
        :type prototype: str

        :param sources: a list of parent render nodes.
        :type sources: list

        :param parameters: related parameters used to create the node.
        :type parameters: dict
        """
        init = self._lookup(prototype)
        return init(name, nodes=sources, **parameters)
