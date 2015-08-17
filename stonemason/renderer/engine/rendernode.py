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
