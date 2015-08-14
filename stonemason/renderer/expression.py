# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/19/15'


class RenderNode(object):  # pragma: no cover
    """Abstract Layer Renderer"""

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def render(self, context):
        raise NotImplementedError


class TermNode(RenderNode):  # pragma: no cover
    """Abstract Terminal Render Node

    A `TermNode` is a leaf node in a render tree.
    """

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)


class TransformNode(RenderNode):  # pragma: no cover
    """Abstract Transform Render Node"""

    def __init__(self, name, node):
        RenderNode.__init__(self, name)
        self._node = node

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.name, self._node)


class CompositeNode(RenderNode):  # pragma: no cover
    """Abstract Composite Render Node"""

    def __init__(self, name, nodes):
        RenderNode.__init__(self, name)
        self._nodes = nodes

    def __repr__(self):
        components = ', '.join('%r' % l for l in self._nodes)
        return '%s(%r, %s)' % (self.__class__.__name__, self.name, components)


class NullNode(TermNode):
    def render(self, context):
        return None


class RenderNodeFactory(object):
    def __init__(self):
        self._register = dict()

    def _lookup(self, prototype):
        init = self._register.get(prototype)
        if init is None:
            raise ValueError('Unknown prototype: "%s"!' % prototype)
        return init

    def create_terminal_node(self, name, prototype, **parameters):
        init = self._lookup(prototype)
        return init(name, **parameters)

    def create_transform_node(self, name, prototype, source, **parameters):
        init = self._lookup(prototype)
        return init(name, node=source, **parameters)

    def create_composite_node(self, name, prototype, sources, **parameters):
        init = self._lookup(prototype)
        return init(name, nodes=sources, **parameters)


class ImageNodeFactory(RenderNodeFactory):
    def __init__(self):
        RenderNodeFactory.__init__(self)

    def load_node(self, prototype, node_class):
        assert node_class is None or issubclass(node_class, RenderNode)
        self._register[prototype] = node_class
