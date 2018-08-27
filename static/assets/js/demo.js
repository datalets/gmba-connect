(function($) {

	$(function() {

		$container = $('#content')
		var runSearch = function(query) {
			var filters = [{"name": "id", "op": "like", "val": "%y%"}];
$.ajax({
  data: {"filter[objects]": JSON.stringify(filters)},
  headers: {
    "Accept": JSONAPI_MIMETYPE
  },
			$.getJSON('/api/person', data, function(data) {
				$.each(data, function() {
					var fulltext = this.fullname + ' ' + this.organisation + ' ' + this.biography;
					fulltext = fulltext.toLowerCase();
					$container.append(
						'<div class="person">' +
						'<h4>' + this.fullname + '</h4>' +
						'<span>' + this.organisation + '</span> &nbsp;' +
						'<a class="c-button c-button--brand u-small" href="' + this.personal + '">Details</a>' +
						'<hide>' + fulltext + '</hide>' +
						'</div>'
					);
				});
			}); //- getJSON
		} //- runSearch

		var delay = (function(){
		  var timer = 0;
		  return function(callback, ms){
		    clearTimeout (timer);
		    timer = setTimeout(callback, ms);
		  };
		})();
		$('input[name="query"]').on('input', function() {
				var q = $(this).val().toLowerCase();
				if (q.length < 3)
					return $container.addClass('hide');

				// console.log(q);
				$('#help').hide();
				delay(runSearch(q));
		});

		$('#show-advanced').click(function() { $('#advanced').show() });

		var mymap = L.map('map').setView([51.505, -0.09], 1);

		L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
			maxZoom: 18,
			attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
				'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
				'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
			id: 'mapbox.streets'
		}).addTo(mymap);

		var mountain_ranges = new L.GeoJSON.AJAX("/data/gmba.geojson");
		mountain_ranges.addTo(mymap);

	});

})(jQuery);
