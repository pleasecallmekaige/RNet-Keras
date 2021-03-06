from keras import backend as K

from keras import initializers
from keras import regularizers

from keras.engine.topology import Node
from keras.layers import Layer, InputLayer

class SharedWeightLayer(InputLayer):
    """
    Module implementing Weight Sharing among layers, to reduce training time and for faster convergence.
    As, Keras doesn't directly support WeightSharing, but supports Layer Sharing, so use SharedWeightLayer to solve this problem.
    Takes no input tensor and return Weight tensor.
    # Arguments
        size: size/shape of the weight tensor to be shared
        initializer: initializer used for initializing weights
        regularizer: regularizer for weight tensor
        name: str, name for the SharedWeight Layer
        **kwargs: Additional keyword arguments
    """
    def __init__(self, 
                 size,
                 initializer='glorot_uniform',
                 regularizer=None,
                 name=None,
                 **kwargs):
        self.size = tuple(size)
        self.initializer = initializers.get(initializer)
        self.regularizer = regularizers.get(regularizer)

        if not name:
            prefix = 'shared_weight'
            name = prefix + '_' + str(K.get_uid(prefix))

        Layer.__init__(self, name=name, **kwargs)

        with K.name_scope(self.name):
            self.kernel = self.add_weight(shape=self.size,
                                        initializer=self.initializer,
                                        name='kernel',
                                        regularizer=self.regularizer)


        self.trainable = True
        self.built = True

        input_tensor = self.kernel * 1.0

        self.is_placeholder = False
        input_tensor._keras_shape = self.size
        
        input_tensor._uses_learning_phase = False
        input_tensor._keras_history = (self, 0, 0)

        Node(self,
            inbound_layers=[],
            node_indices=[],
            tensor_indices=[],
            input_tensors=[input_tensor],
            output_tensors=[input_tensor],
            input_masks=[None],
            output_masks=[None],
            input_shapes=[self.size],
            output_shapes=[self.size])
        
    def get_config(self):
        """Returns the config of the layer.
        A layer config is a Python dictionary (serializable)
        containing the configuration of a layer.
        The same layer can be reinstantiated later
        (without its trained weights) from this configuration.
        The config of a layer does not include connectivity
        information, nor the layer class name. These are handled
        by `Network` (one layer of abstraction above).
        # Returns
            Python dictionary.
        """
        config = {
            'size': self.size,
            'initializer': initializers.serialize(self.initializer),
            'regularizer': regularizers.serialize(self.regularizer)
        }
        base_config = Layer.get_config(self)
        return dict(list(base_config.items()) + list(config.items()))

def SharedWeight(**kwargs):
    input_layer = SharedWeightLayer(**kwargs)

    outputs = input_layer.inbound_nodes[0].output_tensors
    if len(outputs) == 1: 
        return outputs[0]
    else:
        return outputs
