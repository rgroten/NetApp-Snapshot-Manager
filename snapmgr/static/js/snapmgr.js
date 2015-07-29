
(function() {
	var x2js = new X2JS();
	var app = angular.module('snapmgr', ['ngProgress']);
	
	// Filter to roll bytes into human readable sizes
	app.filter('bytesToSize', function() {
		return function(bytes) {
		    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
		    if (bytes == 0) return 'n/a';
		    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
		    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
		};
	});
	
	app.factory('dataSnapFactory', function($http) {
		var factory = [];
		
		factory.getEnv = function() {
			return $http.get('/getenv');
		}
		factory.getVols = function(env) {
			return $http.post('/vols', {env:env});
		}
		
		factory.getSnaps = function(env, volume) {
			return $http.post('/snaps', {env:env, volume:volume});
		}
		
		factory.createSnap = function(env, volume, newName) {
			return $http.post('/snapcr', {env:env, volume:volume, newName:newName});
		}
		
		factory.deleteSnap = function(env, volume, snapshot) {
			return $http.post('/snapdel', {env:env, volume:volume, snapshot:snapshot});
		}
		
		factory.restoreSnap = function(env, volume, snapshot, rfcNumber) {
			return $http.post('/snaprest', {env:env, volume:volume, snapshot:snapshot, rfcNumber:rfcNumber});
		}
		
		factory.renameSnap = function(env, volume, snapshot, newName) {
			return $http.post('/snaprename', {env:env, volume:volume, snapshot:snapshot, newName:newName});
		}
		return factory;
	});
	
	app.directive("volumes", function() {
		return {
			restrict: 'E',
		    templateUrl: "/static/html/volumes.html"
	   	};
	});
	
	app.directive("error", function() {
		return {
			restrict: 'E',
			templateUrl: "/static/html/error.html"
		};
	});
	
	app.directive("filter", function() {
		return {
			restrict: 'E',
			templateUrl: "/static/html/filter.html"
		};
	});
	
	app.directive("snapshots", function() {
		return {
			restrict: 'E',
			templateUrl: "/static/html/snapshots.html"
		};
	});
	
	app.controller('SnapMgrController', function($scope, dataSnapFactory, ngProgressFactory){
		$scope.vols = [];			// Array of volumes
		$scope.snaps = {};			// Associative array of snapshots. volume name is index key
		$scope.error = null;		// String with error message
		$scope.alerts = [];			// Array of Alerts
		$scope.selectedSnap = null;
		$scope.selectedVol = null;
		$scope.envs = [];
		
		progressBeginColor="royalblue";
		progressCompleteColor="springgreen";
		progressFailColor="firebrick";
		progressbar = ngProgressFactory.createInstance();
		progressbar.setColor(progressBeginColor);

		$scope.loadEnv = function() {
			dataSnapFactory.getEnv()
			.success(function(data) {			
				if (data.envs == null)
					$scope.alerts.push(new Alert("danger", "Couldn't load environment list"));
				else {
					$scope.envs = data.envs;
					$scope.selectedEnv = $scope.envs[0];
					
					// Now force load the volume list
					$scope.loadVols();
				}
			});
		}
		// Function to get volume list from server

		$scope.loadVols = function() {
			progressbar.setColor(progressBeginColor);
			progressbar.start();
			dataSnapFactory.getVols($scope.selectedEnv.name)
			.success(function(data) {
				jsonData = x2js.xml_str2json(data.data);
				
				// If only 1 object exists, json will not return an array 
				// But ng-repeat expects an array so create one for it
				if (jsonData == null) {
					$scope.vols = [];
				}
				else if (jsonData["attributes-list"]["volume-attributes"] instanceof Array)
					$scope.vols = jsonData["attributes-list"]["volume-attributes"];
				else
					$scope.vols = [jsonData["attributes-list"]["volume-attributes"]];
				
				for (var vol in $scope.vols) {
					var volid = $scope.vols[vol]["volume-id-attributes"].name

					// Instantiate array of snaps
					// If snaps[volid] array already populated, don't instantiate
					if ($scope.snaps[volid] == null) {
						$scope.snaps[volid] = [];
					}	
				}
				progressbar.setColor(progressCompleteColor);
				progressbar.complete();
			})
			.error(function(data) {
				if (data.errorMsg)
					errMsg = data.errorMsg;
				else
					errMsg = "Error while contacting server";
				$scope.alerts.push(new Alert("danger", errMsg));

				progressbar.setColor(progressFailColor);
				progressbar.reset();
			});
		};
		
		$scope.loadSnaps = function() {
			//Clear the No Snaps message if set
			$('#noSnapsDiv').text("");
			volume = $scope.selectedVol['volume-id-attributes'].name
			progressbar.setColor(progressBeginColor);
			progressbar.start();
			if ($scope.snaps.length > 0) {
				$scope.snaps = [];
			}
			dataSnapFactory.getSnaps($scope.selectedEnv.name, volume)
			.success(function(data) {
				jsonData = x2js.xml_str2json(data.data);
				
				// If only 1 object exists, json will not return an array 
				// But ng-repeat expects an array so create one for it
				if (jsonData == null) {
					$scope.snaps[volume] = [];
					$('#noSnapsDiv').text("No Snapshots found");
				}
				else if (jsonData["snapshots"]["snapshot-info"] instanceof Array)
					$scope.snaps[volume] = jsonData["snapshots"]["snapshot-info"];
				else
					$scope.snaps[volume] = [jsonData["snapshots"]["snapshot-info"]];
				
				progressbar.setColor(progressCompleteColor);
				progressbar.complete();
			})
			.error(function(data) {
				if (data.errorMsg)
					errMsg = data.errorMsg;
				else
					errMsg = "Error while contacting server";
				$scope.alerts.push(new Alert("danger", errMsg));

				progressbar.setColor(progressFailColor);
				progressbar.reset();
			});
		};
		// TODO lots of duplicate code in action functions.  Extract into module?
		$scope.createSnapshot = function(volume) {
			progressbar.setColor(progressBeginColor);
			progressbar.start();
			newName = $('#createSnapText').val();
			$('#createSnapText').val("");
			
			dataSnapFactory.createSnap($scope.selectedEnv.name, volume, newName)
			.success(function(data) {
				$scope.alerts.push(new Alert("success","Snapshot created successfully"));
				progressbar.setColor(progressCompleteColor);
				progressbar.complete();
				$scope.loadSnaps();
				// TODO: Somehow need to increment volume snapshot count on success (reload vols?)
//					$scope.selectedVol['volume-snapshot-attributes']['snapshot-count'] += 1;
			})
			.error(function(data) {
				if (data.errorMsg)
					errMsg = data.errorMsg;
				else
					errMsg = "Error while contacting server";
				$scope.alerts.push(new Alert("danger", errMsg));

				progressbar.setColor(progressFailColor);
				progressbar.reset();
			});
		}
		
		$scope.deleteSnapshot = function() {
			volume = $scope.selectedVol['volume-id-attributes'].name;
			snapshot = $scope.selectedSnap.name;
			progressbar.setColor(progressBeginColor);
			progressbar.start();
			
			dataSnapFactory.deleteSnap($scope.selectedEnv.name, volume, snapshot)
			.success(function(data) {
				$scope.alerts.push(new Alert("success","Snapshot deleted successfully"));
				progressbar.setColor(progressCompleteColor);
				progressbar.complete();
				$scope.loadSnaps();
			})
			.error(function(data) {
				if (data.errorMsg)
					errMsg = data.errorMsg;
				else
					errMsg = "Error while contacting server";
				$scope.alerts.push(new Alert("danger", errMsg));

				progressbar.setColor(progressFailColor);
				progressbar.reset();
			});
		}
		
		$scope.restoreSnapshot = function() {
			volume = $scope.selectedVol['volume-id-attributes'].name;
			snapshot = $scope.selectedSnap.name; 
			rfcNumber = $('#restoreSnapText').val();
			progressbar.setColor(progressBeginColor);
			progressbar.start();
			
			dataSnapFactory.restoreSnap($scope.selectedEnv.name, volume, snapshot, rfcNumber)
			.success(function(data) {
				$scope.alerts.push(new Alert("success","Snapshot restored successfully"));
				progressbar.setColor(progressCompleteColor);
				progressbar.complete();
				$scope.loadSnaps();
			})
			.error(function(data) {
				if (data.errorMsg)
					errMsg = data.errorMsg;
				else
					errMsg = "Error while contacting server";
				$scope.alerts.push(new Alert("danger", errMsg));

				progressbar.setColor(progressFailColor);
				progressbar.reset();
			});
		}
		
		$scope.renameSnapshot = function() {
			volume = $scope.selectedVol['volume-id-attributes'].name;
			snapshot = $scope.selectedSnap.name;
			newName = $('#renameSnapText').val();
			progressbar.setColor(progressBeginColor);
			progressbar.start();
			
			// After submit is pressed, clear text and reset form.
			// Using $setPristine causes modal to not hide, so do it manually
			$scope.renameSnapText = "";
			$scope.renameSnapForm.$setPristine();
			$('#renameModal').modal('hide');

			dataSnapFactory.renameSnap($scope.selectedEnv.name, volume, snapshot, newName)
			.success(function(data) {
				$scope.alerts.push(new Alert("success","Snapshot renamed successfully"));
				progressbar.setColor(progressCompleteColor);
				progressbar.complete();
				$scope.loadSnaps();
			})
			.error(function(data) {
				if (data.errorMsg)
					errMsg = data.errorMsg;
				else
					errMsg = "Error while contacting server";
				$scope.alerts.push(new Alert("danger", errMsg));

				progressbar.setColor(progressFailColor);
				progressbar.reset();
			});
		}
		
		var isSnapsCollapseVisible = false;
//			TODO: Use .collapse('toggle') logic instead
		$scope.toggleSnapPanel = function(forceVisible) {
			if (forceVisible) {
				console.log("got forceVisible true");
				isSnapsCollapseVisible = false;
			}
			if (isSnapsCollapseVisible) {
				// Hide snapshot panel
				$("#collapseSnaps").collapse('hide');
				$("#toggleSnapPanel").text("Show Snapshot Panel");
				$("#volumePanel").addClass("panel-full");
				isSnapsCollapseVisible = false;
			} else {
				// Show snapshot panel
				$("#collapseSnaps").collapse('show');
				$("#toggleSnapPanel").text("Hide Snapshot Panel");
				$("#volumePanel").removeClass("panel-full");
				isSnapsCollapseVisible = true;
			}
		}
		
//			Volume pane is visible on startup
		var isVolsCollapseVisible = true;
		$scope.toggleVolPanel = function(forceVisible) {
			if (forceVisible) {
				console.log("got forceVisible true");
				isVolsCollapseVisible = false;
			}
			if (isVolsCollapseVisible) {
				// Hide snapshot panel
				$("#collapseVols").collapse('hide');
				$("#toggleVolPanel").text("Show Volume Panel");
				$("#snapPanel").addClass("panel-full");
				isVolsCollapseVisible = false;
			} else {
				// Show snapshot panel
				$("#collapseVols").collapse('show');
				$("#toggleVolPanel").text("Hide Volume Panel");
				$("#snapPanel").removeClass("panel-full");
				isVolsCollapseVisible = true;
			}
		}
		
		// Load environments when controller loads
		$scope.loadEnv();
	});
	
	//Hide alert when dismissed
	$(function(){
	    $("[data-hide]").on("click", function(){
	        $(this).closest("." + $(this).attr("data-hide")).hide();
	    });
	});
})();
