import enum


class FlowStatus(enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"

    def is_ended(self):
        return self in (self.COMPLETED, self.FAILED)
