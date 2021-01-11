// Use the margin convention practice
var margin = {top: 50, right: 50, bottom: 50, left: 70}
  , width = 700 - margin.left - margin.right // Use a hard-coded width for now, improve later
  , height = 700 - margin.top - margin.bottom; // Use a hard-coded height for now, improve later

// Data is an an array of objects of length N. Each object has key -> value pair
// cdf_data
// pdf_data 

// The number of datapoints
var n = cdf_data.length

// use d3.scaleLinear() to convert between data coordinates and SVG coordinates
// Same xScale for both PDF and CDF
var xScale = d3.scaleLinear()
    .domain([cdf_metadata.xmin, cdf_metadata.xmax]) // input
    .range([0, width]); // output

var cdf_yScale = d3.scaleLinear()
    .domain([0,1]) // input
    .range([height, 0]); // output

var pdf_yScale = d3.scaleLinear()
    .domain([pdf_metadata.ymin, maximum_density_to_display]) // input
    .range([height, 0]); // output

// d3's line generator
var cdf_line_generator = d3.line()
    .x(function(d) { return xScale(d.x); }) // set the x values for the line generator
    .y(function(d) { return cdf_yScale(d.y); }) // set the y values for the line generator

var pdf_line_generator = d3.line()
    .x(function(d) { return xScale(d.x); }) // set the x values for the line generator
    .y(function(d) { return pdf_yScale(d.y); }) // set the y values for the line generator

// Add the SVG to the graph div and employ margin conventions
var cdf_svg = d3.select("#cdf_plot").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var pdf_svg = d3.select("#pdf_plot").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Create the CDF x axis in a group tag
cdf_svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

// Create the CDF y axis in a group tag
cdf_svg.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(cdf_yScale)); // Create an axis component with d3.axisLeft

// text label for the CDF y axis
cdf_svg.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 0 - margin.left)
  .attr("x",0 - (height / 2))
  .attr("dy", "1em")
  .style("text-anchor", "middle")
  .text("Probability");

// CDF plot title
cdf_svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text("CDF (cumulative distribution function)");

// Create the PDF x axis in a group tag
pdf_svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

// Create the PDF y axis in a group tag
pdf_svg.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(pdf_yScale)); // Create an axis component with d3.axisLeft

// text label for the y axis
pdf_svg.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 0 - margin.left)
  .attr("x",0 - (height / 2))
  .attr("dy", "1em")
  .style("text-anchor", "middle")
  .text("Density");

// PDF plot title
pdf_svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text("PDF (probability density function)");

// Append the path, bind the data, and call the line generator
plane_cdf = cdf_svg.append("g").attr('class','plane')
plane_pdf = pdf_svg.append("g").attr('class','plane')

plane_cdf.append("path")
    .datum(cdf_data) // Binds data to the line
    .attr("class", "line") // Assign a class for styling
    .attr("d", cdf_line_generator); // Calls the line generator

plane_pdf.append("path")
    .datum(pdf_data) // Binds data to the line
    .attr("class", "line") // Assign a class for styling
    .attr("d", pdf_line_generator); // Calls the line generator



quantile_vertical_lines = new Array()
quantile_horizontal_lines = new Array()
pdf_quantile_vertical_lines = new Array()

var cross = {
  draw: function draw(context, size) {
    context.moveTo(-size, 0)
    context.lineTo(size,0)
    context.moveTo(0, -size)
    context.lineTo(0,size)
  }
}

DataPointCrosses = new Array()
DataPointCircles = new Array()

function drawDataPoints(x, y, index) {
    DataPointCrosses.push(
        plane_cdf.append("path")
            .attr('d', d3.symbol().type(cross).size(10))
            .attr('transform', 'translate(' + xScale(x) + ',' + cdf_yScale(y) + ')')
            .attr('class', 'dataPointCross')
            .attr('quantile_index', index)
    )

    DataPointCircles.push(
        plane_cdf.append("path")
            .attr('d', d3.symbol().type(d3.symbolCircle).size(6000))
            .attr('transform', 'translate(' + xScale(x) + ',' + cdf_yScale(y) + ')')
            .attr('class', 'dataPointCircle')
            .attr('quantile_index', index)
    )
}

for (let i = 0; i < quantiles.length; i++) {
    drawDataPoints(quantiles[i].x,quantiles[i].y, i)
}

for (let i = 0; i < quantiles.length; i++) {
    DataPointCircles[i].call(
        d3.drag()
            .on("drag", draggedDataPoint)
            .on("end", endDragDataPoint)
    )
}
for (let i = 0; i < quantiles.length; i++) {
    DataPointCircles[i].on("click", removePointByClick)
}

function draggedDataPoint(event,d) {
    i = parseInt(d3.select(this).attr('quantile_index'))
    y_drag = cdf_yScale.invert(event.y)
    x_drag = xScale.invert(event.x)
    DataPointCircles[i].attr('transform','translate(' + event.x + ',' + event.y + ')')
    DataPointCrosses[i].attr('transform','translate(' + event.x + ',' + event.y + ')')

    document.getElementById('pairs-' + i + '-Q').value = x_drag.toPrecision(3)
    document.getElementById('pairs-' + i + '-P').value = y_drag.toPrecision(3)

}

