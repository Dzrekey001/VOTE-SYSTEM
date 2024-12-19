function handleCheckbox(checkbox) {
    if (checkbox.checked) {
        // Checkbox is checked, handle the selection logic
        var portfolioTable = checkbox.closest('.form-table');
        var checkboxes = portfolioTable.querySelectorAll('.candidate-checkbox');

        checkboxes.forEach(function (currentCheckbox) {
            if (currentCheckbox !== checkbox) {
                currentCheckbox.checked = false;
            }
        });
    } else {
        // Checkbox is unchecked, handle the deselection logic (optional)
    }
}
