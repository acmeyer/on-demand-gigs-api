#!/usr/bin/env python3
"""API for on-demand gigs."""

from uuid import uuid1
import time

import boto3
import simplejson

from flask import Flask
from flask import abort, request

# from two1.wallet import Wallet
# from two1.bitserv.flask import Payment

# Configure the app, wallet, and database
app = Flask(__name__)
# wallet = Wallet()
# payment = Payment(app, wallet)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Gigs-dev')


# Charge a fixed fee of 100 satoshis per request to get a list of gigs
@app.route('/on-demand-gigs')
# @payment.required(100)
def list():
    """Return a list of available gigs."""
    response = table.scan()
    if response['Items']:
        return simplejson.dumps(response['Items']), {'Content-Type': 'application/json'}
    else:
        return abort(422)


# Charge a fixed fee of 1000 satoshis per request to create a new gig
@app.route('/on-demand-gigs/new', methods=['POST'])
# @payment.required(1000)
def create():
    """Create a new gig."""
    timestamp = int(time.time())
    gig_id = str(uuid1())

    jsonData = request.get_json(force=True)

    companyName = jsonData['companyName'] if 'companyName' in jsonData else abort(422)
    companyLogo = jsonData['companyLogo'] if 'companyLogo' in jsonData else abort(422)
    jobType = jsonData['jobType'] if 'jobType' in jsonData else abort(422)
    applicationUrl = jsonData['applicationUrl'] if 'applicationUrl' in jsonData else abort(422)
    requirements = jsonData['requirements'] if 'requirements' in jsonData else []
    description = jsonData['description'] if 'description' in jsonData else ''
    roles = jsonData['roles'] if 'roles' in jsonData else []
    locations = jsonData['locations'] if 'locations' in jsonData else []

    response = table.put_item(
        Item={
            'id': gig_id,
            'companyName': companyName,
            'companyLogo': companyLogo,
            'requirements': requirements,
            'jobType': jobType,
            'description': description,
            'roles': roles,
            'locations': locations,
            'applicationUrl': applicationUrl,
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        resp = table.get_item(
            Key={
                'id': gig_id
            }
        )
        if 'Item' in resp:
            return simplejson.dumps(resp['Item']), {'Content-Type': 'application/json'}
        else:
            return abort(404)
    else:
        return abort(response['ResponseMetadata']['HTTPStatusCode'])


# Charge a fixed fee of 100 satoshis per request to get a gig
@app.route('/on-demand-gigs/<gig_id>')
# @payment.required(100)
def get(gig_id):
    """Return a gig."""
    response = table.get_item(
        Key={
            'id': gig_id
        }
    )
    if 'Item' in response:
        return simplejson.dumps(response['Item']), {'Content-Type': 'application/json'}
    else:
        return abort(404)


# Charge a fixed fee of 500 satoshis per request to update a gig
@app.route('/on-demand-gigs/<gig_id>/update', methods=['PUT'])
# @payment.required(100)
def update(gig_id):
    """Update a gig."""
    timestamp = int(time.time())
    jsonData = request.get_json(force=True)

    expressionAttributeNames = {}
    updateExpression = 'SET updatedAt = :updatedAt'
    expressionAttributeValues = {
        ':updatedAt': timestamp
    }

    if 'companyName' in jsonData:
        expressionAttributeValues[':companyName'] = jsonData['companyName']
        updateExpression += ', companyName = :companyName'

    if 'companyLogo' in jsonData:
        expressionAttributeValues[':companyLogo'] = jsonData['companyLogo']
        updateExpression += ', companyLogo = :companyLogo'

    if 'jobType' in jsonData:
        expressionAttributeValues[':jobType'] = jsonData['jobType']
        updateExpression += ', jobType = :jobType'

    if 'applicationUrl' in jsonData:
        expressionAttributeValues[':applicationUrl'] = jsonData['applicationUrl']
        updateExpression += ', applicationUrl = :applicationUrl'

    if 'requirements' in jsonData:
        expressionAttributeValues[':requirements'] = jsonData['requirements']
        updateExpression += ', requirements = :requirements'

    if 'description' in jsonData:
        expressionAttributeValues[':description'] = jsonData['description']
        updateExpression += ', description = :description'

    if 'roles' in jsonData:
        expressionAttributeValues[':roles'] = jsonData['roles']
        expressionAttributeNames['#gig_roles'] = 'roles'
        updateExpression += ', #gig_roles = :roles'

    if 'locations' in jsonData:
        expressionAttributeValues[':locations'] = jsonData['locations']
        updateExpression += ', locations = :locations'

    if 'roles' in jsonData:
        response = table.update_item(
            Key={
                'id': gig_id
            },
            ExpressionAttributeNames=expressionAttributeNames,
            UpdateExpression=updateExpression,
            ExpressionAttributeValues=expressionAttributeValues,
            ReturnValues='ALL_NEW'
        )
    else:
        response = table.update_item(
            Key={
                'id': gig_id
            },
            UpdateExpression=updateExpression,
            ExpressionAttributeValues=expressionAttributeValues,
            ReturnValues='ALL_NEW'
        )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        resp = table.get_item(
            Key={
                'id': gig_id
            }
        )
        if 'Item' in resp:
            return simplejson.dumps(resp['Item']), {'Content-Type': 'application/json'}
        else:
            return abort(404)
    else:
        return abort(response['ResponseMetadata']['HTTPStatusCode'])


# Charge a fixed fee of 10000 satoshis per request to delete a gig
@app.route('/on-demand-gigs/<gig_id>/delete', methods=['DELETE'])
# @payment.required(10000)
def delete(gig_id):
    """Delete a gig."""
    response = table.delete_item(
        Key={
            'id': gig_id
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return simplejson.dumps({}), 200, {'Content-Type': 'application/json'}
    else:
        return abort(response['ResponseMetadata']['HTTPStatusCode'])


# Initialize and run the server
if __name__ == '__main__':
    app.run()
