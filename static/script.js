
 function auto_grow(element){
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
 }


 $(document).ready(function() {
   // Auto-dismiss flash messages after 4 seconds (4000 milliseconds)
   $(".alert").delay(4000).fadeOut('slow');
})


function confirmDeletion() {
   var confirmation = confirm("Are you sure you want to delete this account?")
   if (confirm) {
       window.location.href = "{{ url_for('delete') }}";
   } 
   else {
       document.getElementById("confirm-request").innerHTML = "Deletion canceled";
   }

}