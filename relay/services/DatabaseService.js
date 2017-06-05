import store from 'react-native-simple-store';

const DEVICES_TABLE = "devices";
const MEASUREMENTS_TABLE = "measurements";

class DatabaseServiceImpl {
  _stringifyDevices(devices) {
    if(!devices) {
      return;
    }
    let res = "";
    for(let device of devices) {
      res = res + JSON.stringify(device);
    }
    return res;
  }
  listDevices() {
    if(!this.devices) {
      return store.get(DEVICES_TABLE).then((devices) => {
        if(devices !== null) {
          this.devices = devices;
        } else {
          this.devices = [];
        }
        return this.devices;
      });
    } else {
      return new Promise.resolve(this.devices);
    }
  };
  saveDevice(deviceId, pendingMeasurements = 0) {
    return this.listDevices().then((devices) => {
      let device = devices.find(device => {
        return device.id === deviceId;
      });
      if(!device) {
        devices.push({ id: deviceId, pendingMeasurements: pendingMeasurements });
        this._saveDevices(devices);
      } else {
        if(device.pendingMeasurements !== pendingMeasurements) {
          device.pendingMeasurements = pendingMeasurements;
          this._saveDevices(devices);
        }
      }
    }).catch((error) => {
      console.warning("ERROR (1) "+error);
    });
  };
  _saveDevices(devices) {
    store.save(DEVICES_TABLE, devices);
    this.devices = devices;
  };
  saveMeasurements(deviceId, newMeasurements) {
    return this.retrieveMeasurements(deviceId).then(measurements => {
      let updatedMeasurements = [...measurements, ...newMeasurements];
      let pendingMeasurements = updatedMeasurements.length;
      store.save(this._getMeasurementTable(deviceId), updatedMeasurements);
      this.saveDevice(deviceId, pendingMeasurements = pendingMeasurements);
      return pendingMeasurements;
    }).catch((error) => {
      console.warning("ERROR (2) "+error);
    });
  };
  retrieveMeasurements(deviceId) {
    return store.get(this._getMeasurementTable(deviceId)).then(measurements => {
      if(measurements === null) {
        return [];
      }

      return measurements;
    }).catch((error) => {
      console.warning("ERROR (3) "+error);
    });
  };
  deleteMeasurements(deviceId) {
    return store.delete(this._getMeasurementTable(deviceId)).then(() => {
      return this.saveDevice(deviceId, pendingMeasurements = 0);
    });
  }
  _getMeasurementTable(deviceId) {
    return MEASUREMENTS_TABLE+"_"+deviceId;
  }
};

export let DatabaseService = new DatabaseServiceImpl();