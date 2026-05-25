// Definición del formulario (podría venir luego de un JSON o API)
const formDefinition = [
  { label: "Nombre completo", name: "nombre", type: "text", required: true },
  { label: "Correo electrónico", name: "email", type: "email", required: true },
  { label: "Edad", name: "edad", type: "number" },
  { label: "Género", name: "genero", type: "select", options: ["Masculino", "Femenino", "Otro"] },
  { label: "Comentarios", name: "comentarios", type: "textarea" }
];

// Referencia al formulario
const form = document.getElementById("dynamicForm");

// Crear los campos
formDefinition.forEach(field => {
  const col = document.createElement("div");
  col.classList.add("col-md-6");

  const label = document.createElement("label");
  label.classList.add("form-label");
  label.textContent = field.label;

  let input;
  if (field.type === "select") {
    input = document.createElement("select");
    input.classList.add("form-select");
    field.options.forEach(opt => {
      const o = document.createElement("option");
      o.value = opt;
      o.textContent = opt;
      input.appendChild(o);
    });
  } else if (field.type === "textarea") {
    input = document.createElement("textarea");
    input.classList.add("form-control");
    input.rows = 3;
  } else {
    input = document.createElement("input");
    input.type = field.type;
    input.classList.add("form-control");
  }

  input.name = field.name;
  input.required = field.required || false;

  col.appendChild(label);
  col.appendChild(input);
  form.appendChild(col);
});

// Envío al backend
document.getElementById("submitBtn").addEventListener("click", async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("http://127.0.0.1:5000/api/enviar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    mostrarAlerta(result.message, "success");
    form.reset();
  } catch (error) {
    mostrarAlerta("Error al enviar los datos", "danger");
  }
});

function mostrarAlerta(mensaje, tipo) {
  const alertContainer = document.getElementById("alertContainer");
  alertContainer.innerHTML = `
    <div class="alert alert-${tipo}" role="alert">
      ${mensaje}
    </div>`;
}
