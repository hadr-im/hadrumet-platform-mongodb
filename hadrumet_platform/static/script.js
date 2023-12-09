function togglebutton(checkbox , btnid){
    let cb = document.getElementById(checkbox);
    let btn = document.getElementById(btnid);
    if(cb.checked){
        btn.style.display = "block";
    }else{
        //check if all checkboxes are unchecked
        let allcb = document.getElementsByClassName("form-check-input");
        let allchecked = false;
        for(let i = 0; i < allcb.length; i++){
            if(allcb[i].checked){
                allchecked = true;
            }
        }
        if(!allchecked){
            btn.style.display = "none";
        }
    }
}



function selectAllCheckboxes(source) {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][name="filter"]');
        checkboxes.forEach((checkbox) => {
            checkbox.checked = source.checked;
        });
}

function initializeDataTable(id) {
    let datatable_head = document.getElementById(id);
    if (datatable_head) {
        datatable_head.innerHTML = '<div style="margin-bottom: 5px; display: inline-block"><label>Search:<input type="search" class="" placeholder="" aria-controls="leads"></label> <btn class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#filterModal">Filter</btn></div>';
    }
}

window.onload =function() {
    initializeDataTable("leads_filter");
    initializeDataTable("dispatched_filter");
    initializeDataTable("unmanaged_filter");
}



$(document).ready(function () {
        $('#leads').DataTable();
});

$(document).ready(function () {
        $('#unmanaged').DataTable();
});

$(document).ready(function () {
        $('#dispatched').DataTable();
});
