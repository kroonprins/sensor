import { IN_EMULATOR } from '../constants.js';

const DEVICE_HOST = IN_EMULATOR ? "http://10.0.2.2:8901/device" : "http://192.168.42.1:8080";

class DeviceServiceImpl {

  startPollingPing(onlineCallback, offlineCallback, interval = 5000) {
    this.pollingPingInterval = interval;
    if(!this.pollingPing) {
      let _poll = () => {
        console.info("Poll device");
        this.isAvailable().then((deviceId) => {
          if(deviceId) {
            onlineCallback(deviceId);
          } else {
            offlineCallback();
          }
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
    return fetch(DEVICE_HOST + "/ping").then((response) => {
      return response.text();
    });
  };
  numberOfAvailableMeasurements() {
    console.info(DEVICE_HOST)
    return fetch(DEVICE_HOST + "/measurements/count").then((response) => {
      return response.text();
    });
  };
  downloadMeasurements() {
    return fetch(DEVICE_HOST + "/measurements", {
      method: "POST",
      headers: {
        'Accept': 'application/text',
        'Content-Type': 'application/json'
      },
      body: "{}"
    }).then((response) => {
      console.info("in then "+JSON.stringify(response))
      if(response.ok) {
        console.info("Response download: "+JSON.stringify(response))
        return response.text();
      } else {
        console.info("throwing")
        throw new Error("Download measurements returned with response code "+response)
      }
    }).then((responseBody) => {
      console.info("Second then: "+responseBody)
      return this._parseDownloadedMeasurements(responseBody);
    }).catch((error) => {
      console.error("Error downloading measurements "+error);
    });
    /*let mockResult = "1#1494894419#28.312$1#1494894435#28.312$1#1494894451#28.312$";
    return new Promise.resolve(this._parseDownloadedMeasurements(mockResult));*/
  };

  _parseDownloadedMeasurements(asString) {
    let measurements = asString.split("$");
    let result = [];
    for(let measurement of measurements) {
      let splitted = measurement.split("#");
      if(splitted.length === 3) {
        result.push({
          type: splitted[0],
          time: splitted[1],
          value: splitted[2]
        });
      }
    }
    return result;
  };
};

export let DeviceService = new DeviceServiceImpl();