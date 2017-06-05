import { IN_EMULATOR } from '../constants.js';

const SERVER_HOST = IN_EMULATOR ? "http://10.0.2.2:8901/server/sensor" : "http://172.18.0.5:8080/sensor";

class UploadServerServiceImpl {

  startPollingPing(onlineCallback, offlineCallback, interval = 5000) {
    this.pollingPingInterval = interval;
    if(!this.pollingPing) {
      let _poll = () => {
        console.info("Poll server");
        this.isAvailable().then(() => {
          onlineCallback();
        }).catch((error) => {
          console.info("Error polling device "+error);
          offlineCallback();
        })
      };      
      _poll();
      // keep on polling (rock & poll will never die...)
      this.pollingPing = setInterval(_poll, this.pollingPingInterval);
    }

  };
  stopPollingPing() {
    if(this.pollingPing) {
      clearInterval(this.pollingPing);
      this.pollingPing = null;
    };
  };

  isAvailable() {
    // TODO fix caching headers on the server itself
    return fetch(SERVER_HOST + "/ping", {cache: "no-store"}).then((response) => {
      if(response.ok) {
        return response.text();
      } else {
        throw new Error("Ping response not ok");
      }
    }).catch((error) => {
      console.info("Error trying to connect server ping "+JSON.stringify(error))
      throw error;
    });
  };

  uploadMeasurements(deviceId, measurements) {
    return fetch(SERVER_HOST + "/measurement", {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: this._createBodyForMeasurementsUpload(deviceId, measurements)
    }).then((response) => {
      console.info("in then "+JSON.stringify(response))
      if(response.ok) {
        console.info("Response download: "+JSON.stringify(response))
        return response.text();
      } else {
        console.info("throwing")
        throw new Error("Download measurements returned with response code "+response)
      }
    }).catch((error) => {
      console.error("Error uploading measurements "+error);
    });
  };

  _createBodyForMeasurementsUpload(deviceId, measurements) {
    if(!measurements || !measurements.length > 0) {
      console.info("No measurements to upload");
      return;
    }
    let result = {
      deviceId: deviceId,
      measurements: this._transformMeasurements(measurements)
    }
    console.info("Body "+JSON.stringify(result))
    return JSON.stringify([result]);
  };

  _transformMeasurements(measurements) {
    let result = [];
    for(let measurement of measurements) {
      // TODO measurement.type gebruiken
      result.push({
        type: "TEMPERATURE",
        value: measurement.value,
        timing: new Date(measurement.time * 1e3).toISOString()
      })
    }
    return result;
  }
};

export let UploadServerService = new UploadServerServiceImpl();