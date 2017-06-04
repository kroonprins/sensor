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
import { DatabaseService } from './services/DatabaseService.js';

import { NetworkStatus } from './jsx/NetworkStatus.js';
import { ConnectedDevice } from './jsx/ConnectedDevice.js';
import { KnownDevice } from './jsx/KnownDevice.js';

import { IN_EMULATOR, NETWORK_POLLING_INTERVAL, DEVICE_POLLING_INTERVAL } from './constants.js';

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
    connectedDeviceIdx: -1
  };
  componentDidMount() {
    console.info("component did mount")
    this.initializeKnownDevices();
    this.initializeNetworkMonitoring();
  };
  initializeNetworkMonitoring = () => {
    console.info("start network monitoring")
    NetworkStatusService.monitor((status) => {
      console.info("Network status: "+JSON.stringify(status))
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
      this.setState(status);
    }, interval = NETWORK_POLLING_INTERVAL);
  };
  startDeviceMonitoring = () => {
    console.info("start device monitoring "+Date.now())
    DeviceService.startPollingPing((deviceId) => {
      console.info("connected "+Date.now())
      if(!this.state.deviceConnected || deviceId !== this.state.knownDevices[this.state.connectedDeviceIdx].id) {
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
      }
    }, () => {
      console.info("disconnected "+Date.now())
      this.resetDeviceConnected();
    }, DEVICE_POLLING_INTERVAL);
  }
  stopDeviceMonitoring = () => {
    console.info("stop device monitoring "+Date.now())
    DeviceService.stopPollingPing();
    this.resetDeviceConnected();
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
            return Object.assign({}, device, { pendingMeasurements: pendingMeasurements });
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
    console.warn("Uploading measurements but nothing implemented yet "+device.id);
  };
  renderKnownDevices = ({item}) => {
    if(!this.state.knownDevices[this.state.connectedDeviceIdx]
        || item.id !== this.state.knownDevices[this.state.connectedDeviceIdx].id) {
      return (
        <KnownDevice
          device={item}
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
        <ConnectedDevice
          status={this.state.deviceConnected}
          device={this.state.knownDevices[this.state.connectedDeviceIdx]}
          downloadClickHandler={this.downloadMeasurements}
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
