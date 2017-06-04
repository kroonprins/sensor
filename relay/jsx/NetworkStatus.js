import React from 'react';
import {
  View,
  Text
} from 'react-native';

export const NetworkStatus = (props) => {
  return (
    <View>
      <Text>Wifi is {props.wifiStatus ? "" : "not "}connected</Text>
      <Text>Network is {props.networkStatus ? "" : "not "}connected</Text>
    </View>
  );
}