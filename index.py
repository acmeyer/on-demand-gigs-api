#!/usr/bin/env python3
"""API for on-demand gigs."""

from uuid import uuid1
import time

import boto3

from flask import Flask
from flask import jsonify, request, abort

# from two1.wallet import Wallet
# from two1.bitserv.flask import Payment

# Configure the app, wallet, and database
app = Flask(__name__)
# wallet = Wallet()
# payment = Payment(app, wallet)
client = boto3.client('dynamodb')


# Charge a fixed fee of 100 satoshis per request to get a list of gigs
@app.route('/on-demand-gigs')
# @payment.required(100)
def list():
    """Return a list of available gigs."""
    response = client.scan(
        TableName='Gigs-dev'
    )
    return jsonify(response['Items'])


# Charge a fixed fee of 1000 satoshis per request to create a new gig
@app.route('/on-demand-gigs/new', methods=['POST'])
# @payment.required(1000)
def create():
    """Create a new gig."""
    timestamp = int(time.time())

    json = request.get_json(force=True)

    companyName = json['companyName'] if 'companyName' in json else abort(422)
    companyLogo = json['companyLogo'] if 'companyLogo' in json else abort(422)
    jobType = json['jobType'] if 'jobType' in json else abort(422)
    applicationUrl = json['applicationUrl'] if 'applicationUrl' in json else abort(422)
    requirements = json['requirements'] if 'requirements' in json else []
    description = json['description'] if 'description' in json else ''
    roles = json['roles'] if 'roles' in json else []
    locations = json['locations'] if 'locations' in json else []

    response = client.put_item(
        TableName='Gigs-dev',
        Item={
            'id': uuid1,
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
    return jsonify(response['Item'])


# Charge a fixed fee of 100 satoshis per request to get a gig
@app.route('/on-demand-gigs/<int:gig_id>')
# @payment.required(100)
def get(gig_id):
    """Return a gig."""
    return 'Gig %d' % gig_id


# Charge a fixed fee of 500 satoshis per request to update a gig
@app.route('/on-demand-gigs/<int:gig_id>/update', methods=['PUT'])
# @payment.required(100)
def update(gig_id):
    """Update a gig."""
    return 'Update gig %d' % gig_id


# Charge a fixed fee of 10000 satoshis per request to delete a gig
@app.route('/on-demand-gigs/<int:gig_id>/delete', methods=['DELETE'])
# @payment.required(10000)
def delete(gig_id):
    """Delete a gig."""
    return 'Delete gig %d' % gig_id


# Initialize and run the server
if __name__ == '__main__':
    app.run()
