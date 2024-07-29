# bed_exit_event.py
import asyncio

from api_server.gateway import rmf_gateway
from api_server.logger import logger
from api_server.rmf_io.events import sensor_events

# from api_server.workflows import BedExitFlow
from . import EventHandler, EventListener, Events


# Define the handler function for the bed_exit event
async def bed_exit_handler(data, service):
    logger.info(f"Handling event with data: {data}")
    if data.classification == "bed_exit":
        logger.warn(f"bed_exit event triggered")
        logger.warn(f"running {service} service")
    # Add your specific logic here


# Create the EventHandler instance
service = "bed_exit_service"  # Placeholder for service
bed_exit_event_handler = EventHandler(service, bed_exit_handler)

# Create the EventListener instance
stream = sensor_events.sensors
bed_exit_event_listener = EventListener(stream, bed_exit_event_handler)

# Create the Events instance
gateway = rmf_gateway()


def bedExitEvent():

    bed_exit_event = Events(
        name="bed_exit",
        service=service,
        stream=stream,
        gateway=gateway,
        handler=bed_exit_event_handler,
        listener=bed_exit_event_listener,
    )

    return bed_exit_event
