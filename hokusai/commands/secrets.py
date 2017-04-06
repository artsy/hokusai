from hokusai.command import command
from hokusai.secret import Secret

@command
def get_secrets(context):
  secret = Secret(context)
  secret.load()
  for k, v in secret.all():
    print("%s=%s" % (k, v))

@command
def set_secrets(context, secrets):
  secret = Secret(context)
  secret.load()
  for s in secrets:
    if '=' not in s:
      print_red("Error: secrets must be of the form 'KEY=VALUE'")
      return -1
    split = s.split('=', 1)
    secret.update(split[0], split[1])
  secret.save()

@command
def unset_secrets(context, secrets):
  secret = Secret(context)
  secret.load()
  for s in secrets:
    secret.delete(s)
  secret.save()
