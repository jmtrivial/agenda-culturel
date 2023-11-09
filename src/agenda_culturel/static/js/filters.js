let underToggle = false;

const toggleElement = (event) => {
    console.log(event.currentTarget.getAttribute("data-target"));
    container = document.getElementById(event.currentTarget.getAttribute("data-target"));
    setFilterClasses(container);
};


// Toggle select all elements
const toggleSelectAllFilterElements = (event) => {
    event.preventDefault();

    selectAllFilterElementsFromCheckbox(event.currentTarget);
};

const selectAllFilterElementsFromCheckbox = (checkbox) => {
    const container = document.getElementById(checkbox.getAttribute("data-target"));
    active = checkbox.checked;
    
    Array.prototype.forEach.call(container.children, function(child) {
        Array.prototype.forEach.call(child.getElementsByTagName("input"), function(elem) {
            elem.checked = active;
        }); 
    });
    setFilterClasses(container);
};

const setFilterClasses = (container) => {
    console.log("set filter");
    if (!underToggle) {
        underToggle = true;
        selectionButtom = document.getElementById(container.getAttribute("data-button"));
        checkboxes = container.getElementsByTagName("input");
        // count the number of selected elements
        nbElemsChecked = 0;
        for (i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) {
                nbElemsChecked++;
            }
        }

        // count the number of elements
        nbElems = checkboxes.length;

        // if all elements are deselected, the class "no-selected" is removed and the all selection button is deselected
        if (nbElemsChecked == 0) {
            Array.prototype.forEach.call(checkboxes, function(checkbox) {
                checkbox.parentNode.parentNode.classList.remove("no-selected");
            });
            selectionButtom.checked = false;
            selectionButtom.indeterminate = false;
        }
        else {
            // otherwise, for each filter element, set "no-selected" class if required
            Array.prototype.forEach.call(checkboxes, function(checkbox) {
                if (checkbox.checked)
                    checkbox.parentNode.parentNode.classList.remove("no-selected");
                else
                    checkbox.parentNode.parentNode.classList.add("no-selected");
            });

            // if all elements are selected, the all selection button is selected, otherwise its set to "indeterminate"
            if (nbElems == nbElemsChecked) {
                selectionButtom.checked = true;
                selectionButtom.indeterminate = false;
            } else {
                selectionButtom.indeterminate = true;
                selectionButtom.checked = false;
            }
        }

        underToggle = false;
    }
}

document.addEventListener("DOMContentLoaded", function(e) {
    Array.prototype.forEach.call(document.getElementsByClassName("buttons-filter"), function(buttongroup) {
        buttongroup.style.display = "inline-block";
    });

    const buttonsAll = document.getElementsByClassName("all-elements");

    Array.prototype.forEach.call(buttonsAll, function(button) {
        const container = document.getElementById(button.getAttribute("data-target"));
        setFilterClasses(container);
    });


});
  