import {
  NetInfo
} from 'react-native';

class NetworkStatusServiceImpl {
  monitor(callback, interval = 5000) {
    if(!this.pollingMonitor) {
      let _poll = () => {
        NetInfo.fetch().then((result) => {
          callback({
            wifiConnected: result === 'WIFI',
            networkConnected: result === 'WIFI' || result.startsWith('MOBILE')
          });
        });
      };      
      _poll();
      this.pollingMonitor = setInterval(_poll, interval);      
    }
  }
}

export let NetworkStatusService = new NetworkStatusServiceImpl();