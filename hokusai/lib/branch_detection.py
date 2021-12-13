from hokusai.lib.common import shout
# This method is looking up the local git default branch (HEAD) and returning its name
# For example if HEAD is "main" it will return "main"
# If for any reason the lookup fails, it will return "main" as the default.

def detect_branch():
  try: 
    default_branch = shout("git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'")
    return default_branch
  except: 
    return "main"
  