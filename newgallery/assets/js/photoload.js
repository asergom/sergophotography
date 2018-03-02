function imageExists(image_url){

    var http = new XMLHttpRequest();

    http.open('HEAD', image_url, false);
    http.send();

    return http.status != 404;;

}

/* */
function showCaseFunction(photoID) {

    var caseID = document.getElementsByClassName('showcase ' + photoID.id)[0];   

    if (caseID.innerHTML == "click_for_raw_view"){

        var photoURL = "images/raw/" + album + "/" + photoID.id + "_ori.jpg";
        var loaded = imageExists(photoURL);
        console.log(loaded);

        if (loaded) {
            document.getElementById(photoID.id).getElementsByTagName("img")[0].src = "images/raw/" + album + "/" + photoID.id + "_ori.jpg";
        }
        else {
            console.log("here")
            document.getElementById(photoID.id).getElementsByTagName("img")[0].src = "images/raw/no_ori.jpg";
        }

        caseID.innerHTML = "click_for_developed_view";
    }

    else {
        document.getElementById(photoID.id).getElementsByTagName("img")[0].src = "images/fulls/" + album + "/" + photoID.id + ".jpg";
        caseID.innerHTML = "click_for_raw_view";
    }

}

/* Load reference names */
var img = [];
var album = document.title;
album = album.toLowerCase(document.title);
album = album.replace(/\s/g, '');
console.log(album)

/* Load album data */

/* Photo load */
for (i=0; i<photo.length; i++ ) {
    var img = document.createElement('div');
    img.className = "thumb";
    img.innerHTML = '<a href=#' + photo[i].name + 
        '><img class="gallery"' + 
        'data-src="images/thumbs/' + album + '/' + photo[i].name + '.jpg" />' + 
        '<div class="caption">' +
        '<h1><table id="mytable">' + 
        '<tr><td class="right">ISO: </td><td class="left">' + photo[i].ISO + '</td></tr>' +
        '<tr><td class="right">Exposure Time: </td><td class="left">' + photo[i].ExposureTime + '</td></tr>' +
        '<tr><td class="right">Aperture: </td><td class="left">' + photo[i].Aperture + '</td></tr>' +
        '<tr><td class="right">Focal length: </td><td class="left">' + photo[i].FocalLength + '</td></tr>' +
        '</table></h1>' + 
        '</div></a>';
    document.getElementById('photoload').appendChild(img);
        
    var showimg = document.createElement('div');
    var divdef = '<div href="#' + photo[i].name + '" class="lightbox" id="' + photo[i].name +'">' + 
    '<ul><li id="infophoto">ISO:&nbsp;' + photo[i].ISO + '</li>' + 
    '<li id="infophoto">Exposure Time:&nbsp;' + photo[i].ExposureTime + '</li>' + 
    '<li id="infophoto">Aperture:&nbsp;' + photo[i].Aperture + '</li>' + 
    '<li id="infophoto">Focal length:&nbsp;' + photo[i].FocalLength + '</li></ul>' + 
    '<img src="images/fulls/' + album + '/' + photo[i].name + '.jpg" />'

    if (i == 0) {
        showimg.innerHTML = divdef + '<ul><li id="dumcircle"><a class="fa fa-circle"></a></li><li id="closephoto"><a class="fa fa-close" href="#"></a></li><li id="arrowright"><a class="fa fa-arrow-circle-right" href="#' + photo[i+1].name + '"></a></li></ul><ul><li><a class="showcase ' + photo[i].name + '" onClick="showCaseFunction(' + photo[i].name + ')">click_for_raw_view</a></li></ul></div>';
    }
    else if (i == photo.length-1) {
        showimg.innerHTML = divdef + '<ul><li id="arrowleft"><a class="fa fa-arrow-circle-left" href="#' + photo[i-1].name + '"></a></li><li id="closephoto"><a class="fa fa-close" href="#"></a></li><li id="dumcircle"><a class="fa fa-circle"></a></li></ul><ul><li><a class="showcase ' + photo[i].name + '" onClick="showCaseFunction(' + photo[i].name + ')">click_for_raw_view</a></li></ul></div>';
    }
    else {
        showimg.innerHTML = divdef + '<ul><li id="arrowleft"><a class="fa fa-arrow-circle-left" href="#' + photo[i-1].name + '"></a></li><li id="closephoto"><a class="fa fa-close" href="#"></a></li><li id="arrowright"><a class="fa fa-arrow-circle-right" href="#' + photo[i+1].name + '"></a></li></ul><ul><li><a class="showcase ' + photo[i].name + '" onClick="showCaseFunction(' + photo[i].name + ')">click_for_raw_view</a></li></ul></div>';
    }
       
    document.getElementById('photoload').appendChild(showimg);
    
}
