These should reside in every server that we docker..
They will continually wait for files to appear in their /videos directory..

Load Balancer will keep track of clients rerouted upload..


Make sure to look at public/lib/common.js, we'll implement a way for a websocket to contact the load balancer
in order to retrieve the correct IP at port 9000 to upload to..

NGINX will offload videos after the video has been processed in its static directory..

Every Peer server of the load balancer must run facial processor.

Main Node.js -> Load Balancer -> Rerouted to Peer's BinaryJS server -> Peer Load Balancer (+1 on tasks) -> Peer Facial Processor will handle processing -> Peer Load Balancer (-1 on tasks, send health report) -> Load Balancer -> Sends a request to Main Node.js server with exposed link to video on Peer's NGINX server

We will also keep the database on the Main Node.js server, it would be too messy for Peer servers to contact a singular database, rather.. we just send a request to Main Node.js and the Main node.js will handle saving it into the database..
