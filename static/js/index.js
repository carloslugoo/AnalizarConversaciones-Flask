function handleFileUpload() {
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];

  if (file) {
      // Verificar el tipo de archivo (por ejemplo, solo permitir archivos .zip)
      if (file.name.slice(-4) !== '.zip') {
          // Mostrar alerta de error si el formato no es adecuado
          Swal.fire({
              icon: 'error',
              title: 'Error',
              text: 'Formato de archivo no válido. Por favor, selecciona un archivo con extensión .zip.',
              confirmButtonColor: '#28a745', // Establece el color del botón de confirmación
              customClass: {
                  confirmButton: 'btn btn-success'
              }
          });
          return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10 megabytes en bytes
          Swal.fire({
              icon: 'error',
              title: 'Error',
              text: 'Tu archivo es muy grande (menos de 10MB), podría ser que intentas subirlo con multimedia',
              confirmButtonColor: '#28a745',
              customClass: {
                  confirmButton: 'btn btn-success'
              }
          });
      }

      // Mostrar una pantalla de carga mientras se realiza la solicitud AJAX
      Swal.fire({
          title: 'Cargando...',
          allowOutsideClick: false,
          showCancelButton: false,
          showCloseButton: false,
          timerProgressBar: true,
          customClass: {
              confirmButton: 'btn btn-success'
          },
          onBeforeOpen: () => {
              Swal.showLoading();
          },
      });

      // Crear un objeto FormData y añadir el archivo
      const formData = new FormData();
      formData.append('file', file);

      fetch('/chats/recibir', {
          method: 'POST',
          body: formData,
      })
          .then(response => {
              if (!response.ok) {
                  throw new Error('Error en la solicitud');
              }
              return response.json();
          })
          .then(data => {
            window.location.href = data.url;
          })
          .catch(error => {
              // Puedes agregar aquí el código para manejar errores
              Swal.fire({
                  icon: 'error',
                  title: 'Error',
                  text: 'Probablemente tu archivo .zip no contiene una conversación',
                  confirmButtonColor: '#28a745',
                  customClass: {
                      confirmButton: 'btn btn-success'
                  }
              });
          });
  }
}