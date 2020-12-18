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
    .domain([pdf_metadata.ymin, pdf_metadata.ymax]) // input
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
function drawGreekCross(x,y){
    plane_cdf.append("path")
        .attr('d',d3.symbol().type(cross).size(10))
        .attr('transform','translate('+xScale(x)+','+cdf_yScale(y)+')')
        .attr('class','dataPointCross')
}

for (const quantile of quantiles) {
    drawGreekCross(quantile.x,quantile.y)
}

function drawQuantileLines() {
    console.log("running drawQuantileLines")
    for (let i = 0; i < quantiles.length; i++) {
        // Draw on the CDF
        quantile = quantiles[i]
        quantile_vertical_line_0 = {'x': quantile.x, 'y': cdf_metadata.ymin}
        quantile_vertical_line_1 = {'x': quantile.x, 'y': quantile.y}

        quantile_horizontal_line_0 = {'x': cdf_metadata.xmin, 'y': quantile.y}
        quantile_horizontal_line_1 = {'x': quantile.x, 'y': quantile.y}

        quantile_vertical_lines.push(
            plane_cdf.append("path")
                .datum([quantile_vertical_line_0, quantile_vertical_line_1])
                .attr('d', cdf_line_generator)
                .attr('class', 'line quantile_line')
                .attr('quantile_index',i).attr('quantile_line_direction','vertical'))

        quantile_horizontal_lines.push(
            plane_cdf.append("path")
                .datum([quantile_horizontal_line_0, quantile_horizontal_line_1])
                .attr('d', cdf_line_generator)
                .attr('class', 'line quantile_line')
                .attr('quantile_index',i).attr('quantile_line_direction','horizontal'))

        // Draw on the PDF
        pdf_quantile_vertical_line_0 = {'x': quantile.x, 'y': pdf_metadata.ymin}
        pdf_quantile_vertical_line_1 = {'x': quantile.x, 'y': pdf_metadata.ymax}

        pdf_quantile_vertical_lines.push(
            plane_pdf.append("path")
                .datum([pdf_quantile_vertical_line_0, pdf_quantile_vertical_line_1])
                .attr('d', pdf_line_generator)
                .attr('class', 'line pdf_quantile_line')
                .attr('quantile_index',i).attr('quantile_line_direction','vertical'))
    }
}
function redrawQuantileLines(i,coord,dragDirection) {
    existing_horizontal = quantile_horizontal_lines[i].data()[0]
    existing_vertical = quantile_vertical_lines[i].data()[0]
    if (dragDirection == 'horizontally'){
        // Redraw on the CDF
        quantile_vertical_line_0 = {'x': coord, 'y': cdf_metadata.ymin}
        quantile_vertical_line_1 = {'x': coord, 'y': existing_vertical[1].y}

        quantile_vertical_lines[i] =
            d3.select(quantile_vertical_lines[i].node())
                .datum([quantile_vertical_line_0, quantile_vertical_line_1])
                .attr('d', cdf_line_generator)
                .attr('class', 'line quantile_line')

        quantile_horizontal_line_0 = existing_horizontal[0]
        quantile_horizontal_line_1 = {'x': coord, 'y': existing_horizontal[1].y}

        quantile_horizontal_lines[i] =
            d3.select(quantile_horizontal_lines[i].node())
                .datum([quantile_horizontal_line_0, quantile_horizontal_line_1])
                .attr('d', cdf_line_generator)
                .attr('class', 'line quantile_line')

        // Redraw on the PDF
        pdf_quantile_vertical_line_0 = {'x': coord, 'y': pdf_metadata.ymin}
        pdf_quantile_vertical_line_1 = {'x': coord, 'y': pdf_metadata.ymax}

        pdf_quantile_vertical_lines[i] =
            d3.select(pdf_quantile_vertical_lines[i].node())
                .datum([pdf_quantile_vertical_line_0, pdf_quantile_vertical_line_1])
                .attr('d', pdf_line_generator)
                .attr('class', 'line pdf_quantile_line')
    }

    if (dragDirection == 'vertically'){
        quantile_horizontal_line_0 = {'x': cdf_metadata.xmin, 'y': coord}
        quantile_horizontal_line_1 = {'x': existing_horizontal[1].x, 'y': coord}

        quantile_horizontal_lines[i] =
            d3.select(quantile_horizontal_lines[i].node())
                .datum([quantile_horizontal_line_0, quantile_horizontal_line_1])
                .attr('d', cdf_line_generator)
                .attr('class', 'line quantile_line')

        quantile_vertical_line_0 = existing_vertical[0]
        quantile_vertical_line_1 = {'x': existing_vertical[1].x, 'y': coord}

        quantile_vertical_lines[i] =
            d3.select(quantile_vertical_lines[i].node())
                .datum([quantile_vertical_line_0, quantile_vertical_line_1])
                .attr('d', cdf_line_generator)
                .attr('class', 'line quantile_line')

    }
}

drawQuantileLines()

function dragged_horizontally(event,d) {
        i = parseInt(d3.select(this).attr('quantile_index'))
        d3.select(quantile_vertical_lines[i].node()).style('stroke','black')
        d3.select(pdf_quantile_vertical_lines[i].node()).style('stroke','black')
        x = xScale.invert(event.x)
        redrawQuantileLines(i,x,'horizontally')
        document.getElementById('pairs-'+i+'-Q').value = x.toPrecision(3)
    }
for (line of quantile_vertical_lines) {
    line.call(
        d3.drag()
            .on("drag", dragged_horizontally)
            .on("end",dragEnd)
    )
}

function dragged_vertically(event,d) {
        d3.select(this).style('stroke','black')
        i = parseInt(d3.select(this).attr('quantile_index'))
        y = cdf_yScale.invert(event.y)
        if (0<=y && y<=1) {
            redrawQuantileLines(i,y,'vertically')
            document.getElementById('pairs-'+i+'-P').value = y.toPrecision(3)
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
    document.getElementById('plot_custom_domain_left').value = cdf_metadata.xmin.toPrecision(3)
    document.getElementById('plot_custom_domain_right').value = cdf_metadata.xmax.toPrecision(3)
    document.getElementById('dataInputForm').submit()

}