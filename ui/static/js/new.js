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
