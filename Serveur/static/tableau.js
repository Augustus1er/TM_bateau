// Fonction asynchrone : permet d'utiliser "await" à l'intérieur
// Elle sera appelée au chargement de la page
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
// Déclenche l'exécution de loadTable une fois que la page est entièrement chargée
window.addEventListener('load', loadTable);