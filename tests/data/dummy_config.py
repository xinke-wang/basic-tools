_base_ = ['tests/data/default.py']

learning_rate = 0.001
momentum = 0.95

training_params = {'batch_size': 64, 'epochs': 20, 'verbose': 1}

data_transforms = {
    'train': {
        'normalize': True,
        'resize': (256, 256)
    },
    'val': {
        'normalize': True,
        'resize': (128, 128),
        'flip': True
    }
}

additional_info = 'This is a dummy config'

database_url = 'env:PJTOOLS_DUMMY_TEST_DATABASE_URL'
