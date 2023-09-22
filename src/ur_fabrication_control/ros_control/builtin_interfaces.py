from roslibpy import Message

class Duration(Message):
    def __init__(self, sec=0, nanosec=0, values=None):
        super().__init__(values)
        self.update({
            'sec': sec,
            'nanosec': nanosec
        })
        