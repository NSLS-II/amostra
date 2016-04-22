Introduction
===========

Overview
--------

amostra is a sample management service for scientific experiments. It is implemented as a web service with a RESTful api. Amostra is not a data acquisition tool that controls robots etc. It keeps track of an experiment/run's samples, sample groups(containers), and requests that act on these samples. The full amostra collection suit is available but optional for every beamline or application. Flexible No-SQL nature allows storing semi structured sample information (which I have proven works in every beamline so far). Amostra can be coupled with 3rd party applications such as sample management hardware(e.g. robots), PASS system, or csv import/export utility libraries.

The service comes with both an online api that communicates with the amostra service server and a local api that is capable of performing similar tasks offline(locally). The goal of this approach is to provide users with the ability to perform sample management tasks similar to their beamline environment when they have no access to amostra server.
The flexible No-SQL nature allows storing semi structured sample information. What is meant by semi-structured?

Sample, Container, and Request documents all expect certain required fields such as time, uid, name, etc. and user can define any additional fields that the values of these fields can be string, array, document, or array of documents. I hide some of the complexity of semi-structured documents from the end user on the server by defaulting the required values to their appropriate values. If preferred, the user can define these parameters himself/herself. This is intended for those those that have existing tools -which use some other convention- or would like to build their own convention by populating these with values that make more sense for their experiment.

Relationships among collections are made available for any application to utilize and all relationships are completely optional. For instance, a beamline that is interested in this service for solely keeping track of their samples and have only one container, can use the **SampleReference** client, leaving **container** field empty. On the other hand, if an experiment has various containers, samples, and requests that are meaningful to some external source (either daq or analysis), one can use all three collections, using the relationships defined by this service. I talk about how these relationships can be utilized in the Schema section below. In addition to this, you could take a quick look at tutorial section for code examples.


Schema
------

Sample
******

.. code-block:: javascript

    {
    "properties": {
        "project": {
            "type": "string",
            "description": "Name of project that this sample is part of"
        },
        "beamline_id": {
            "type": "string",
            "description": "The beamline ID"
        },
        "time": {
            "type": "number",
            "description": "Time the sample was created.  Unix epoch time"
        },
        "uid": {
            "type": "string",
            "description": "Globally unique ID for tihs run"
        },
        "owner": {
            "type": "string",
            "description": "String identifier that denotes the owner of this sample. Process/project/user"
        },
        "name": {
            "type": "string",
            "description": "Sample name!"
        },
        "container": {
            "type": "string",
            "description": "Name of the container/group sample is contained within.Can be virtual or real. Sparsely indexed, not required"
        }
    },
    "required": [
        "uid",
        "time",
        "name"
     ],
    "type": "object",
    "description": "Document created for a single sample"
    }

Container
******

.. code-block:: javascript

    {
    "properties": {
        "uid": {
            "type": "string",
            "description": "Globally unique ID for this container"
        },
        "owner": {
            "type": "string",
            "description": "String descriptor to associate this request with. Can be user or process"
        },
        "time": {
            "type": "number",
            "description": "Time the container was created.  Unix epoch time"
        },
        "kind": {
            "type": "string",
            "description": "Type of the container"
        },
        "name": {
            "type": "string",
            "description": "Container name"
        },
        "content": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "The items of this container"
        }
    },
    "required": [
        "uid",
        "time"
     ],
    "type": "object",
    "description": "Document created for group of containers."
    }


Request
******
.. code-block:: javascript

    {
    "properties": {
        "project": {
            "type": "string",
            "description": "Name of project that this request is part of"
        },
        "beamline_id": {
            "type": "string",
            "description": "The beamline ID"
        },
        "time": {
            "type": "number",
            "description": "Time request created.  Unix epoch time"
        },
        "uid": {
            "type": "string",
            "description": "Globally unique ID for this request"
        },
        "owner": {
            "type": "string",
            "description": "String descriptor to associate this request with. Can be user or process"
        },
        "sample": {
            "type": "string",
            "description": "sample uid. samples are unaware of requests but requests know about samples"
        }
    },
    "required": [
        "uid",
        "time",
        "sample"
     ],
    "type": "object",
    "description": "Document created for a single request."
    }
