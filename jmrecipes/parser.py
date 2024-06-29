import json
import yaml
from fractions import Fraction

from utils import to_fraction


def parse_recipe(filepath: str) -> dict:
    """Converts a recipe data file to a recipe dictionary.

    Args:
        filepath: Str path to recipe data file.

    Returns:
        Dict containing recipe data.
    """

    with open(filepath, 'r', encoding='utf8') as f:
        data = f.read()
    format = get_format(filepath)
    parser = get_parser(format)
    return parser(data)


def get_format(file: str) -> str:
    """Determines the format of a recipe data file.
    
    Args:
        file: Filename as a str.

    Returns:
        Str defining the format, eg 'json' or 'yaml'.

    Raises:
        ValueError: File format is not 'json' or 'yaml'.
    """

    if file.endswith('.json'):
        return 'json'
    elif file.endswith('.yaml'):
        return 'yaml'
    raise ValueError('file is not a valid format')


def get_parser(format: str):
    """Returns the parser function for a format.
    
    Args:
        format: As a string.

    Returns:
        Function to parse the given format.

    Raises:
        ValueError: Format is not 'json' or 'yaml'.
    """

    if format == 'json':
        return parse_from_json
    elif format == 'yaml':
        return parse_from_yaml
    
    raise ValueError(format)


def parse_from_json(data: str) -> dict:
    """Converts json data into a recipe input dictionary.

    Args:
        data: Json data as string.

    Returns:
        Recipe data dictionary.
    """

    return recipe_dict(json.loads(data))


def parse_from_yaml(data: str) -> dict:
    """Converts yaml data into a recipe input dictionary.

    Args:
        data: Yaml data as string.

    Returns:
        Recipe data dictionary.
    """

    return recipe_dict(yaml.safe_load(data))


def recipe_dict(data: dict) -> dict:
    """Restructures input dictionary to creates recipe dictionary.

    Args:
        data: Recipe input data as dictionary.

    Returns:
        Recipe data dictionary.
    """

    recipe = {}
    recipe['title'] = data['title']
    recipe['subtitle'] = data.get('subtitle', '')

    recipe['times'] = []
    for time in data.get('times', []):
        recipe['times'].append(parse_time(time))

    recipe['yield'] = []
    for d_yield in data.get('yield', []):
        recipe['yield'].append(parse_yield(d_yield))

    recipe['ingredients'] = []
    if 'ingredients' in data:
        for ingredient in data['ingredients']:
            recipe['ingredients'].append(parse_ingredient(ingredient))

    recipe['instructions'] = []
    if 'instructions' in data:
        for step in data['instructions']:
            recipe['instructions'].append(parse_step(step))

    recipe['scales'] = []
    recipe['scales'].append({'multiplier': Fraction(1)})
    for scale in data.get('scale',[]):
        recipe['scales'].append({
            'multiplier': read_multiplier(scale)
        })

    if 'cost' in data:
        recipe['explicit_cost'] = data['cost']

    if 'hide_cost' in data:
        recipe['hide_cost'] = data['hide_cost']


    return recipe


def read_multiplier(scale) -> Fraction:
    """Returns multiplier of a scale."""

    if not isinstance(scale, (int, float, str, dict)):
        raise TypeError('Scale must be a dict or number.')

    if isinstance(scale, dict):
        return to_fraction(scale['multiplier'])
    if isinstance(scale, (int, float, str)):
        return to_fraction(scale)

    
def parse_time(time: dict) -> dict:
    """Formats time data from input file."""

    if not isinstance(time, dict):
        raise TypeError('time must be a dict.')
    if 'name' not in time:
        raise KeyError('time must have a name.')
    if not isinstance(time['name'], str):
        raise TypeError('time name must be a string.')
    if 'time' not in time:
        raise KeyError('time must have a time.')
    if not isinstance(time['time'], (int, float)):
        raise TypeError(f'time time is a {type(time["time"])}, not a number.')
    if not isinstance(time.get('unit', ''), str):
        raise TypeError(f'time unit is a {type(time["unit"])}, not a string.')
    
    name = time['name']
    time_time = to_fraction(time['time'])
    time_data = {
        'name': name,
        'time': time_time,
        'unit': time.get('unit', '')
    }
    return time_data


def parse_ingredient(data: dict) -> dict:
    """Formats ingredient data from input file.

    Args:
        data: Ingredient input data as dictionary.

    Returns:
        Ingredient data as dictionary.
    """

    ingredient = {
        'number': to_fraction(data.get('number', 0)),
        'unit': data.get('unit', ''),
        'item': data.get('item', ''),
        'descriptor': data.get('descriptor', ''),
        'display_number': to_fraction(data.get('display_number', 0)),
        'display_unit': data.get('display_unit', ''),
        'display_item': data.get('display_item', ''),
    }
    if 'list' in data:
        ingredient['list'] = data['list']
    if 'scale' in data:
        ingredient['scale'] = data['scale']

    return ingredient


def parse_yield(data):
    """Formats yield data from input file."""

    return {
        'number': to_fraction(data['number']),
        'unit': data.get('unit', 'servings'),
        'show_yield': data.get('show_yield', ''),
        'show_serving_size': data.get('show_serving_size', '')
    }


def parse_step(data):
    """Formats instructions data from input file."""

    if isinstance(data, str):
        return {'text': data}
        
    if isinstance(data, dict) and 'text' in data:
        step = {'text': data['text']}
        if 'scale' in data:
            step['scale'] = data['scale']
        if 'list' in data:
            step['list'] = data['list']
        return step
    
