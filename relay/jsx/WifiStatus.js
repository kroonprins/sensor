import React from 'react';
import {
  Text
} from 'react-native';

export const WifiStatus = (props) => {
  return (
    <Text>Wifi is {props.status ? "" : "not "}connected</Text>
  );
}