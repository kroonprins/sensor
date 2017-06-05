import React from 'react';
import {
  View,
  Text
} from 'react-native';

export const UploadServer = (props) => {
  return (
    <View>
      <Text>Upload server is {props.status ? "" : "not "}available</Text>
    </View>
  );
}