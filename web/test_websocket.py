import sys
from twisted.python import log
from twisted.internet import reactor
log.startLogging(sys.stdout)
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory

socket_dictionary = {}
#Class for socket testing.
class MyServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		global socket_dictionary
		socket_dictionary[request.protocols[0]] = request
	def onClose(self, wasClean, code, reason):
		1
	def onMessage(self, payload, isBinary):
		#self.sendMessage(payload, isBinary)
		1
	def sendImageLink(self, token, link):
		global socket_dictionary
		client = socket_dictionary[token]
		if not client == None:
			reactor.callFromThread(self.sendMessage, client, link)
			
factory = WebSocketServerFactory()
factory.protocol = MyServerProtocol

reactor.listenTCP(6654, factory)
reactor.run()
