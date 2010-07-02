#
#    Copyright (c) 2007-2010 iMatix Corporation
#
#    This file is part of 0MQ.
#
#    0MQ is free software; you can redistribute it and/or modify it under
#    the terms of the Lesser GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    0MQ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    Lesser GNU General Public License for more details.
#
#    You should have received a copy of the Lesser GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import time
import zmq

def main():
    use_poll = '-p' in sys.argv
    use_copy = '-c' in sys.argv
    if use_copy:
        sys.argv.remove('-c')
    if use_poll:
        sys.argv.remove('-p')

    if len (sys.argv) != 4:
        print 'usage: local_lat [-c use-copy] [-p use-poll] <bind-to> <message-size> <roundtrip-count>'
        sys.exit (1)

    try:
        bind_to = sys.argv[1]
        message_size = int(sys.argv[2])
        roundtrip_count = int(sys.argv[3])
    except (ValueError, OverflowError), e:
        print 'message-size and roundtrip-count must be integers'
        sys.exit(1)

    ctx = zmq.Context()
    s = ctx.socket(zmq.REP)

    if use_poll:
        p = zmq.Poller()
        p.register(s)

    s.bind(bind_to)

    for i in range(0, roundtrip_count):
        if use_poll:
            res = p.poll()
            assert(res[0][1] & zmq.POLLIN)
        msg = s.recv(zmq.NOBLOCK if use_poll else 0, copy=use_copy)
        assert len(msg) == message_size

        if use_poll:
            res = p.poll()
            assert(res[0][1] & zmq.POLLOUT)
        s.send(msg, zmq.NOBLOCK if use_poll else 0, copy=use_copy)

    # Let the context finish messaging before ending.
    # You may need to increase this time for longer or many messages.
    time.sleep(2.0)

if __name__ == '__main__':
    main()
