learning_rate = 0.01
momentum = 0.9
optimizer = 'Adam'
use_cuda = True
layers = [64, 128, 256]
input_shape = (3, 224, 224)

training_params = {'batch_size': 32, 'epochs': 10}

data_transforms = {
    'train': {
        'normalize': True,
        'resize': (128, 128)
    },
    'val': {
        'normalize': True,
        'resize': (128, 128)
    }
}

nested_list = [[1, 2, 3], [4, 5, 6]]
nested_tuple = ((1, 2), (3, 4))
