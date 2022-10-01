

let request_url = document.location.pathname

console.log("URL => ", request_url)

if (request_url === "/venues/create") {
	/* Handling Venue form submission. */
	document.getElementById('venue-form').onsubmit = function (e) {
		e.preventDefault();
		const formData = new FormData(document.getElementById('venue-form'));
		const payload = {
			'name': document.getElementById('name').value,
			'city': document.getElementById('city').value,
			'state': document.getElementById('state').value,
			'address': document.getElementById('address').value,
			'phone': document.getElementById('phone').value,
			'genres': formData.getAll('genres'),
			'facebook_link': document.getElementById('facebook_link').value,
			'image_link': document.getElementById('image_link').value,
			'website_link': document.getElementById('website_link').value,
			'seeking_talent': document.getElementById('seeking_talent').checked,
			'seeking_description': document.getElementById('seeking_description').value,
		}
		console.log("Venue form submitted [Form Data] ==> ", payload);

		fetch('/venues/create', {
			method: 'POST',
			body: JSON.stringify(payload),
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then(function (response) {

				console.log("Venue form response => ", response);
				return response.json();
			})
			.then(function (jsonResponse) {

				console.log("Venue form JSON response => ", jsonResponse);

				// TODO: Redirect to appropriate page
			})
			.catch(function () {
				document.getElementById('error').className = '';
				console.log("Error submitting venue form");
			})
	}
}

if (request_url === "/artists/create") {
	/* Handling Artist form submission. */
	document.getElementById('artist-form').onsubmit = function (e) {
		e.preventDefault();
		const formData = new FormData(document.getElementById('artist-form'));
		const payload = {
			'name': document.getElementById('name').value,
			'city': document.getElementById('city').value,
			'state': document.getElementById('state').value,
			'phone': document.getElementById('phone').value,
			'genres': formData.getAll('genres'),
			'facebook_link': document.getElementById('facebook_link').value,
			'image_link': document.getElementById('image_link').value,
			'website_link': document.getElementById('website_link').value,
			'seeking_venue': document.getElementById('seeking_venue').checked,
			'seeking_description': document.getElementById('seeking_description').value,
		}

		console.log("Artist form submitted [Form Data] ==> ", payload);

		fetch('/artists/create', {
			method: 'POST',
			body: JSON.stringify(payload),
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then(function (response) {

				console.log("Artist form response => ", response);
				return response.json();
			})
			.then(function (jsonResponse) {

				console.log("Artist form JSON response => ", jsonResponse);

				// TODO: Redirect to appropriate page
			})
			.catch(function () {
				document.getElementById('error').className = '';
				console.log("Error submitting artist form");
			})
	}
}













if (request_url === "/shows/create") {
	/* Handling Show form submission. */
	document.getElementById('show-form').onsubmit = function (e) {
		e.preventDefault();
		const payload = {
			'venue_id': document.getElementById('venue_id').value,
			'artist_id': document.getElementById('artist_id').value,
			'start_time': document.getElementById('start_time').value,
		}

		console.log("Show payload => ", payload)

		fetch('/shows/create', {
			method: 'POST',
			body: JSON.stringify(payload),
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then(function (response) {

				console.log("Show form response => ", response);
				return response.json();
			})
			.then(function (jsonResponse) {

				console.log("Show form JSON response => ", jsonResponse);

				// TODO: Redirect to appropriate page
			})
			.catch(function () {
				document.getElementById('error').className = '';
				console.log("Error submitting show form");
			})
	}
}
