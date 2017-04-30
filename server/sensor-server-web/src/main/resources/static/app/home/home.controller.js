(function () {
    'use strict';

    angular
        .module('sensorApp')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$scope', 'SensorService', '$mdDialog'];

    function HomeController($scope, SensorService, $mdDialog) {
        var vm = this;

        const TYPE = "TEMPERATURE";

        SensorService.byDevice('1zc', TYPE).then(function (data) {
            vm.sensorData = data;
            vm.labels = [];
            var data1 = [];
            angular.forEach(data, function (value) {
                vm.labels.push(value.timing);
                data1.push(value.value);
            });

            vm.data = [];
            vm.data.push(data1);
        });

        vm.showDialog = function ($event) {
            var dialog = $mdDialog.confirm().title("Yo?").textContent("Yo? Yo? Yo?").targetEvent($event).ok("Yup").cancel("Nyo");
            $mdDialog.show(dialog);
        }


        //vm.labels = ["January", "February", "March", "April", "May", "June", "July"];
        vm.series = [TYPE];
        /*vm.data = [
            [65, 59, 80, 81, 56, 55, 40]
        ];*/
        //vm.datasetOverride = [{ yAxisID: 'y-axis-1' }];
        vm.options = {
            /*scales: {
                yAxes: [
                    {
                        id: 'y-axis-1',
                        type: 'linear',
                        display: true,
                        position: 'left'
                    }
                ]
            }*/
        };
    }
})();
