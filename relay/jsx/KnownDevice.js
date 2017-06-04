import React from 'react';
import {
  View,
  Text,
  TouchableHighlight
} from 'react-native';

export const KnownDevice = (props) => {
    return (
      <View>
        <Text>{props.device.id} ({props.device.pendingMeasurements})</Text>
        {props.device.pendingMeasurements > 0 &&
          <TouchableHighlight onPress={props.uploadClickHandler}>
            <Text>Upload</Text>
          </TouchableHighlight>
        }       
      </View>
    );
}