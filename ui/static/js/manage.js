function addAnother() {
  var newDiv = $(`<div class="row g-3 incident">
      <div class="col-sm-3">
        <input type="text" class="form-control inputTitle" placeholder="Title" aria-label="Title" required>
      </div>
      <div class="col-sm">
        <input type="text" class="form-control inputScenario" placeholder="Scenario" aria-label="Scenario" required>
      </div>
      <div class="col-sm-1">
        <input class="btn btn-outline-danger removeIncident" type="button" value="Remove" onclick="removeIncident(this);">
      </div>
    </div>`);
  var lastIncident = $('#incidentSetForm .incident:last');
  lastIncident.find('.removeIncident').removeAttr('disabled');
  newDiv.insertAfter(lastIncident);
}

function removeIncident(element) {
  var incident = $(element).closest('.incident');
  incident.remove();
  var incidents = $('#incidentSetForm .incident');
  if (incidents.length == 1) {
    incidents.find('.removeIncident').attr('disabled', 'disabled');
  }
}
if (document.getElementById("incidentSetForm")) {
  document.forms["incidentSetForm"].addEventListener(
    "submit",
    (event) => {
      event.preventDefault();
      document.forms["incidentSetForm"].reportValidity();
      var incidents = [];
      $('#incidentSetForm .incident').each(function (index, element) {
        var incident = {};
        incident.ID = index;
        incident.title = $(element).find('.inputTitle').val();
        incident.scenario = $(element).find('.inputScenario').val();
        incidents.push(incident);
      });
      $.ajax({
        url: "/api/v1/sets",
        type: "PUT",
        data: JSON.stringify(incidents),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
          window.location.href = `/set/${data.id}`;
        }
      });
    },
    false,
  );
}
if (document.getElementById("editIncidentSetForm")) {
  document.forms["editIncidentSetForm"].addEventListener(
    "submit",
    (event) => {
      event.preventDefault();
      document.forms["editIncidentSetForm"].reportValidity();
      var setID = $('#editIncidentSetForm').data('set-id');
      var incidents = [];
      $('#editIncidentSetForm .incident').each(function (index, element) {
        var incident = {};
        incident.ID = index;
        incident.title = $(element).find('.inputTitle').val();
        incident.scenario = $(element).find('.inputScenario').val();
        incidents.push(incident);
      });
      $.ajax({
        url: `/api/v1/sets/${setID}`,
        type: "POST",
        data: JSON.stringify(incidents),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
          window.location.href = `/set/${data.id}`;
        }
      });
    },
    false,
  );
}

function deleteSet(element) {
  var setID = $(element).closest('.incident-set').data('set-id');
  $.ajax({
    url: `/api/v1/sets/${setID}`,
    type: "DELETE",
    success: function (data) {
      $(`[data-set-id="${setID}"]`).remove();
    }
  });
}

$(function () {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
});
