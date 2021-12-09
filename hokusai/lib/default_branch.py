from hokusai.lib.common import shout

def detect_branch():
  try: 
    default_branch = shout("git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'")
    return default_branch
  except: 
    return "main"
  