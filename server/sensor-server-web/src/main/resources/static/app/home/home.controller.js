(function() {
    'use strict';

    angular
        .module('sensorApp')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$scope', 'SensorService'];

    function HomeController ($scope, SensorService) {
        var vm = this;

        vm.message = "Yo Yo Yo Yo";

        SensorService.byDevice('1zc', 'TEMPERATURE').then(function(data) {
            vm.sensorData = data;
        });
    }
})();
