
class Player:
    def __init__(self, id, name, client):
        super().__init__()
        self.id = id
        self.name = name
        self.client = client

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exec_value, exec_traceback):
        self.client.close()

    @property
    def volume(self):
        response = self.client.send_command(
            "player/get_volume", params={"pid": self.id}
        )
        response.raise_for_result()
        return int(response.message_fields["level"])

    @volume.setter
    def volume(self, value: int):
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100")

        response = self.client.send_command(
            "player/set_volume", params={"pid": self.id, "level": value}
        )
        response.raise_for_result()

    @property
    def mute(self):
        response = self.client.send_command("player/get_mute", params={"pid": self.id})
        response.raise_for_result()
        return response.message_fields["state"] == "on"

    @mute.setter
    def mute(self, value: bool):
        response = self.client.send_command(
            "player/set_mute",
            params={"pid": self.id, "state": "on" if value else "off"},
        )
        response.raise_for_result()
