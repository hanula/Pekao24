Pekao24 API
===========

Simple API to get accounts info from Pekao Bank SA (http://www.pekao.com.pl/)


Installation
------------
    $ pip install pekao24

Or using source:

    $ pip install https://github.com/hanula/Pekao24/tarball/master

Using simple client
-------------------

from command line::

    $ pekao24 [clientID]
    Client ID:
    ...
    Password:
    ...

    Account details: XXXXXXXXXXXX YYYYYYYY: ZZZZ PLN
    Transaction # XXX: ...
    ...


Using the API
-------------

::

    from pekao24 import Pekao24
    import getpass
    client_id = raw_input('Client ID: ')
    password = getpass.getpass('Password: ')
    client = Pekao24(client_id, password)

    accounts = client.get_accounts()

    for account in accounts:
        print "Account details: %(id)s %(name)s: %(amount)s %(currency)s" % account

        transactions = client.get_transaction_history(account['id'])
        for transaction in transactions:
            print "Transaction #%(id)5s: %(date)s, %(amount)12s %(currency)s: %(title)s" % transaction
            print




