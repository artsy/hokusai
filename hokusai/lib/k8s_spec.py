def add_env(spec, newvar):
  """
  take a k8s container spec's 'env' property,
  return a new 'env' property with a new var added to it

  spec = the k8s container spec (as a dict, see YamlSpec)
  newvar = the var to be added to 'env'

  Example:

  - container spec:

    {
      'image': ...,
      'env': [
        {'name': 'var1', 'value': 'var1value'},
        {'name': 'var2', 'value': 'var2value'},
        ...
      ],
      ...
    }

  - newvar:

    {'name': 'foo', 'value': '123'}

  - return:

    [
      {'name': 'var1', 'value': 'var1value'},
      {'name': 'var2', 'value': 'var2value'},
      {'name': 'foo', 'value': '123'}
    ]
  """

  newenv = []
  if 'env' in spec and spec['env'] is not None:
    # 'env' property exists, and it is not None
    # remove any existing var whose 'name' is same as newvar's
    newenv = [var for var in spec['env'] if not ('name', newvar['name']) in list(var.items())]
    # add newvar
    newenv = newenv + [newvar]
  else:
    # 'env' property does not exist, or it does but it's None
    newenv = [newvar]

  return newenv
