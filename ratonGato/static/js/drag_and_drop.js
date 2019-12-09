/* 
 * Function incharge of the drag and drop of the game 
 * Author: Martin Salinas
 */

$(document).ready(function() {
	var initial_position = -1;
	var final_position = -1;

	$('.draggable').on("dragstart", function (draggable) {
          var elemId = $(this).parent().attr("id");
		  initial_position = elemId.substring(11, elemId.length);
		  // var gif = document.createElement("img");
		  // gif.src = "sample_url";
		  // draggable.dataTransfer.setDragImage(gif, 0, 0);
		  // var img = $(this).attr("id");
		  //document.getElementById(img).style.visibility = "hidden";
		  //document.getElementById(img).hidden = true;
    });

	$('.blank_cell').on("dragenter dragover drop", function (draggable) {
		draggable.preventDefault();
		if (draggable.type === 'drop') {
			var elemId = $(this).parent().attr("id");
			final_position = elemId.substring(5, elemId.length);
			document.getElementById("id_origin").value = initial_position;
			document.getElementById("id_target").value = final_position;
			initial_position = -1;
			final_position = -1;
			document.getElementById("move_button").click();
		}
	});
});

function replay(s){
	alert(s);
}