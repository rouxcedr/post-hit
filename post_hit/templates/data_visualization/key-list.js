function key_list(){
    var svg = d3.select("body").append("svg");

    svg.attr("width",  250);
    svg.attr("height", 250);

    var rect = svg.append("rect");

    rect.attr("x", 50);
    rect.attr("y", 50);
    rect.attr("width", 20);
    rect.attr("height", 20);
}