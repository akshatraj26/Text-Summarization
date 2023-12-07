
 function auto_grow(element){
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
 }


 $(document).ready(function() {
   // Auto-dismiss flash messages after 3 seconds (3000 milliseconds)
   $(".alert").delay(3000).fadeOut('slow');
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