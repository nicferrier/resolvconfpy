#!/usr/bin/python

"""Python resolvconf implementation

resolvconf does configuring of a resolv.conf.

It takes 2 forms of command line:

 -a interface      indicates that resolvers for interface are on stdin
 -d interface      requests deletion of resolvers for the specified interface

You can also:

 -D <datadir>      to change where resolvconf.py stores it's data

When the resolver information is updated a resolv.conf is created in:

   <datadir>/resolv.conf

An almost unrelated-but-not-quite-feature is:

 -t <name>         test resolution of <name> with the resolver.

"""

import os
from os.path import exists
from os.path import join

import getopt
import sys
import logging
import glob
import re
import socket

DATADIR="/var/lib/resolvconfpy"
logger = logging.getLogger("resolvconf")

def configure(iface, addresses):
    if not exists(DATADIR):
        os.makedirs(DATADIR)
    fd = open(join(DATADIR, "%s.if" % iface), "w")
    try:
        print >>fd, "\n".join(addresses)
    except Exception:
        logger.error("could not write resolvconf for %s" % iface)
        sys.exit(1)
    finally:
        try:
            fd.close()
        except:
            logger.info("failed to close the fd for %s" % iface)
    # Convert the resolver state into a file
    makeresolvconf()

def delete(iface):
    if exists(join(DATADIR, iface)):
        try:
            os.remove(join(DATADIR, "%s.if" % iface))
        except:
            logger.error("failed to remove %s" % iface)
        else:
            makeresolvconf()

def makeresolvconf():
    search = []
    server = []
    for i in glob.glob(join(DATADIR, "*.if")):
        fd = open(i)
        try:
            lines = fd.read().split("\n")
        except:
            logger.error("couldn't read from %s" % i)
        else:
            search += [searchline \
                           for searchline in lines \
                           if re.match("^search .*", searchline)]
            server += [serverline \
                           for serverline in lines \
                           if re.match("^nameserver .*", serverline)]
    outfd = open(join(DATADIR, "resolv.conf"), "w")
    try:
        if search:
            print >>outfd, "\n".join(search).strip()
        if server:
            print >>outfd, "\n".join(server).strip()
    except:
        logger.error("failed to write the resolvconf resolver file")
    finally:
        try:
            outfd.close()
        except:
            logger.error("some error close the resolvconf resolver file")

def main():
    opts, args = getopt.getopt(sys.argv[1:], "a:d:D:t:hf")
    for o,a in opts:
        if o == "-D":
            global DATADIR
            DATADIR = a
            continue

        if o == "-a":
            iface = a
            addresses_data = sys.stdin.read()
            addresses = [item \
                             for item in addresses_data.split("\n") \
                             if item.strip() != ""]
            configure(iface, addresses)
            break

        if o == "-d":
            iface = a
            delete(iface)
            break

        if o == "-t":
            print socket.gethostbyname(a)
            break

        if o == "-h":
            print __doc__
            sys.exit(0)

if __name__ == "__main__":
    main()

# End
