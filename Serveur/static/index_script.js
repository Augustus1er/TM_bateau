async function loadTable() {

  //  Appel HTTP vers l'endpoint Flask /get_results
  // fetch retourne une Promise (requête asynchrone)
  const response = await fetch('/get_results');
  //  Conversion de la réponse HTTP en JSON
  // response.json() retourne aussi une Promise
  // data sera ici un tableau d'objets JS
  const data = await response.json();

  //  Initialisation du HTML du tableau
  // On utilise un template string (backticks `) pour écrire du HTML multi-lignes
  let htmlTable = `
    <table border="2">
      <thead>
        <tr>
          <th>id</th>
          <th>date</th>
          <th>gps</th>
          <th>Temperature</th>
          <th>mode</th>

        </tr>
      </thead>
      <tbody>
  `;
  //Boucle sur chaque élément du tableau "data"
  // Chaque élément correspond à UNE ligne de la base de données
  data.forEach(item => {

    //  Ajout dynamique d'une ligne <tr> au tableau
    // item.date et item.gps viennent directement du JSON retourné par Flask
    htmlTable += `
      <tr>
        <td>${item.id}</td>
        <td>${item.date}</td>
        <td>${item.gps}</td>
        <td>${item.temperature}</td>
        <td>${item.mode}</td>

      </tr>
    `;
  });

  //  Fermeture du corps du tableau et de la table
  htmlTable += '</tbody></table>';

  // Injection du HTML généré dans la page
  // container-table doit exister dans le HTML
  document.getElementById('container-table').innerHTML = htmlTable;
}

async function AddPoints() {
	const Rmoyenne = await fetch('/moyenne');
	const response = await fetch('/get_results');
	const data = await response.json();
	const moyenne = parseFloat(await Rmoyenne.text());
	data.forEach(item => {
	        const gps = JSON.parse(item.gps);
	        const temperature = parseFloat(item.temperature);

	        let icon;

	        if (temperature > moyenne) {
	            icon = IconRouge;
	        } else if (temperature < moyenne) {
	            icon = IconBleu;
	        } else {
	            icon = IconNoir;
	        }
			var marker = L.marker(gps,{icon: icon}).addTo(map);
				marker.bindPopup(`<b>id=${item.id}</b><br>température=${item.temperature}`).openPopup();
	});
} 
	

var map = L.map('map').setView([46.37, 6.25 ], 10);
    // Add tile layer
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
	
	var IconBleu = L.icon({iconUrl: '../static/image/image(39,39,245).png',iconSize: [50, 50],iconAnchor: [50, 100],popupAnchor: [0, -100],});
	var IconRouge = L.icon({iconUrl: '../static/image/image(245,94,39).png',iconSize: [50, 50],iconAnchor: [50, 100],popupAnchor: [0, -100],});
	var IconNoir = L.icon({iconUrl: '../static/image/image(0,0,0).png',iconSize: [50, 50],iconAnchor: [50, 100],popupAnchor: [0, -100],});
	
	
// Déclenche l'exécution de loadTable une fois que la page est entièrement chargée	
window.addEventListener('load', loadTable);
window.addEventListener('load', AddPoints);
