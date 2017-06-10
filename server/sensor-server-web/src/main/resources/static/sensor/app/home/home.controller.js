(function () {
    'use strict';

    angular
        .module('sensorApp')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$scope', 'SensorService', '$mdDialog'];

    function HomeController($scope, SensorService, $mdDialog) {
        var vm = this;

        const TYPE = "TEMPERATURE";

        SensorService.byDevice('000000007d8a3464', TYPE).then(function (data) {
            vm.sensorData = data;
            var points = [];
            angular.forEach(data, function (value) {
            	points.push({ x: value.timing, y: value.value });
            });

            vm.data = [ points ];
        });

        vm.showDialog = function ($event) {
            var dialog = $mdDialog.confirm().title("Yo?").textContent("Yo? Yo? Yo?").targetEvent($event).ok("Yup").cancel("Nyo");
            $mdDialog.show(dialog);
        }

        vm.series = [TYPE];
        vm.options = {
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        displayFormats: {
                        	second: 'HH:mm:ss',
                        	minute: 'HH:mm:ss'
                        },
                    	parser: "YYYY-MM-DD[T]HH:mm:ss[.SSSZ]"
                    }
                }]
            }
        };
    }
})();
