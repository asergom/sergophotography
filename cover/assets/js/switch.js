function mySwitch(){
    
    var val = document.getElementsByClassName('switch')[0].getAttribute("value");
    var sela = document.querySelectorAll("a");
    var selh1 =  document.querySelector("h1");
    var selsp = document.querySelector("sp");
    var selswitch = document.getElementsByClassName('switch');
    var selwrapper = document.getElementById('wrapper');
    var selu = document.querySelectorAll("u");
    
    var hovercolorbrown = '#header nav a:before {border-radius: 100%;border: solid 1px brown;}';
    var hovercolorwhite = '#header nav a:before {border-radius: 100%;border: solid 1px white;}';
    var style = document.createElement('style');
    
    var selobj = document.getElementById("cover-svg").contentDocument;
    var selcat = document.querySelectorAll("#category-svg");
    var selcatletters = document.querySelectorAll("#cat-letters-svg")
        
    if (val == "white") {
        
        selswitch[0].setAttribute("value", "brown");    
        selwrapper.style.backgroundColor = "brown";
        
        selh1.style.color = "white";
        
        selobj.getElementById("coverlogo").setAttribute("fill", "white");
        
        for(var i=0;i<selcat.length;i++){
            temp = selcat[i].contentDocument;
            temp.getElementById("cover-logo").setAttribute("stroke", "white");
        }
        
        for(var i=0;i<selcatletters.length;i++){
            temp = selcatletters[i].contentDocument;
            temp.getElementById("cover-letters").setAttribute("fill", "white");
        }
            
        for(var i=0;i<selu.length;i++){
            selu[i].style.color = "white";
            selu[i].style.borderBottomColor = "white";
            selu[i].style.borderTopColor = "white";
        }
                
        for(var i=0;i<sela.length;i++){
            sela[i].style.color = "white";
        }

        style.type = 'text/css';
        if (style.styleSheet) {
            style.styleSheet.cssText = hovercolorwhite;
        } else {
            style.appendChild(document.createTextNode(hovercolorwhite));
        }

        document.getElementsByTagName('head')[0].appendChild(style);
        
    }
    
    if (val == "brown") {
        
        selswitch[0].setAttribute("value", "white");
        selwrapper.style.backgroundColor = "white";
        
        selh1.style.color = "brown";
        
       selobj.getElementById("coverlogo").setAttribute("fill", "brown");
        
        for(var i=0;i<selcat.length;i++){
            temp = selcat[i].contentDocument;
            temp.getElementById("cover-logo").setAttribute("stroke", "brown");
        }
        
        for(var i=0;i<selcatletters.length;i++){
            temp = selcatletters[i].contentDocument;
            temp.getElementById("cover-letters").setAttribute("fill", "brown");
        }
          
        for(var i=0;i<selu.length;i++){
            selu[i].style.color = "brown";
            selu[i].style.borderBottomColor = "brown";
            selu[i].style.borderTopColor = "brown";
        }
                
        for(var i=0;i<sela.length;i++){
            sela[i].style.color = "brown";
        }
        
        
        if (style.styleSheet) {
            style.styleSheet.cssText = hovercolorbrown;
        } else {
            style.appendChild(document.createTextNode(hovercolorbrown));
        }

        document.getElementsByTagName('head')[0].appendChild(style);

        }
}