
Events used by peng3dnet
========================

The event system of :py:mod:`peng3d` is used by peng3dnet to allow peng3d apps
to easily integrate with peng3dnet.

.. seealso::
   See the :py:mod:`peng3d` docs about the `Peng3d Event System <http://peng3d.readthedocs.io/en/latest/events.html#peng3d-events-using-sendevent>`_
   for more information about the peng3d event system.

Server-Side Events
------------------

These events are sent exclusively by the :py:class:`~peng3dnet.net.Server()` class.

Unless otherwise noted, they always contain the ``peng`` and ``server`` keys in their data dictionary.

``peng`` will be an instance of :py:class:`peng3d.peng.Peng()` or ``None``\ , as supplied to the constructor.

``server`` will be the instance of :py:class:`~peng3dnet.net.Server()` that sent the event.

.. peng3d:event:: peng3dnet:server.initialize
   
   Sent once the server has been initialized via :py:meth:`peng3dnet.net.Server.initialize()`\ .
   
   This event has no additional data attached to it.

.. peng3d:event:: peng3dnet:server.bind
   
   Sent once the server-side socket has been bound to a specific address via :py:meth:`peng3dnet.net.Server.bind()`\ .
   
   This event has the additional data key ``addr`` set to a 2-tuple of format ``(host,port)``\ .

.. peng3d:event:: peng3dnet:server.start
   
   Sent when the server main loop is about to start.
   
   This event has no additional data attached to it.

.. peng3d:event:: peng3dnet:server.stop
   
   Sent whenever the :py:meth:`peng3dnet.net.Server.stop()` method is called.
   
   The data key ``reason`` will be set to ``method`` to indicate that the stop
   has been caused by calling the stop method. In the future, other reasons may
   be introduced.

.. peng3d:event:: peng3dnet:server.interrupt
   
   Sent whenever an interrupt has been sent via :py:meth:`peng3dnet.net.Server.interrupt()`\ .
   
   Note that the processing of the interrupt may be delayed due to various factors.
   
   This event has no additional data attached to it.

.. peng3d:event:: peng3dnet:server.shutdown
   
   Sent once the server has been shutdown by calling the :py:meth:`peng3dnet.net.Server.shutdown()` method.
   
   All arguments passed to :py:meth:`peng3dnet.net.Server.shutdown()` will be present in the data attached to this event.

Connection-specific Events
^^^^^^^^^^^^^^^^^^^^^^^^^^

These events are specific to a connection and will often be triggered very
frequently. This makes it important that event handlers subscribing to events in
this subsection are high-performant, as they may significantly impact overall
performance.

.. peng3d:event:: peng3dnet:server.connection.accept
   
   Sent whenever a new connection is established.
   
   Note that the connection may not be able to transmit data, see
   :peng3d:event:`peng3dnet:server.connection.handshakecomplete` for more information.
   
   This event has the following data attached to it:
   
   ``sock`` is the actual TCP socket of the connection.
   
   ``addr`` is the remote address that has connected to the server.
   
   ``client`` is an instance of :py:class:`~peng3dnet.net.ClientOnServer()` used to represent the client.
   
   ``cid`` is the numerical ID of the client.

.. peng3d:event:: peng3dnet:server.connection.handshakecomplete
   
   Sent whenever a handshake with a client has been completed.
   
   Usually, this means that the client in question is now able to both send and receive packets.
   
   The data key ``client`` will be set to the instance of :py:class:`~peng3dnet.net.ClientOnServer()` that represents the client.

.. peng3d:event:: peng3dnet:server.connection.send
   
   Sent whenever a packet has been sent over a connection.
   
   Note that this event is only triggered if the connection type allows it.
   
   Additional data:
   
   ``client`` is the instance of :py:class:`~peng3dnet.net.ClientOnServer()` representing the target client.
   
   ``pid`` is the packet type, as given to :py:meth:`peng3dnet.net.Server.send_message()`\ .
   
   ``data`` is the encoded packet, including header and length-prefix.

