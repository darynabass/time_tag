from services.rfid_reading import RFIDReading


class RFIDController:
    """Control the RFID reader."""

    def __init__(self) -> None:
        """Initialize the RFID controller."""
        self.reader = RFIDReading()

    def start(self) -> None:
        """Start the RFID reader."""
        self.reader.start()

    def get_card(self) -> str | None:
        """Get the UID of the scanned RFID card.

        Returns:
            str | None: The card UID if a card is detected,
            or None if the reader is not running or no card is detected.
        """
        if not self.reader.running:
            return None

        return self.reader.get_card(timeout=0)

    def stop(self) -> None:
        """Stop the RFID reader."""
        self.reader.stop()
