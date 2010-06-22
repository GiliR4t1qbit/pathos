#!/usr/bin/env python
"""
interface to core pathos commands
"""

def copy(file,rhost,dest):
  from LauncherSCP import LauncherSCP
  copier = LauncherSCP('copy_%s' % file)
 #print 'executing {scp %s %s:%s}' % (file,rhost,dest)
  copier.stage(options='-q', source=file, destination=rhost+':'+dest)
  copier.launch()
  return


def run(command,rhost,bg=True): #XXX: default should be fg=True ?
  if not bg: fgbg = 'foreground'
  else: fgbg = 'background'
  from LauncherSSH import LauncherSSH
  launcher = LauncherSSH('%s' % command)
 #print 'executing {ssh %s "%s"}' % (rhost,command)
  launcher.stage(options='-q', command=command, rhost=rhost, fgbg=fgbg)
  launcher.launch()
  return launcher.response() #XXX: should return launcher, not just response


def kill(pid,rhost): #XXX: launcher should have method to "kill self"
  command = 'kill -n TERM %s' % pid #XXX: TERM=15 or KILL=9 ?
  return run(command,rhost,bg=False)


def getpid(target,rhost): #XXX: or 'ps -j' for pid, ppid, pgid ?
 #command = "ps -A | grep '%s'" % target #XXX: 'other users' only
  command = "ps ax | grep '%s'" % target #XXX: 'all users'
  print 'executing {ssh %s "%s"}' % (rhost,command)
  response = run(command,rhost)
  pid = response.split(" ")[0:2] # pid is 1st or 2nd element of response string
  return pid[0] or pid[1]


def pickport(rhost):
  from pox import which, getSEP
  file = which('portpicker.py') #file = 'util.py'
  dest = '~' #FIXME: *nix only

  from time import sleep
  delay = 0.0

  # copy over the port selector to remote host
  print 'executing {scp %s %s:%s}' % (file,rhost,dest)
  copy(file,rhost,dest)
  file = file.split(getSEP())[-1]   # save only the filename
  sleep(delay)

  # get an available remote port number
  command = 'python %s' % file
  print 'executing {ssh %s "%s"}' % (rhost,command)
  try:
    rport = int(run(command,rhost,bg=False))
  except:
    from Tunnel import TunnelException
    raise TunnelException, "failure to pick remote port"
  #print rport
  sleep(delay)

  # remove temporary remote file (i.e. the port selector file)
  dest = dest+'/'+file  #FIXME: *nix only
  command = 'rm -f %s' % dest #FIXME: *nix only
  print 'executing {ssh %s "%s"}' % (rhost,command)
  run(command,rhost)

  # return remote port number
  return rport


def connect(rhost,rport):
  from Tunnel import Tunnel
  t = Tunnel('Tunnel')
  lport = t.connect(rhost,rport)
  #FIXME: want to have r.lport, r.rport, r.rhost as class members
  return t,lport


def serve(server,rhost,rport,profile='.bash_profile'):
  file = '~/bin/%s.py' % server  #XXX: _should_ be on the $PATH
  #file = '%s.py' % server
  command = "source %s; %s -p %s" % (profile,file,rport)
  from LauncherSSH import LauncherSSH
  rserver = LauncherSSH('%s' % command)
  print 'executing {ssh %s "%s"}' % (rhost,command)
  rserver.stage(options='-q', command=command, rhost=rhost, fgbg='background')
  rserver.launch()
  response = rserver.response()
  if response in ['', None]: #XXX: other responses allowed (?)
    pass
  else:
    print response #XXX: not really error checking...
  from time import sleep
  delay = 2.0
  sleep(delay)
  return response


if __name__ == '__main__':
  pass

