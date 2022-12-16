from ..utilities import islist

__all__ = [
    'URSocketComm'
]


class URSocketComm:
    # --- Socket essentials ---
    def set_socket(self, ip="192.168.10.11", port=50002, name="socket_0"):
        socket = {"{}".format(name): {"ip": ip, "port": port, "is_open": False}}
        self.sockets.update(socket)
        socket_variables = {"{}_name".format(name): '{} = "{}"'.format(name, name),
                            "{}_ip".format(name): '{}_ip = "{}"'.format(name, ip),
                            "{}_port".format(name): "{}_port = {}".format(name, port)}
        self.add_lines(socket_variables.values(), to_dict="globals",
                       keys=socket_variables.keys())

    def set_psuedo_socket(self, name="socket_0"):
        self.set_socket(ip="None", port=0, name=name)

    def socket_open(self, name="socket_0"):
        """Open socket connection
        """
        self.add_lines(['textmsg("Opening socket connection...")',
                       'socket_open({}_ip, {}_port, {})'.format(name, name, name)])
        self.sockets.get(name).update({"is_open": True})

    def socket_close(self, name="socket_0"):
        """Close socket connection
        """
        self.add_lines(['textmsg("Closing socket connection with {}...")'.format(name),
                        'socket_close(socket_name={})'.format(name)])
        self.sockets.get(name).update({"is_open": False})

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
        name = self.__get_socket_name(socket_name, address)
        func = 'socket_send_line({}, socket_name={})'.format(line, name)
        return self.add_line(func)
        # return self._once_socket_wrapper(func)

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
        name = self.__get_socket_name(socket_name, address)
        func = 'socket_send_line("{}", socket_name={})'.format(line, name)
        return self.add_line(func)
        # return self._once_socket_wrapper(func)

    def socket_send_int(self, integer, socket_name="socket_0",
                        address=("192.168.10.11", 50002)):
        name = self.__get_socket_name(socket_name, address)
        func = 'socket_send_int({}, socket_name={})'.format(integer, name)
        return self.add_line(func)

    def socket_send_ints(self, integers, var_name="ints",
                         socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        kwargs_dict = {self.__get_socket_name(socket_name, address):
                       address, self._get_var_name(var_name): integers}
        func = 'socket_send_int({1}[i], socket_name="{0}")'.format(
            *kwargs_dict.keys())
        return self._socket_send_list(func, None, **kwargs_dict)

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
        return self._while_socket_wrapper(func, None, **kwargs_dict)

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
    def __get_socket_name(self, name=None, address=None):
        if self.sockets.get(name, False):
            pass
        elif address is not None:
            for key, value in self.sockets.items():
                if [value.get("ip"), value.get("port")] == address:
                    name = key
                    break
        else:
            raise Exception("No sockets set with name or address!")
        if self.sockets.get(name).get("is_open"):
            return name
        else:
            self.socket_open(name)
            return name

    def _socket_send_list(self, func, *args, **kwargs):
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
