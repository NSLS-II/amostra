=====
Usage
=====

Connect to a MongoDB database.

.. ipython:: python

   import amostra.mongo_client
   URI = 'mongodb://localhost:27017/amostra_demo'
   client = amostra.mongo_client.Client(URI)

.. ipython:: python
   :suppress:

   # Drop the demo database to clean data from any previous builds.
   client._db.client.drop_database('amostra_demo')

Create a new Sample.

.. ipython:: python

   s = client.new_sample(name='peanut butter')
   s
   s.name

Update a trait of the sample.

.. ipython:: python

   s.name = 'jelly'
   s

And again.

.. ipython:: python

   s.name = 'grape jelly'
   s

All revisions are automatically persisted in the database and can be accessed.
The most recent revisions are given first.

.. ipython:: python

   list(s.revisions())

.. note::

   The Sample has two read-only traits that are used internally:

   .. ipython:: python

      s.uuid
      s.revision

   A Sample is automatically given a uuid when it is created. All revisions of
   that Sample share that same uuid, but the combination of uuid and revision
   number is globally unique. The revision is incremented on each update.

Create several more samples, and then search to find one.

.. ipython:: python

   client.new_sample(name='coffee')
   client.new_sample(name='tea')
   client.new_sample(name='water')
   results = client.find_samples({'name': 'tea'})
   results

The search results are given as a *generator*, a lazy object that pulls data on
demand, to avoid clobbering the system if the set of results is large. To pull
just one result we can use ``next``.

.. ipython:: python

   s = next(results)
   s