.. peng3d:event:: peng3dnet:server.connection.recv
   
   Sent whenever a packet has been received from a connection.
   
   Note that this event is only triggered if the connection type allows it.
   
   Additional data:
   
   ``client`` is the instance of :py:class:`~peng3dnet.net.ClientOnServer()` representing the sender of the packet.
   
   ``pid`` is the packet type, as an integer.
   
   ``msg`` is the fully decoded message. Usually, this will be a dictionary, but other types are possible.

.. peng3d:event:: peng3dnet:server.connection.close
   
   Sent whenever a connection has been closed.
   
   This event should only be sent once per connection, though this is not guaranteed.
   
   After this event has been sent, the connection will be cleant up, meaning it is no longer available to send or receive.
   
   Additional data:
   
   ``client`` is the instance of :py:class:`~peng3dnet.net.ClientOnServer()` representing the connection to be closed.
   
   ``reason`` is a string or ``None`` representing the reason this connection has been closed.
   Note that these reasons are not standardized and may change at any point in time.

Client-Side Events
------------------

These events are sent exclusively by the :py:class:`~peng3dnet.net.Client()` class.

Unless otherwise noted, they always contain the ``peng`` and ``client`` keys in their data dictionary.

``peng`` will be an instance of :py:class:`peng3d.peng.Peng()` or ``None``\ , as supplied to the constructor.

``client`` will be the instance of :py:class:`~peng3dnet.net.Client()` that sent the event.

.. peng3d:event:: peng3dnet:client.initialize
   
   Sent once the client has been initialized by calling :py:meth:`peng3dnet.net.Client.initialize()`\ .
   
   Will be sent exactly once per client.
   
   This event has no additional data attached to it.

.. peng3d:event:: peng3dnet:client.connect
   
   Sent once the client has been connected to a server via :py:meth:`peng3dnet.net.Client.connect()`\ .
   
   Note that this event only signals that the underlying connection has been established, the SSL tunnel and Handshake may not yet be working.
   
   Will be sent exactly once per client.
   
   Additional data:
   
   ``addr`` will be the address of the server in the format ``(host,port)``
   
   ``sock`` will be the socket itself used to communicate with the server.

.. peng3d:event:: peng3dnet:client.start
   
   Sent once the client has been started via :py:meth:`peng3dnet.net.Client.runBlocking()`\ .
   
   Note that this event will be sent once per instance of :py:class:`~peng3dnet.net.Client()`.
   
   This event has no additional data attached to it.

.. peng3d:event:: peng3dnet:client.stop
   
   Sent whenever the :py:meth:`peng3dnet.net.Client.stop()` method is called.
   
   The data key ``reason`` will be set to ``method`` to indicate that the stop
   has been caused by calling the stop method. In the future, other reasons may
   be introduced.

.. peng3d:event:: peng3dnet:client.interrupt
   
   Sent whenever an interrupt has been issued by :py:meth:`peng3dnet.net.Client.interrupt()`\ .
   
   Note that the actual processing of the interrupt may be delayed by an arbitrary time.

.. peng3d:event:: peng3dnet:client.handshakecomplete
   
   Sent once the handshake has been completed.
   
   Note that some connection types may not trigger this event.
   
   This event has no additional data attached to it.

.. peng3d:event:: peng3dnet:client.recv
   
   Sent whenever a packet has been received from the server.
   
   Note that this event is only triggered if the connection type allows it.
   
   Additional data:
   
   ``pid`` is the packet type, as an integer.
   
   ``msg`` is the fully decoded message. Usually, this will be a dictionary, but other types are possible.

.. peng3d:event:: peng3dnet:client.send
   
   Sent whenever a packet is about to be sent to the server.
   
   Note that this event is only triggered if the connection type allows it.
   
   Additional data:
   
   ``pid`` is the packet type, as given to :py:meth:`peng3dnet.net.Client.send_message()`\ .
   
   ``data`` is the raw packet data before encoding.

.. peng3d:event:: peng3dnet:client.close
   
   Sent once the connection to the server has been closed.
   
   This event will usually be sent only once per client.
   
   The ``reason`` data key will be set to the reason as either a string or ``None``\ .
