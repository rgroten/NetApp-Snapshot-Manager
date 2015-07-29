#!/usr/bin/env python

'''
Created on Feb 23, 2015

@author: rgroten
'''
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, json
from flask.globals import g
from flask.json import jsonify
from werkzeug.utils import redirect

import LoginAuth
import NaFunctions
import RFCChecker


app = Flask(__name__)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(user)s %(env)s %(funcName)s : %(message)s")
handler = RotatingFileHandler("/home/rgroten/git/NetApp-Snapshot-Manager/snapmgr/snapmgr.log", maxBytes=10000000, backupCount=3)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.debug = NaFunctions.getConfigOption("Debug")

@app.route("/")
@LoginAuth.requires_auth
def index():
    return render_template('index.html')

@app.route('/snapmgr')
@app.route('/snapmgr/')
@LoginAuth.requires_auth
def snapmgr_index():
    return redirect('/#/snapmgr')


@app.route('/getenv')
@app.route('/api/get_envs.json')
@LoginAuth.requires_auth
def env_get():
    try:
        envs = NaFunctions.getEnvs()
#         jsonEnvs = json.dumps([env.__dict__ for env in envs])
        jsonData = jsonify(success=True, envs=[env.__dict__ for env in envs])
        app.logger.info('success', extra={'user':g.user, 'env':'n/a'})
    except Exception as e:
        app.logger.error('failure: ' + str(e), extra={'user':g.user, 'env':'n/a'})
        jsonData = jsonify(errorMsg = str(e))
        jsonData.status_code = 400
    finally:
        return jsonData
#         return Response(json.dumps([env.__dict__ for env in envs]), mimetype='application/json')


@app.route('/vols', methods=['POST'])
@LoginAuth.requires_auth
def volume_get():
    request_dict = json.loads(request.data)
    g.env = request_dict["env"]
    ret = NaFunctions.listVolumes()

    if ret.results_status() == "failed":
        app.logger.error('failure: ' + ret.results_reason(), extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(errorMsg = ret.results_reason())
        jsonData.status_code = 400
        
    else:
        app.logger.info('success', extra={'user':g.user, 'env':g.env})
        vollist = ret.child_get("attributes-list")
        if vollist:
            data = vollist.toEncodedString()
        else:
            data = None
        jsonData = jsonify(success=True, data = data)
    return jsonData


@app.route('/snaps', methods=['POST'])
@LoginAuth.requires_auth
def snapshot_get():
    request_dict = json.loads(request.data)
    g.env = request_dict["env"]
    ret = NaFunctions.listSnapshots(request_dict["volume"])

    if ret.results_status() == "failed":
        app.logger.error('failure: ' + ret.results_reason(), extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(errorMsg = ret.results_reason())
        jsonData.status_code = 400
    else:
        app.logger.info('success for ' + request_dict["volume"], extra={'user':g.user, 'env':g.env})
        snaplist = ret.child_get("snapshots")
        if snaplist:
            data = snaplist.toEncodedString()
        else:
            data = None
        jsonData = jsonify(success=True, data = data)
    return jsonData


@app.route('/snapcr', methods=['POST'])
@LoginAuth.requires_auth
def snapshot_create():
    request_dict = json.loads(request.data)
    g.env = request_dict["env"]
    volume = request_dict["volume"]
    newName = request_dict["newName"]

    ret = NaFunctions.createSnapshot(volume, newName)

    if (ret.results_status() == "failed"):
        app.logger.error('failure: ' + ret.results_reason(), extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(errorMsg = ret.results_reason())
        jsonData.status_code = 400
    else:
        app.logger.info('success', extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(success=True, data = ret.toEncodedString())

    return jsonData


@app.route('/snapdel', methods=['POST'])
@LoginAuth.requires_auth
def snapshot_delete():
    request_dict = json.loads(request.data)
    g.env = request_dict["env"]
    volume = request_dict["volume"]
    snapshot = request_dict["snapshot"]

    ret = NaFunctions.deleteSnapshot(volume, snapshot)
    if (ret.results_status() == "failed"):
        app.logger.error('failure for ' + volume + ':' + snapshot +
                         ' : ' + ret.results_reason(), extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(errorMsg = ret.results_reason())
        jsonData.status_code = 400
    else:
        app.logger.info('success for ' + volume +
                        ':' + snapshot, extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(success=True, data = ret.toEncodedString())

    return jsonData


@app.route('/snaprest', methods=['POST'])
@LoginAuth.requires_auth
def snapshot_restore():
    request_dict = json.loads(request.data)
    g.env = request_dict["env"]
    volume = request_dict["volume"]
    snapshot = request_dict["snapshot"]

    if NaFunctions.EnvObj(g.env).get_rfc_required() == "True":
        rfcNumber = request_dict["rfcNumber"]
        try:
            rfcRes = RFCChecker.RFCChecker(rfcNumber)
        except Exception as e:
            errorMsg = str(e)
            app.logger.error('failure for ' + volume + ':' + snapshot + ' : ' + errorMsg, extra={'user':g.user, 'env':g.env})
            jsonData = jsonify(errorMsg = errorMsg)
            jsonData.status_code = 400
            return jsonData
                

        if rfcRes.isRFCScheduled():
            app.logger.info('RFC #' + rfcNumber + ' is Scheduled, proceeding', extra={'user':g.user, 'env':g.env})
        else:
            errorMsg = 'RFC #' + rfcNumber + ' is not in scheduled state'
            app.logger.error('failure for ' + volume + ':' + snapshot + ' : ' + errorMsg, extra={'user':g.user, 'env':g.env})
            jsonData = jsonify(errorMsg = errorMsg)
            jsonData.status_code = 400
            return jsonData
    
    ret = NaFunctions.restoreSnapshot(volume, snapshot)
    if (ret.results_status() == "failed"):
        app.logger.error('failure for ' + volume + ':' + snapshot +
                         ' : ' + ret.results_reason(), extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(errorMsg = ret.results_reason())
        jsonData.status_code = 400
    else:
        app.logger.info('success for ' +
                        volume + ':' + snapshot, extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(success=True, data = ret.toEncodedString())

    return jsonData


@app.route('/snaprename', methods=['POST'])
@LoginAuth.requires_auth
def snapshot_rename():
    request_dict = json.loads(request.data)
    g.env = request_dict["env"]
    volume = request_dict["volume"]
    snapshot = request_dict["snapshot"]
    newName = request_dict["newName"]

    ret = NaFunctions.renameSnapshot(volume, snapshot, newName)
    if (ret.results_status() == "failed"):
        app.logger.error('failure for ' + volume + ':' + snapshot +
                         ' : ' + ret.results_reason(), extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(errorMsg = ret.results_reason())
        jsonData.status_code = 400
    else:
        app.logger.info('success for ' + volume + ':' + snapshot +
                        ' to ' + newName, extra={'user':g.user, 'env':g.env})
        jsonData = jsonify(success=True, data = ret.toEncodedString())

    return jsonData


# Only used when running with internal web server, won't get called in wsgi
if __name__ == '__main__':
    app.run(port=5001)