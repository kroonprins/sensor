import React from 'react';
import {
  View,
  Text,
  TouchableHighlight
} from 'react-native';

export const ConnectedDevice = (props) => {
  if(props.status) {
    return (
      <View>
        <Text>Device is connected: {props.device.id} ({props.device.pendingMeasurements} / {props.device.availableMeasurements})</Text>
        {props.device.availableMeasurements > 0 &&
          <TouchableHighlight onPress={props.downloadClickHandler}>
            <Text>Download</Text>
          </TouchableHighlight>
        }
        {props.device.pendingMeasurements > 0 &&
          <TouchableHighlight onPress={props.uploadClickHandler}>
            <Text>Upload</Text>
          </TouchableHighlight>
        }       
      </View>
    );
  } else {
    return (
      <Text>Device is not connected.</Text>
    );
  }
}