function endDragDataPoint(event,d){
    document.getElementById('dataInputForm').submit()
}


function drawQuantileLines() {
    for (let i = 0; i < quantiles.length; i++) {
        quantile = quantiles[i]

        // Draw on the CDF
        quantile_vertical_lines.push(
            plane_cdf.append("rect")
                .attr('x',xScale(quantile.x) - 3/2)
                .attr('y',cdf_yScale(quantile.y))
                .attr('width', 3)
                .attr('height',cdf_yScale(1-quantile.y))
                .attr('class', 'quantile_rect')
                .attr('quantile_index',i).attr('quantile_line_direction','vertical')
                .attr('x_data',quantile.x)
        )


        quantile_horizontal_lines.push(
            plane_cdf.append("rect")
                .attr('x',xScale(cdf_metadata.xmin))
                .attr('y',cdf_yScale(quantile.y) - 3/2)
                .attr('width', xScale(quantile.x))
                .attr('height',3)
                .attr('class', 'quantile_rect')
                .attr('quantile_index',i).attr('quantile_line_direction','horizontal')
                .attr('y_data',quantile.y)
        )

        // Draw on the PDF
        pdf_quantile_vertical_lines.push(
            plane_pdf.append("rect")
                .attr('x',xScale(quantile.x) - 3/2)
                .attr('y',pdf_yScale(maximum_density_to_display))
                .attr('width', 3)
                .attr('height',height)
                .attr('class', 'quantile_rect')
                .attr('quantile_index',i).attr('quantile_line_direction','vertical')
                .attr('x_data',quantile.x)
        )
    }
}
function moveQuantileLines(i, coord, dragDirection) {
    if (dragDirection == 'horizontally'){
        // Redraw on the CDF
        quantile_vertical_lines[i].attr('x',xScale(coord) - 3/2)
        quantile_horizontal_lines[i].attr('width',xScale(coord))

        // Redraw on the PDF
        pdf_quantile_vertical_lines[i].attr('x',xScale(coord) - 3/2)
    }

    if (dragDirection == 'vertically'){
        // Redraw on the CDF
        quantile_horizontal_lines[i].attr('y',cdf_yScale(coord) - 3/2)
        quantile_vertical_lines[i].attr('height',cdf_yScale(1-coord))
        quantile_vertical_lines[i].attr('y',cdf_yScale(coord))
    }
}

drawQuantileLines()

function dragged_horizontally(event,d) {
        i = parseInt(d3.select(this).attr('quantile_index'))
        x_drag = xScale.invert(event.x)

        quantile_vertical_lines_sorted = quantile_vertical_lines.concat().sort((a, b) => parseFloat(a.attr('x_data')) - parseFloat(b.attr('x_data')))
        i_sorted = quantile_vertical_lines_sorted.findIndex(element => element.attr('x_data') === d3.select(this).attr('x_data'))

        if (i_sorted<quantiles.length-1) {
            maxdrag = parseFloat(quantile_vertical_lines_sorted[i_sorted + 1].attr('x_data'))
        }
        else {
            maxdrag = Infinity
        }
        if (i_sorted>0) {
            mindrag = parseFloat(quantile_vertical_lines_sorted[i_sorted - 1].attr('x_data'))
        }
        else {
            mindrag = -Infinity
        }

        if (event.sourceEvent.shiftKey) {
            start_x_dragged = parseFloat(quantile_vertical_lines[i].attr('x_data'))
             for (let j = 0; j < quantiles.length; j++) {
                 current_x = parseFloat(quantile_vertical_lines[j].attr('x_data'))
                 new_x = current_x+(x_drag-start_x_dragged)
                 console.log(new_x)
                 moveQuantileLines(j, new_x, 'horizontally')
                document.getElementById('pairs-' + j + '-Q').value = new_x.toPrecision(3)
             }
         }
         else {
             if (mindrag<x_drag && x_drag<maxdrag) {
                 moveQuantileLines(i, x_drag, 'horizontally')
                 document.getElementById('pairs-' + i + '-Q').value = x_drag.toPrecision(3)
             }
        }

    }
for (line of quantile_vertical_lines) {
    line.call(
        d3.drag()
            .on("drag", dragged_horizontally)
            .on("end",dragEnd)
    )
}

for (line of pdf_quantile_vertical_lines) {
    line.call(
        d3.drag()
            .on("drag", dragged_horizontally)
            .on("end",dragEnd)
    )
}

