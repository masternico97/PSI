$(document).ready(function(){
		$('.draggable').on("dragstart", function (draggable) {
			  var dt = draggable.originalEvent.dataTransfer;
			  dt.setData('Text', $(this).attr('id'));
			});
	    $('table td').on("dragenter dragover drop", function (draggable) {
		   event.preventDefault();
		   if (draggable.type === 'drop') {
			  var data = draggable.originalEvent.dataTransfer.getData('Text',$(this).attr('id'));
              alert(draggable.originalEvent.dataTransfer.getData('Text',$(this).attr('id')));
			  de=$('#'+data).detach();
			  de.appendTo($(this));
		   };
	   });
})

// $( init );
//
// function init() {
//   $('.draggable').draggable( {
//     cursor: 'move',
//     containment: 'document',
//     stop: handleDragStop
//   } );
// }
//
// function handleDragStop( event, ui ) {
//   var offsetXPos = parseInt( ui.offset.left );
//   var offsetYPos = parseInt( ui.offset.top );
//   alert( "Drag stopped!nnOffset: (" + offsetXPos + ", " + offsetYPos + ")n");
// }
