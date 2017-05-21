import React, { Component } from 'react';
import {
  AppRegistry,
  StyleSheet,
  Text,
  View,
  TouchableHighlight
} from 'react-native';
import { WifiStatusService } from './services/WifiStatusService.js';
import { DeviceService } from './services/DeviceService.js';

import { WifiStatus } from './jsx/WifiStatus.js';
import { Device } from './jsx/Device.js';

export default class RelayApp extends Component {
  state = {
    wifiConnected: true,
    deviceConnected: false,
    connectedDevice: {}
  };
  _onPressButton = () => {
    WifiStatusService.isConnected().then(isConnected => {
      this.setState((prevState) => ({
        wifiConnected: isConnected
      }));
    });
    DeviceService.isAvailable().then(deviceId => {
      if (deviceId !== '') {
        this.setState((prevState) => ({
          deviceConnected: true,
          connectedDevice: {
            id: deviceId
          }
        }));
        DeviceService.numberOfAvailableMeasurements().then(count => {
          this.setState((prevState) => {
            let updatedState = Object.assign({}, prevState);
            updatedState.connectedDevice.count = count;
            return updatedState;
          });
        });
      }
    });
  };
  render() {
    return (
      <View style={styles.container}>
        <WifiStatus status={this.state.wifiConnected} />
        <Device status={this.state.deviceConnected} device={this.state.connectedDevice} />
        <TouchableHighlight onPress={this._onPressButton}>
          <Text>Button</Text>
        </TouchableHighlight>
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
