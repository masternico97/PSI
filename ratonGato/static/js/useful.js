function sleep(miliseconds) {
    var currentTime = new Date().getTime();
    while (currentTime + miliseconds >= new Date().getTime()) {}
}

// function change_button_text(button_id)  {
//    var text = document.getElementById(button_id).firstChild;
//    text.data = text.data == "Play" ? "Pause" : "Play";
// }
