temp = document.getElementsByTagName("template")[0];
item = temp.content.querySelector("div");
tempContainer = document.getElementsByTagName("template")[1];
container = tempContainer.content.querySelector("div");
tempLink = document.getElementsByTagName("template")[2];
emptyLink = tempLink.content.querySelector("div");
tempEditorial = document.getElementsByTagName("template")[3];
emptyEditorial = tempEditorial.content.querySelector("div");
tempHelp = document.getElementsByTagName("template")[4];
emptyHelp = tempHelp.content.querySelector("div");

function addProblemLinks(a, badge, k, badgeEl){
    //.querySelector("a")
    newLink = document.importNode(emptyLink, true);
    newLink.querySelector("a").href = "https://open.kattis.com/problems/" + badge[badgeEl][k][0];
    newLink.querySelector("a").textContent = badge[badgeEl][k][1];
    //a.getElementsByClassName(className)[0].appendChild(newLink);    
    return newLink;
}

function displayBadges(data){
    $('.badge-container').remove();
    badgesprogress = JSON.parse(data);
    
    badges = badgesprogress["badges"]
    for(i = 0; i < badges.length; i++){
        var badgeGroup = badges[i];
        c = document.importNode(container, true);
        c.querySelector("h2").textContent = badgeGroup["group-name"];
        document.body.appendChild(c);
        for(j = 0; j < badgeGroup["badges"].length; j++){
             badge = badgeGroup["badges"][j];
             a = document.importNode(item, true);
             a.getElementsByClassName("badge-name")[0].textContent = badge["name"];
             a.getElementsByClassName("badge-icon")[0].src = badge["icon"];
            if (!badge["finished"]) a.getElementsByClassName("badge-icon")[0].style = "filter: grayscale(100%);";
             a.getElementsByClassName("completed")[0].textContent += (badge["finished"]) ? "✔️" : "❌";
             a.getElementsByClassName("desc")[0].textContent = badge["desc"];

             var progress = a.getElementsByClassName("progress-bar")[0];
             progress.textContent = badge["progress"][0] + "/" + badge["progress"][1];
             var percent_done = (badge["progress"][0] / badge["progress"][1]) * 100
             progress.style.width = percent_done + "%";
             if(percent_done == 100) progress.classList.add("bg-success");
             else if(percent_done >= 50) progress.classList.add("bg-warning");
             else progress.classList.add("bg-danger");
             progress.setAttribute("aria-valuenow", percent_done);

             if(badge["type"] == "problems"){
                 if(badge["completed_problems"].length > 0){
                    a.getElementsByClassName("problems-solved")[0].innerHTML = "<b>Problems Solved: </b>";
                    for(k = 0; k < badge["completed_problems"].length; k++){
                        var newLink = addProblemLinks(a, badge, k, "completed_problems");  
                        a.getElementsByClassName("problems-solved")[0].appendChild(newLink);    
					}
				 }
                 else{
                    a.getElementsByClassName("problems-solved")[0].textContent = "";        
				 }
                 if(!badge["finished"]){
                    a.getElementsByClassName("problems-left")[0].innerHTML = "<b>Problems Left: </b>";
                    for(k = 0; k < badge["left"].length; k++){
                        var newLink = addProblemLinks(a, badge, k, "left", "problems-left");
                        if(badge["left"][k].length > 2){
                            var ed = document.importNode(emptyEditorial, true);
                            ed.getElementsByClassName("editorial")[0].textContent = badge["left"][k][2];
                            ed.insertBefore(newLink.querySelector("a"), ed.firstChild);
                            a.getElementsByClassName("problems-left")[0].appendChild(ed);    
						}
                        else{
                            a.getElementsByClassName("problems-left")[0].appendChild(newLink);    
						}
                     
					}
				 }
                 else{
                    a.getElementsByClassName("problems-left")[0].textContent = "";
				 }
	         }
             else if(badge["type"] == "langs"){
                a.getElementsByClassName("problems-solved")[0].innerHTML = (badge["completed_problems"].length == 0) ? "" : "<b>Languages used for problems: </b>";
                var keys = Object.keys(badge["completed_problems"]);
                keys.forEach(key=>{
                    a.getElementsByClassName("problems-solved")[0].innerHTML += (" " + key + ': ' + badge["completed_problems"][key] + " ");
                });
                a.getElementsByClassName("problems-left")[0].innerHTML = (!badge["finished"]) ? "<b>Languages Left: </b>" : "";
                var keys = Object.keys(badge["left_langs"]);
                keys.forEach(key=>{
                    a.getElementsByClassName("problems-left")[0].innerHTML += (" " + key + ': ' + badge["left_langs"][key] + " ");
                });
	         }
             var badgeLinks = badge["links"];
             if(badgeLinks.length > 0){
                var title = document.importNode(emptyHelp, true);
                for(var k = 0; k < badgeLinks.length; k++){
                    var newLink = document.importNode(emptyLink.querySelector("a"), true);
                    newLink.href = badgeLinks[k][0];
                    newLink.textContent = badgeLinks[k][1];
                    title.appendChild(newLink);
				}
                a.getElementsByClassName("badge-hide")[0].appendChild(title);
			 }
             //a.gtextContent = "Problems Left: " + badge["left"] + "Finished Problems: " + badge["completed_problems"];// + "\n" + (badge["finished"] == true) ? "✔️" : "❌";
             document.getElementsByClassName("badge-container")[i].appendChild(a);
		}
	}
}

function readBadgeJson(file){
    if(file == null) return;
    if(file.type && file.type != "application/json"){
        $("#not-json-alert").addClass("show");
        setTimeout(function() { $("#not-json-alert").removeClass("show"); }, 3000);
        return;
	}
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
      displayBadges(event.target.result);
    });
    reader.readAsText(file);
}

function toggleEditorial(event){
    $(event.target).next().collapse("toggle");
    //$("this div:first").collapse("toggle");
    //el.find(".spoiler-content")[0].collapse();
    //el.parentElement.getElementsByClassName("spoiler-content")[0].collapse();
    //edbox.style.display = (window.getComputedStyle(edbox).display === "none") ? "block" : "none"
}

function toggleBadge(event){
    $(event.target).parent().next().collapse("toggle");
    if($(event.target).data("rotated") == false){
        $(event.target).rotate({ endDeg: 180, persist:true, easing:'ease-in', duration:0.3 });
        $(event.target).data("rotated", true)
    }
    else {
        $(event.target).rotate({ endDeg: 360, persist:true, easing:'ease-out', duration:0.3 });
        $(event.target).data("rotated", false)
    }
}

fetch('http://localhost:5000/badgeprogress')
  .then(response => response.text())
  .then(data => {
    displayBadges(data);
});

const fileSelector = document.getElementById('file-selector');
fileList = null;
  fileSelector.addEventListener('change', (event) => {
    fileList = event.target.files;
    console.log(fileList[0]);
    //readBadgeJson(fileList[0]);
});

document.getElementById("submitBadgeButton").onclick = function() {readBadgeJson(fileList[0])};

