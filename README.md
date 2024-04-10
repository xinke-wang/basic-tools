# basic-tools

# Project Tools

**Project Tools** simplifies the process of building and configuring machine learning projects.

## Features

- **Auto Configuration**: Seamlessly load configurations from `.yaml`, `.py`, `.json` files, making your project setup cleaner and more manageable.

## Installation

**Project Tools** can be easily installed using pip or by cloning the repository.

### Using pip

```bash
pip install pjtools
```

### Cloning the Repository

To get the latest version and potentially modify the source code:

```bash
git clone https://github.com/xinke-wang/project-tools.git
cd project-tools
pip install -r requirements.txt
pip install -e .
```

## Quick Start

After installation, Project Tools is ready to streamline your machine learning project configuration. Here’s how you can use it:

### Auto Configuration

Imagine you have several configurations in a `.py` file like so:

```python
# config.py
_base_ = ['defaults/settings.py']  # Base configuration for inheritance

learning_rate = 0.001
momentum = 0.95
training_params = {'batch_size': 64, 'epochs': 20, 'verbose': 1}
```

With **Project Tools**, loading this configuration is as simple as:

```python
from pjtools.configurator import AutoConfigurator

config = AutoConfigurator.fromfile('path/to/config.py')
print(f"Learning Rate: {config.learning_rate}")
```
