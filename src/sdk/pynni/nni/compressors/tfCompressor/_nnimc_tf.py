import tensorflow as tf
from tensorflow import Graph, Operation, Tensor

from typing import List

__all__ = [
    'TfCompressor',
    'TfPruner',
    'TfQuantizer',
    '_tf_detect_prunable_layers'
]


class TfCompressor:
    """TODO"""

    def __init__(self):
        self._bound_model = None


    def compress(self, model):
        """
        Compress given graph with algorithm implemented by subclass.
        This will edit the graph.
        """
        assert self._bound_model is None, "Each NNI compressor instance can only compress one model"
        self._bound_model = model
        self.bind_model(model)

    def compress_default_graph(self):
        """
        Compress the default graph with algorithm implemented by subclass.
        This will edit the graph.
        """
        self.compress(tf.get_default_graph())


    def bind_model(self, model):
        """
        This method is called when a model is bound to the compressor.
        Users can optionally overload this method to do model-specific initialization.
        It is guaranteed that only one model will be bound to each compressor instance.
        """
        pass


class TfLayerInfo:
    def __init__(self, layer):
        self.name = layer.name
        self.layer = layer
        self.weight_index = None

        if layer.type == 'Conv2D':
            self.weight_index = 1
        else:
            raise ValueError('Unsupported layer')


def _tf_detect_prunable_layers(model):
    # search for Conv2D layers
    # TODO: whitelist
    return [ TfLayerInfo(op) for op in model.get_operations() if op.type == 'Conv2D' ]


class TfPruner(TfCompressor):
    """TODO"""

    def __init__(self):
        super().__init__()

    def calc_mask(self, layer_info, weight):
        """
        Pruners should overload this method to provide mask for weight tensors.
        The mask must have the same shape and type comparing to the weight.
        It will be applied with `multiply()` operation.
        This method works as a subgraph which will be inserted into the bound model.
        """
        raise NotImplementedError("Pruners must overload calc_mask()")


    def compress(self, model):
        super().compress(model)
        # TODO: configurable whitelist
        for layer_info in _tf_detect_prunable_layers(model):
            self._instrument_layer(layer_info)

    def _instrument_layer(self, layer_info):
        # it seems the graph editor can only swap edges of nodes or remove all edges from a node
        # it cannot remove one edge from a node, nor can it assign a new edge to a node
        # we assume there is a proxy operation between the weight and the Conv2D layer
        # this is true as long as the weight is `tf.Value`
        # not sure what will happen if the weight is calculated from other operations
        weight_op = layer_info.layer.inputs[layer_info.weight_index].op
        weight = weight_op.inputs[0]
        mask = self.calc_mask(layer_info, weight)
        new_weight = weight * mask
        tf.contrib.graph_editor.swap_outputs(weight_op, new_weight.op)


class TfQuantizer(TfCompressor):
    def __init__(self):
        super().__init__()

    def quantize_weight(self, layer_info, weight) -> Tensor:
        raise NotImplementedError()


    def compress(self,  model):
        for layer_info in _tf_detect_prunable_layers(model):
            self._instrument_layer(layer_info)

    def _instrument_layer(self, layer_info):
        weight_op = layer_info.layer.inputs[layer_info.weight_index].op
        new_weight = self.quantize_weight(layer_info, weight_op.inputs[0])
        tf.contrib.graph_editor.swap_outputs(weight_op, new_weight.op)