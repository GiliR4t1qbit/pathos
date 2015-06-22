#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 1997-2015 California Institute of Technology.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/pathos/browser/pathos/LICENSE
#
# adapted from Mike McKerns' and June Kim's gsl SSHLauncher class
"""
This module contains the derived class for secure shell (ssh) launchers
See the following for an example.


Usage
=====

A typical call to a 'ssh launcher' will roughly follow this example:

    >>> # instantiate the launcher, providing it with a unique identifier
    >>> launcher = LauncherSSH('launcher')
    >>>
    >>> # configure the launcher to perform the command on the selected host
    >>> launcher(command='hostname', host='remote.host.edu')
    >>>
    >>> # execute the launch and retrieve the response
    >>> launcher.launch()
    >>> print launcher.response()
 
"""
__all__ = ['LauncherSSH']

from Launcher import Launcher

# broke backward compatability: 30/05/14 ==> replace base-class almost entirely
class LauncherSSH(Launcher):
    '''a popen-based ssh-launcher for parallel and distributed computing.'''

    def __init__(self, name=None, **kwds):
        '''create a ssh launcher

Inputs:
    name        -- a unique identifier (string) for the launcher
    host        -- hostname to recieve command [user@host is also valid]
    command     -- a command to send  [default = 'echo <name>']
    launcher    -- remote service mechanism (i.e. ssh, rsh)  [default = 'ssh']
    options     -- remote service options (i.e. -v, -N, -L)  [default = '']
    background  -- run in background  [default = False]
    stdin       -- file type object that should be used as a standard input
                   for the remote process.
        '''
        self.launcher = kwds.pop('launcher', 'ssh')
        self.options = kwds.pop('options', '')
        self.host = kwds.pop('host', 'localhost')
        super(LauncherSSH, self).__init__(name, **kwds)
        return

    def config(self, **kwds):
        '''configure a remote command using given keywords:

(Re)configure the copier for the following inputs:
    host        -- hostname to recieve command [user@host is also valid]
    command     -- a command to send  [default = 'echo <name>']
    launcher    -- remote service mechanism (i.e. ssh, rsh)  [default = 'ssh']
    options     -- remote service options (i.e. -v, -N, -L)  [default = '']
    background  -- run in background  [default = False]
    stdin       -- file type object that should be used as a standard input
                   for the remote process.
        '''
        if self.message is None:
            self.message = 'echo %s' % self.name #' '?
        else: # pare back down to 'command' # better, just save _command?
            if self.launcher:
                self.message = self.message.split(self.launcher, 1)[-1]
            if self.options:
                self.message = self.message.split(self.options, 1)[-1]
            if self.host:
                self.message = self.message.split(self.host, 1)[-1].strip()
            quote = ('"',"'")
            if self.message.startswith(quote) or self.message.endswith(quote):
                self.message = self.message[1:-1]
        if self.stdin is None:
            import sys
            self.stdin = sys.stdin
        for key, value in kwds.items():
            if key == 'command':
                self.message = value
            elif key == 'host':
                self.host = value
            elif key == 'launcher':
                self.launcher = value
            elif key == 'options':
                self.options = value
            elif key == 'background':
                self.background = value
            elif key == 'stdin':
                self.stdin = value

        self._stdout = None
        self.message = '%s %s %s "%s"' % (self.launcher,
                                          self.options,
                                          self.host,
                                          self.message)
        names = ['message','host','launcher','options','background','stdin']
        return dict((i,getattr(self, i)) for i in names)

    # interface
    __call__ = config
    pass


if __name__ == '__main__':
    pass


# End of file
