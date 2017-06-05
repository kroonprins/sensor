import React, { Component } from 'react';
import {
  AppRegistry,
  StyleSheet,
  Text,
  View,
  FlatList, ListItem,
  TouchableHighlight
} from 'react-native';
import { NetworkStatusService } from './services/NetworkStatusService.js';
import { DeviceService } from './services/DeviceService.js';
import { UploadServerService } from './services/UploadServerService.js';
import { DatabaseService } from './services/DatabaseService.js';

import { NetworkStatus } from './jsx/NetworkStatus.js';
import { ConnectedDevice } from './jsx/ConnectedDevice.js';
import { KnownDevice } from './jsx/KnownDevice.js';
import { UploadServer } from './jsx/UploadServer.js';

import { IN_EMULATOR, NETWORK_POLLING_INTERVAL, DEVICE_POLLING_INTERVAL, UPLOAD_SERVER_POLLING_INTERVAL } from './constants.js';

export default class RelayApp extends Component {
  state = {
    // Wifi is needed for device connection
    wifiConnected: false,
    // Wifi or mobile is needed for server connection
    networkConnected: false,
    // Contains all known devices
    // A device will contain following properties:
    //  * id: device id
    //  * availableMeasurements: number of measurements on the device that have not yet been downloaded from it
    //  * pendingMeasurements: number of measurements that have been downloaded but not yet uploaded to the server   
    knownDevices: [],
    // True if a connected device was found.
    deviceConnected: false,
    // if deviceConnected is true then this contains the index in the list knownDevices of the connected device.
    connectedDeviceIdx: -1,

    // Upload server found
    uploadServerAvailable: false
  };
  componentDidMount() {
    console.info("component did mount")
    this.initializeKnownDevices();
    this.initializeNetworkMonitoring();
  };
  initializeNetworkMonitoring = () => {
    console.info("start network monitoring")
    NetworkStatusService.monitor((status) => {
      console.info("Network status: "+JSON.stringify(status)+" vs existing: "+JSON.stringify(this.state))
      if(status.wifiConnected === this.state.wifiConnected && status.networkConnected === this.state.networkConnected) {
        console.info("no change in network state")
        return;
      }

      if(IN_EMULATOR) {
        // Network connection
        if(!this.state.networkConnected && status.networkConnected) {
          this.startDeviceMonitoring();
        } else {
          // Network disconnection
          if(this.state.networkConnected && !status.networkConnected) {
            this.stopDeviceMonitoring();
          }
        }
      } else {
          // WIFI connection
        if(!this.state.wifiConnected && status.wifiConnected) {
          console.info("wifi start devices monitoring")
          this.startDeviceMonitoring();
        } else {
          // WIFI disconnection
          if(this.state.wifiConnected && !status.wifiConnected) {
            this.stopDeviceMonitoring();
          }
        }      
      }

      // Network connection
      if(!this.state.networkConnected && status.networkConnected) {
        this.startServerMonitoring();
      } else {
        // Network disconnection
        if(this.state.networkConnected && !status.networkConnected) {
          this.stopServerMonitoring();
        }
      }

      this.setState(status);
    }, interval = NETWORK_POLLING_INTERVAL);
  };
  startDeviceMonitoring = () => {
    console.info("start device monitoring "+Date.now())
    DeviceService.startPollingPing((deviceId) => {
      console.info("connected "+Date.now())
      //if(!this.state.deviceConnected || deviceId !== this.state.knownDevices[this.state.connectedDeviceIdx].id) {
        DeviceService.numberOfAvailableMeasurements().then(count => {
          let updatedKnownDevices = [];
          let connectedDeviceIdx = -1;
          let deviceFound = false;
          this.state.knownDevices.forEach((knownDevice, idx) => {
            if(knownDevice.id === deviceId) {
              deviceFound = true;
              connectedDeviceIdx = idx;
              updatedKnownDevices.push(Object.assign({}, knownDevice, { availableMeasurements: count }));
            } else {
              updatedKnownDevices.push(knownDevice);
            }
          });
          if(!deviceFound) {
            connectedDeviceIdx = updatedKnownDevices.length;
            updatedKnownDevices.push({
              id: deviceId,
              pendingMeasurements: 0,
              availableMeasurements: count
            });
          }
          this.setState({
            knownDevices: updatedKnownDevices,
            deviceConnected: true,
            connectedDeviceIdx: connectedDeviceIdx
          });  
          DatabaseService.saveDevice(deviceId, updatedKnownDevices[connectedDeviceIdx].pendingMeasurements);        
        });
      //}
    }, () => {
      console.info("disconnected "+Date.now())
      this.resetDeviceConnected();
    }, DEVICE_POLLING_INTERVAL);
  };
  stopDeviceMonitoring = () => {
    console.info("stop device monitoring "+Date.now())
    DeviceService.stopPollingPing();
    this.resetDeviceConnected();
  };
  startServerMonitoring = () => {
    UploadServerService.startPollingPing(() => {
      console.info("Set server available "+Date.now())
      this.updateUploadServerAvailable(true);
    }, () => {
      console.info("Set server not available "+Date.now())
      this.updateUploadServerAvailable(false);
    }, UPLOAD_SERVER_POLLING_INTERVAL);
  };
  stopServerMonitoring = () => {
    UploadServerService.stopPollingPing();
    this.updateUploadServerAvailable(false);
  };
  updateUploadServerAvailable = (isAvailable) => {
    if(this.state.uploadServerAvailable === isAvailable) {
      return;
    }
    this.setState((prevState) => { 
      return {
        uploadServerAvailable: isAvailable,
        // Needed so that the list of known devices gets re-rendered...
        knownDevices: [...prevState.knownDevices]
      };
    });    
  }
  initializeKnownDevices = () => {
    DatabaseService.listDevices().then((devices) => {
      this.setState({
        knownDevices: devices
      });
    });
  };
  resetDeviceConnected = () => {
    if(this.state.deviceConnected) {
      this.setState((prevState) => {
        return {
          deviceConnected: false,
          connectedDeviceIdx: -1,
          knownDevices: [...prevState.knownDevices]
        }
      });  
    }
  };
  downloadMeasurements = () => {
    if(!this.state.deviceConnected) {
      console.error("Trying to download but no device connected");
      return;
    }

    DeviceService.downloadMeasurements().then((measurements) => {
      DatabaseService.saveMeasurements(this.state.knownDevices[this.state.connectedDeviceIdx].id, measurements).then((pendingMeasurements) => {
        let updatedKnownDevices = this.state.knownDevices.map((device, idx) => {
          if(idx === this.state.connectedDeviceIdx) {
            return Object.assign({}, device, { pendingMeasurements: pendingMeasurements, availableMeasurements: 0 });
          } else {
            return device;
          }
        });  
        this.setState((prevState) => {
          return {
            knownDevices: updatedKnownDevices
          };          
        });
      });
    });   
  };
  uploadMeasurements = (device) => {
    DatabaseService.retrieveMeasurements(device.id).then((measurements) => {
      UploadServerService.uploadMeasurements(device.id, measurements).then(_ => {
        DatabaseService.deleteMeasurements(device.id).then(() => {
          let updatedKnownDevices = this.state.knownDevices.map((knownDevice) => {
            if(knownDevice.id === device.id) {
              return Object.assign({}, knownDevice, { pendingMeasurements: 0 });
            } else {
              return knownDevice;
            }
          });  
          this.setState({ knownDevices: updatedKnownDevices });
        });
      });
    });    
  };
  renderKnownDevices = ({item}) => {
    if(!this.state.knownDevices[this.state.connectedDeviceIdx]
        || item.id !== this.state.knownDevices[this.state.connectedDeviceIdx].id) {
      return (
        <KnownDevice
          device={item}
          uploadPossible={this.state.uploadServerAvailable}
          uploadClickHandler={() => this.uploadMeasurements(item)}
        />
      );
    }
  };

  render() {
    return (
      <View style={styles.container}>
        <NetworkStatus
          wifiStatus={this.state.wifiConnected}
          networkStatus={this.state.networkConnected}
        />
        <UploadServer status={this.state.uploadServerAvailable} />
        <ConnectedDevice
          status={this.state.deviceConnected}
          device={this.state.knownDevices[this.state.connectedDeviceIdx]}
          downloadClickHandler={this.downloadMeasurements}
          uploadPossible={this.state.uploadServerAvailable}
          uploadClickHandler={() => this.uploadMeasurements(this.state.knownDevices[this.state.connectedDeviceIdx])}
        />
        <FlatList 
          keyExtractor={(device, index) => device.id}
          data={this.state.knownDevices}
          renderItem={this.renderKnownDevices}
        />
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5FCFF',
  },
  welcome: {
    fontSize: 20,
    textAlign: 'center',
    margin: 10,
  },
  instructions: {
    textAlign: 'center',
    color: '#333333',
    marginBottom: 5,
  },
});

AppRegistry.registerComponent('Relay', () => RelayApp);
