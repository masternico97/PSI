/*
 * File where several small and useful functions are located
 * Author: Martin Salinas
 */

 /*
  * Function in charge of pausing javascript execution for n miliseconds
  * Author: Martin Salinas
  */
function sleep(miliseconds) {
    if (miliseconds != null) {
        const currentTime = new Date().getTime();
        while (currentTime + miliseconds >= new Date().getTime()) {}
    }
}

/*
 * Function in charge of stopping autoplay
 * Author: Martin Salinas
 */
function stopAutoPlay(id, prev, next) {
    if (id != null && prev != null && next != null) {
        clearInterval(id);
        document.getElementById("auto").innerHTML = "AUTO";
        document.getElementById("auto").onclick = function() { prepareAutoPlay(); };
        if (next === true) {
            document.getElementById("forward").style.visibility = "visible";
        } else {
            document.getElementById("forward").style.visibility = "hidden";
            document.getElementById("replay_end").style.visibility = "visible";
        }
        if (prev === true) {
            document.getElementById("preview").style.visibility = "visible";
        } else {
            document.getElementById("preview").style.visibility = "hidden";
        }
    }
}
