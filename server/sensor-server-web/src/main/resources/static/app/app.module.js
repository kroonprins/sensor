(function () {
    'use strict';

    angular
        .module('sensorApp', [
            'ngRoute'
        ])
        .config(['$routeProvider',
            function ($routeProvider) {
                $routeProvider.
                    when('/home', {
                        templateUrl: 'app/home/home.html',
                        controller: 'HomeController',
                        controllerAs: 'vm'
                    })
                    .otherwise({
                        redirectTo: '/home'
                    });
            }
        ]);
})();
