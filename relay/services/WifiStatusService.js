import {
  NetInfo
} from 'react-native';

class WifiStatusServiceImpl {
  isConnected() {
    return NetInfo.fetch().then((result) => {
      if(result === 'WIFI') {
        return true;
      } else {
        return false;
      }
    });
  }
}

export let WifiStatusService = new WifiStatusServiceImpl();