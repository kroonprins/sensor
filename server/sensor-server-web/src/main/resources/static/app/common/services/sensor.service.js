(function () {
    'use strict';

    angular
        .module('sensorApp')
        .factory('SensorService', SensorService);

    SensorService.$inject = ['$http'];

    function SensorService($http) {
        var service = {
            byDevice: byDevice
        };

        return service;

        function byDevice(deviceId, measurementType) {
            return $http.get('/sensors/' + deviceId, { params: { type: measurementType } }).then(processResponse);

            function processResponse(response) {
                return response.data;
            }
        }
    }
})();
