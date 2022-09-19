# visualizer

Visualizer is a Django web application that consumes a dynamic BPM stream via an Ableton Link session on a LAN allowing for real time visualizations in a web frontend with JavaScript.

## Screenshots

![Alt text](screenshots/screenshot1.png?raw=true "Index")


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Make sure Docker is installed on your system.

You will need access to a LAN that can connect your Ableton Link enabled device with the computer running this project.

On windows, start the Carabiner binary then start the docker project.

## Built With

* [Ableton Link](https://www.ableton.com/en/link/) - In-time network based BPM sync protocol
* [Django](https://www.djangoproject.com/) - Web application framework
* [Kafka](https://kafka.apache.org/) - Distributed event streaming
* [SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) - Real-time event-based communication to browser

