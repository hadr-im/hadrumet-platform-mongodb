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
        const checkboxes = document.querySelectorAll('input[type="checkbox"][name="selected"]');
        checkboxes.forEach((checkbox) => {
            checkbox.checked = source.checked;
        });
}

window.onload =function() {
    let datatable_head = document.getElementById("leads_filter");
    datatable_head.innerHTML = '<div style="margin-bottom: 5px; display: inline-block"><label>Search:<input type="search" class="" placeholder="" aria-controls="leads"></label> <btn class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#filterModal" >Filter</btn></div>';
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
