import asyncio
import time
from multiprocessing import Event

class AsyncTCPClient:
    def __init__(self, host='127.0.0.1', port=8888,
                 confirmation_msg="CONFIRM", completed_msg="COMPLETE"):
        self.host = host
        self.port = port
        self.confirmation_msg = confirmation_msg
        self.completed_msg = completed_msg

        # These variables will be updated when the respective messages are received.
        self.confirmation_received = asyncio.Event()
        self.completed_received = asyncio.Event()

        self.reader = None
        self.writer = None
        self.read_task = None

    async def connect(self):
        """Establish connection and start the background read task."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        # Start reading from the server in a background task.
        self.read_task = asyncio.create_task(self._read_from_server())

    async def _read_from_server(self):
        """Continuously read from the server, updating state when specific messages arrive."""
        try:
            while True:
                data = await self.reader.readline()
                if not data:
                    print("[Client] Server closed the connection.")
                    break
                message = data.decode().strip()
                print("[Client] Received:", message)
                # Update confirmation if the expected text is found.
                if self.confirmation_msg in message:
                    self.confirmation_received.set()
                    print("[Client] Confirmation flag updated.")
                # Update completed flag if the expected text is found.
                if self.completed_msg in message:
                    self.completed_received.set()
                    print("[Client] Completed flag updated.")
        except asyncio.CancelledError:
            # The task was cancelled (likely during disconnect).
            pass

    async def send_message(self, message: str):
        """Send a message to the server."""
        if self.writer:
            self.writer.write((message + "\n").encode())
            await self.writer.drain()

    async def disconnect(self):
        """Cancel the read task and close the connection."""
        if self.read_task:
            self.read_task.cancel()
            try:
                await self.read_task
            except asyncio.CancelledError:
                pass
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()


async def interactive_client_main(host='127.0.0.1', port=8888, confirmation_msg="CONFIRM", completed_msg="COMPLETE"):
    async with AsyncTCPClient(host, port, confirmation_msg, completed_msg) as client:
        print("[Client] Connected. Type your messages (or type 'exit' to quit):")
        loop = asyncio.get_running_loop()
        while True:
            user_input = await loop.run_in_executor(None, input, "You> ")
            if user_input.strip().lower() in ("exit", "quit"):
                break
            await client.send_message(user_input)
            # Check state flags after sending
            if client.confirmation_received:
                print("[Main] Confirmation message has been received!")
            if client.completed_received:
                print("[Main] Completed message has been received!")
        print("[Client] Exiting interactive client...")

# --------------------------
# Example interactive usage:
# --------------------------
if __name__ == '__main__':
    asyncio.run(interactive_client_main('192.168.52.1', 8888, "Task_0_received", "Task_0_completed"))
    
