
Configuration Options for peng3dnet
===================================

These configuration options can be used to manipulate various features of peng3dnet.
The default values for these config options have been set to allow to not need any
config changes for most basic applications.

Config values can be changed by either passing a dictionary with overiddes as
the ``cfg`` argument to :py:class:`~peng3dnet.net.Client()` or
:py:class:`~peng3dnet.net.Server()`\ , or by accessing the ``cfg`` attribute of
an instance of the classes mentioned above.

Note that all config values added by peng3dnet have the ``net.`` prefix to
prevent confusion.

Default config values are mostly documented within the docs themselves or can be
found in :py:data:`peng3dnet.constants.DEFAULT_CONFIG`\ .

``net.server.*`` - Generic Server-side config options
-----------------------------------------------------

All non feature-specific server-side config options will use the ``net.server.*` prefix.

.. confval:: net.server.addr
             net.server.addr.host
             net.server.addr.port
   
   These config options specify the host and port the server will listen on.
   
   .. seealso::
      See :py:class:`peng3dnet.net.Server` for more information on how these
      config options work.
   
   :confval:`net.server.addr` defaults to ``None``\ , while :confval:`net.server.addr.host`
   and :confval:net.server.addr.port` default to ``0.0.0.0`` and ``8080``\ , respectively.

``net.client.*`` - Generic Client-side config options
-----------------------------------------------------

All non feature-specific client-side config options will use the ``net.client.*` prefix.

.. confval:: net.client.addr
             net.client.addr.host
             net.client.addr.port
   
   These config options specify the host and port the client will connect to.
   
   .. seealso::
      See :py:class:`peng3dnet.net.Client` for more information on how these
      config options work.
   
   :confval:`net.client.addr` defaults to ``None``\ , while :confval:`net.client.addr.host`
   and :confval:`net.client.addr.port` default to ``localhost`` and ``8080``\ , respectively.

``net.compress.*`` - Compression settings
-----------------------------------------

These config options apply to the per-packet compression. It is recommended that
client and server use the same config options for better compatibility, but it is
not strictly necessary.

.. confval:: net.compress.enabled
   
   Determines whether or not the compression module is activated.
   
   If this config options is ``False``\ , all outgoing packets will be uncompressed,
   but incoming compressed packets should still be processed appropriately assuming
   the required modules are available.
   
   This config option defaults to ``True``\ .

.. confval:: net.compress.threshold
   
   Determines the compression threshold in bytes.
   
   All packets with a size greater than this config option will be compressed.
   
   Defaults to ``8192``\ , or 8 Kib.

.. confval:: net.compress.level
   
   The :py:mod:`zlib` compression level to use when compressing packets.
   
   .. seealso::
      Please see :py:func:`zlib.compress()` for more information about compression levels.
   
   This config option defaults to ``6``

``net.encrypt.*`` - Encryption settings
---------------------------------------

This module is currently not implemented.

.. confval:: net.encrypt.enabled
   
   Determines whether or not the encryption module is activated.
   
   This module is currently not implemented, changing this option should still not be done.
   
   Defaults to ``False``\ .

``net.ssl.*`` - SSL settings
----------------------------

These config options affect the SSL configuration used by both server and client.

Note that currently the SSL module is very buggy and thus disabled by default.
It should not be used for any serious applications.

The default config values are configured for maximum security, this means that
servers must always have certificates that will be verified.

.. confval:: net.ssl.enabled
   
   Determines whether or not the SSL module is activated.
   
   It is necessary that both sides have SSL enabled, or the connection will fail
   with an undefined error.
   
   This config option defaults to ``False``\ .

.. confval:: net.ssl.force
   
   Used to configure if loading the :py:mod:`ssl` module is required.
   
   If ``True``\ , an error will be raised if the ssl module is not available.
   If ``False`` and the ssl module is not available, it will simply not be loaded.
   
   This config option defaults to ``True``\ .

.. confval:: net.ssl.cafile
             net.ssl.server.force_verify
             net.ssl.server.certfile
             net.ssl.server.keyfile
             net.ssl.client.check_hostname
             net.ssl.client.force_verify
   
   These options mostly do what they are named after, further documentation is currently
   not provided due to frequent design changes regarding them.
   
   For default values see :py:data:`peng3dnet.constants.DEFAULT_CONFIG`\ .

``net.events.*`` - Event settings
---------------------------------

.. confval:: net.events.enable
   
   Determines whether or not events will be sent.
   
   If ``auto`` is used, events will be sent only if a ``peng`` instance has been passed
   to the client or server.
   
   Defaults to ``auto``\ .

``net.debug.*`` - Internal Debug Flags
--------------------------------------

.. confval:: net.debug.print.recv
             net.debug.print.send
             net.debug.print.connect
             net.debug.print.close
   
   Flags that determine whether or not the specific status messsages will be printed out.
   
   These flags are temporary until a proper logging system has been established.
   
   All of these options default to ``False``\ .

``net.registry.*`` - Registry Configuration
-------------------------------------------

.. confval:: net.registry.autosync
   
   Determines whether or not the registry will be automatically synced between
   server and client.
   
   See :py:class:`~peng3dnet.packet.internal.HandshakePacket()` for more information about
   the auto-sync.
   
   This config option defaults to ``True``\ .

.. confval:: net.registry.missingpacketaction
   
   Configures what action is taken if during registry synchronization the client
   and server do not have the same packets.
   
   Currently possible values are ``closeconnection`` which closes the connection
   and ``ignore`` which simply ignores the mismatch but may cause issues later.
   
   This config option defaults to ``closeconnection``\ .
