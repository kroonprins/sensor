import store from 'react-native-simple-store';

//const DEVICE_HOST = "http://192.168.42.1:8080";
const DEVICE_HOST = "http://10.0.2.2:8901/device";

class DeviceServiceImpl {
  isAvailable() {
    /*return new Promise(function(resolve,reject){
      resolve("deviceId");
    });*/
    return fetch(DEVICE_HOST + "/ping").then((response) => {
      return response.text();
    });
  }
  numberOfAvailableMeasurements() {
    /*return new Promise(function(resolve,reject){
      resolve(100);
    });*/
    return fetch(DEVICE_HOST + "/count").then((response) => {
      return response.text();
    });
  }
  downloadMeasurements() {
    /*return fetch('http://10.0.2.2:8111').then((response) => {
      if(response.ok) {
        return response.text();
      } else {
        return "failed";
      }
    });*/
  }
  /*testSaveStorage() {
    store
      .save('key', 'yo');
  }
  testRetrieveStorage() {
    return store.get('key');
  }*/
}

export let DeviceService = new DeviceServiceImpl();