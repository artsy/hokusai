import time
import multiprocessing
import signal

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import shout, EXIT_SIGNALS, select_context, kubernetes_object, CalledProcessError

def get_logs(pod_name, opts):
  shout("kubectl logs %s%s" % (pod_name, opts), print_output=True)

@command
def logs(context, timestamps, nlines, follow):
  config = HokusaiConfig().check()
  select_context(context)

  opts = ''
  if timestamps:
    opts += ' --timestamps'
  if nlines:
    opts += " --tail=%s" % nlines
  if follow:
    opts += ' --follow'

  pods = kubernetes_object('pod', selector="app=%s" % config.project_name)['items']

  if follow:
    # Get logs from each Pod async

    # Pool processes inherit signal handlers from the parent process, so to ignore it detatch the SIGINT handler, create the Pool, then re-attach
    # http://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = multiprocessing.Pool(len(pods))
    signal.signal(signal.SIGINT, original_sigint_handler)

    for pod in pods:
      pool.apply_async(get_logs, (pod['metadata']['name'], opts))

    try:
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      pool.terminate()

  else:
    for pod in pods:
      get_logs(pod['metadata']['name'], opts)