function dragged_vertically(event,d) {
        d3.select(this).style('stroke','black')
        i = parseInt(d3.select(this).attr('quantile_index'))
        y_drag = cdf_yScale.invert(event.y)

        quantile_horizontal_lines_sorted = quantile_horizontal_lines.concat().sort((a, b) => parseFloat(a.attr('y_data')) - parseFloat(b.attr('y_data')))
        i_sorted = quantile_horizontal_lines_sorted.findIndex(element => element.attr('y_data') === d3.select(this).attr('y_data'))
        if (i_sorted<quantiles.length-1) {
            maxdrag = parseFloat(quantile_horizontal_lines_sorted[i_sorted + 1].attr('y_data'))
        }
        else {
            maxdrag = 1
        }
        if (i_sorted>0) {
            mindrag = parseFloat(quantile_horizontal_lines_sorted[i_sorted - 1].attr('y_data'))
        }
        else {
            mindrag = 0
        }

        if (event.sourceEvent.shiftKey) {

            start_y_dragged = parseFloat(quantile_horizontal_lines[i].attr('y_data'))
             for (let j = 0; j < quantiles.length; j++) {
                 current_y = parseFloat(quantile_horizontal_lines[j].attr('y_data'))
                 if (current_y<.5) {
                     ratio = y_drag/start_y_dragged
                     new_y = current_y*ratio
                 }
                 else {
                     ratio = (1-y_drag)/(1-start_y_dragged)
                     new_y = 1- (1-current_y)*ratio
                 }
                 if (0<new_y && new_y<1) {
                     moveQuantileLines(j, new_y, 'vertically')
                     document.getElementById('pairs-' + j + '-P').value = new_y.toPrecision(3)
                 }
             }
        }
        else {
            if (mindrag<y_drag && y_drag<maxdrag) {
                moveQuantileLines(i, y_drag, 'vertically')
                document.getElementById('pairs-' + i + '-P').value = y_drag.toPrecision(3)
            }
        }
    }
for (line of quantile_horizontal_lines) {
    line.call(
        d3.drag()
            .on("drag", dragged_vertically)
            .on("end",dragEnd)

    )
}
d3.selectAll('.quantile_line').lower()

function dragEnd(){
    document.getElementById('plot_custom_domain_bool').checked = true
    document.getElementById('plot_custom_domain_FromTo-From').value = cdf_metadata.xmin.toPrecision(3)
    document.getElementById('plot_custom_domain_FromTo-To').value = cdf_metadata.xmax.toPrecision(3)
    document.getElementById('dataInputForm').submit()

}


// Mouseover tooltip
// const mouseOverRect = cdf_svg.append("rect")
//         .attr("class", "overlay")
//         .attr("width", width)
//         .attr("height", height)
//         .on("mouseover", function() { mouseOverFocus.style("display", null); })
//         .on("mouseout", function() { mouseOverFocus.style("display", "none"); })
//         .on("mousemove", mousemove);
//
// var mouseOverFocus = cdf_svg.append("g")
//         .attr("class", "focus")
//         .style("display", "none");
//
// mouseOverFocus.append("circle")
//     .attr("r", 6)
//     .attr("class",'hover_circle')
//
// mouseOverFocus.append("text")
//     .attr("x", 15)
//     .attr("dy", ".31em");
//
// const cdf_bisector = d3.bisector(d => d.x).left
//
// function mousemove(event,datum) {
//       var x0 = xScale.invert(event.layerX - margin.left),
//           i = cdf_bisector(cdf_data, x0, 1),
//           d0 = cdf_data[i - 1],
//           d1 = cdf_data[i],
//           d = x0 - d0.x > d1.x - x0 ? d1 : d0;
//       mouseOverFocus.attr("transform", "translate(" + xScale(d.x) + "," + cdf_yScale(d.y) + ")");
//       mouseOverFocus.select("text").text(function() {
//           return d.x.toPrecision(3).toString()+"; "+d.y.toPrecision(3).toString();
//       });
//     }
// d3.select(mouseOverRect).node().lower() // move below the rest, otherwise we lose interactivity with the plot


d3.select("#cdf_plot").on("click", addPointByClick)
function addPointByClick(event,d){
    if (event.shiftKey) {
        x_click = xScale.invert(event.layerX - margin.left)
        y_click = cdf_yScale.invert(event.layerY - margin.top)
        console.log(x_click, y_click)
        drawDataPoints(x_click, y_click, null)

        npairs = document.getElementById("nb_pairs").value
        console.log(npairs)
        document.getElementById("pairs-" + (npairs) + "-P").value = y_click.toPrecision(3)
        document.getElementById("pairs-" + (npairs) + "-Q").value = x_click.toPrecision(3)

        document.getElementById("nb_pairs").value = parseInt(document.getElementById("nb_pairs").value) + 1
        display_nb_pairs()
        document.getElementById("dataInputForm").submit()
    }
}

function removePointByClick(event,d){
    if (parseInt(document.getElementById("nb_pairs").value)>2) {
        if (event.altKey) {
            i = parseInt(d3.select(this).attr('quantile_index'))
            d3.selectAll("path[quantile_index=  '"+i+"' ].dataPointCross").remove() // remove via JS for immediate visual feedback
            d3.selectAll("path[quantile_index=  '"+i+"' ].dataPointCircle").remove()
            removePair(i)
        }
    }
}