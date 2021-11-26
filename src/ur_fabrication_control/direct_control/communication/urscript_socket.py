from ..utilities import islist

__all__ = [
    'URSocketComm'
]


class URSocketComm:
    # --- Socket essentials ---
    def socket_open(self, ip="192.168.10.11", port=50002, name="socket_0"):
        """Open socket connection
        """
        self.add_lines(['textmsg("Opening socket connection...")',
                       'socket_open("{}", {}, "{}")'.format(ip, port, name)])
        self.sockets[name] = (ip, port)

    def socket_close(self, name="socket_0"):
        """Close socket connection
        """
        self.add_lines(['textmsg("Closing socket connection' +
                        ' with {}...")'.format(name),
                        'socket_close(socket_name=' +
                        '"{}")'.format(self.__get_socket_name(name))])
        del self.sockets[name]

    # --- Socket send commands ---
    def socket_send_line(self, line, socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        """Send a single line to the socket.

        Parameters
        ----------
        line : string
            A single line to send to the socket.

        Returns
        -------
        None

        """
        func = 'socket_send_line({}, socket_name="{}")'.format(
            line, self.__get_socket_name(socket_name, address))
        return self._once_socket_wrapper(func)

    def socket_send_line_string(self, line, socket_name="socket_0",
                                address=("192.168.10.11", 50002)):
        """Send a single line to the socket.

        Parameters
        ----------
        line : string
            A single line to send to the socket.

        Returns
        -------
        None

        """
        func = 'socket_send_line("{}", socket_name="{}")'.format(
            line, self.__get_socket_name(socket_name, address))
        return self._once_socket_wrapper(func)

    def socket_send_int(self, integer, socket_name="socket_0",
                        address=("192.168.10.11", 50002)):
        func = 'socket_send_int({}, socket_name="{}")'.format(
            integer, self.__get_socket_name(socket_name, address))
        return self._once_socket_wrapper(func)

    def socket_send_ints(self, integers, var_name="ints",
                         socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        kwargs_dict = {self.__get_socket_name(socket_name, address):
                       address, self._get_var_name(var_name): integers}
        func = 'socket_send_int({1}[i], socket_name="{0}")'.format(
            *kwargs_dict.keys())
        return self._while_socket_wrapper(func, **kwargs_dict)

    def socket_send_float(self, float_value, socket_name="socket_0",
                          address=("192.168.10.11", 50002)):
        raise NotImplementedError

    def socket_send_byte(self, byte, socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        """Send a single line to the socket.

        Parameters
        ----------
        byte : bytes
            Byte to send to the socket.

        Returns
        -------
        None

        """
        func = 'socket_send_byte({}, socket_name="{}")'.format(
            byte, self.__get_socket_name(socket_name, address))
        return self._once_socket_wrapper(func)

    def socket_send_bytes(self, bytes_list, var_name="bytes",
                          socket_name="socket_0",
                          address=("192.168.10.11", 50002)):
        kwargs_dict = {self.__get_socket_name(socket_name, address):
                       address, self._get_var_name(var_name): bytes_list}
        func = 'socket_send_byte({1}[i], socket_name="{0}")'.format(
            *kwargs_dict.keys())
        return self._while_socket_wrapper(func, **kwargs_dict)

    # --- Socket read commands ---
    def socket_read_binary_integer(self, var_name="msg_recv_0", number=1,
                                   socket_name="socket_0",
                                   address=("192.168.10.11", 50002),
                                   timeout=2):
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '{} = '.format(var_name) +
            'socket_read_binary_integer({}, '.format(number) +
            'socket_name={}, timeout={})'.format(sock_name, timeout),
            'textmsg({})'.format(var_name)
        ])

    def socket_read_string(self, var_name="msg_recv_0", prefix="", suffix="",
                           int_escape=False, socket_name="socket_0",
                           address=("192.168.10.11", 50002), timeout=2):
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '{} = socket_read_string'.format(var_name) +
            '(socket_name="{}", prefix="{}", '.format(sock_name, prefix) +
            'suffix="{}", interpret_escape={}'.format(suffix, int_escape) +
            ', timeout={})'.format(timeout),
            'textmsg({})'.format(var_name)
        ])

    # --- Socket utilities ---
    def __get_socket_name(self, name, address=None):
        if name in self.sockets.keys():
            return name
        elif (address != ("192.168.10.11", 50002)
              and (address in self.sockets.values())):
            return self.sockets.keys()[self.sockets.values().index(address)]
        else:
            raise Exception("No open sockets available with name or address!")

    def _while_socket_wrapper(self, func, **kwargs):
        lines = []
        for key, value in kwargs.items():
            if isinstance(value, list):
                lines.append('{} = {}'.format(key, value))
        lines.append(['i = 0',
                      'while i < {}:'.format(min(map(len, filter(islist,
                                             kwargs.values())))),
                      '\tsent = ' + func,
                      '\tif sent == True:',
                      '\t\ti = i + 1',
                      '\t\tsent = False',
                      '\tend',
                      'end'])
        self.add_lines(lines)
        return lines

    def _once_socket_wrapper(self, func):
        lines = ['sent = False',
                 'while sent == False:',
                 '\tsent = ' + func,
                 'end']
        self.add_lines(lines)
        return lines
