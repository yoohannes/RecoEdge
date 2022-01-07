import logging
import json
import asyncio
from federated_worker import FederatedWorker
from fedrec.communications.worker_manager import WorkerComManager
from fedrec.communications.comm_manager import (CommunicationManager,
                                                tag_reciever)
from fedrec.utilities.serialization import serialize_object
from fedrec.communications.messages import (ProcMessage, JobSubmitMessage,
                                            ModelRequestMessage,
                                            ModelResponseMessage)


class WorkerComManager(CommunicationManager):
    def __init__(self, trainer, worker_id, config_dict):
        super().__init__(config_dict=config_dict)
        self.trainer = trainer
        self.round_idx = 0
        self.id = worker_id

    def run(self):
        super().run()

    # TODO should come from topology manager

    def send_model(self, receive_id, weights, local_sample_num):
        message = ModelResponseMessage(
            self.id, receive_id, weights, local_sample_num)
        self.send_message(message)

    async def send_job(self, receive_id, job_type):
        if job_type == ProcMessage.TRAIN_JOB:
            message = JobSubmitMessage(
                job_type,
                self.id,
                receive_id,
                json.dumps(FederatedWorker.serialise())
            )
            to_block = True
        elif job_type == ProcMessage.TEST_JOB:
            message = JobSubmitMessage(
                job_type,
                self.id,
                receive_id,
                json.dumps(FederatedWorker.serialise())
            )
            to_block = False
        else:
            raise ValueError(f"Invalid job type: {job_type}")

        logging.info(
            f"Submitting job to global process manager of type: {job_type}")
        return await self.send_message(message, block=to_block)

    def request_model(self, receive_id):
        message = ModelRequestMessage(self.id, receive_id)
        self.send_message(message)
