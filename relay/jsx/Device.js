import React from 'react';
import {
  Text
} from 'react-native';

export const Device = (props) => {
  if(props.status) {
    return (
      <Text>Device is connected: {props.device.id}</Text>
    );
  } else {
    return (
      <Text>Device is not connected.</Text>
    );
  }
}