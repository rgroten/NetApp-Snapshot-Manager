(function() {
	var app = angular.module('opmgr', ['ngRoute', 'ngAnimate', 'snapmgr']);
	
	app.config(function($routeProvider) {
		$routeProvider
			.when('/', {
				templateUrl : '/static/html/main.html',
				controller : 'MainController'
			})
			.when('/home', {
				templateUrl : '/static/html/main.html',
				controller : 'MainController'
			})
			.when('/snapmgr', {
				templateUrl: '/static/html/snapmgr.html',
				controller : 'SnapMgrController'
			});
	});
	
	
	app.directive("naviBar", function() {
		return {
			restrict: 'E',
			templateUrl: "/static/html/navi-bar.html"
		};
	});
	
	app.controller('MainController', function($scope){
		$scope.message = "MainController";
	});

})();


//Object to hold error message and its severity {success, info, warning, danger}
function Alert(severity, message) {
	
	this.severity = severity;
	this.message = message;
	
	return this;
}