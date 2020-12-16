// 2. Use the margin convention practice
var margin = {top: 50, right: 50, bottom: 50, left: 50}
  , width = 700 - margin.left - margin.right // Use a hard-coded width for now, improve later
  , height = 700 - margin.top - margin.bottom; // Use a hard-coded height for now, improve later

// 8. An array of objects of length N. Each object has key -> value pair, the key being "y" and the value is a random number
var dataset = data

// The number of datapoints
var n = data.length

// 5. X scale will use the index of our data
var xScale = d3.scaleLinear()
    .domain([metadata.xmin, metadata.xmax]) // input
    .range([0, width]); // output

// 6. Y scale will use the randomly generate number
var yScale = d3.scaleLinear()
    .domain([metadata.ymin, metadata.ymax]) // input
    .range([height, 0]); // output

// 7. d3's line generator
var line_generator = d3.line()
    .x(function(d) { return xScale(d.x); }) // set the x values for the line generator
    .y(function(d) { return yScale(d.y); }) // set the y values for the line generator

// 1. Add the SVG to the graph div and employ #2
var svg = d3.select("#graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// 3. Call the x axis in a group tag
svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

// 4. Call the y axis in a group tag
svg.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

// 9. Append the path, bind the data, and call the line generator
plane = svg.append("g").attr('class','plane')

plane.append("path")
    .datum(dataset) // 10. Binds data to the line
    .attr("class", "line") // Assign a class for styling
    .attr("d", line_generator); // 11. Calls the line generator

plane.on('click',onclick)

onclick = function (event){
    x = xScale.invert(event.layerX - margin.left);
    y = yScale.invert(event.layerY - margin.top);
    console.log(x,y)
}

quantile_vertical_lines = new Array()
quantile_horizontal_lines = new Array()

var cross = {
  draw: function draw(context, size) {
    context.moveTo(-size, 0)
    context.lineTo(size,0)
    context.moveTo(0, -size)
    context.lineTo(0,size)
  }
}
function drawGreekCross(x,y){
    plane.append("path")
        .attr('d',d3.symbol().type(cross).size(10))
        .attr('transform','translate('+xScale(x)+','+yScale(y)+')')
        .attr('class','dataPointCross')
}

for (const quantile of quantiles) {
    drawGreekCross(quantile.x,quantile.y)
}

function drawQuantileLines() {
    console.log("running drawQuantileLines")
    for (let i = 0; i < quantiles.length; i++) {
        quantile = quantiles[i]
        quantile_vertical_line_0 = {'x': quantile.x, 'y': metadata.ymin}
        quantile_vertical_line_1 = {'x': quantile.x, 'y': quantile.y}

        quantile_horizontal_line_0 = {'x': metadata.xmin, 'y': quantile.y}
        quantile_horizontal_line_1 = {'x': quantile.x, 'y': quantile.y}

        quantile_vertical_lines.push(
            plane.append("path")
                .datum([quantile_vertical_line_0, quantile_vertical_line_1])
                .attr('d', line_generator)
                .attr('class', 'line quantile_line')
                .attr('quantile_index',i).attr('quantile_line_direction','vertical'))

        quantile_horizontal_lines.push(
            plane.append("path")
                .datum([quantile_horizontal_line_0, quantile_horizontal_line_1])
                .attr('d', line_generator)
                .attr('class', 'line quantile_line')
                .attr('quantile_index',i).attr('quantile_line_direction','horizontal'))
    }
}
function redrawQuantileLines(i,coord,dragDirection) {
    existing_horizontal = quantile_horizontal_lines[i].data()[0]
    existing_vertical = quantile_vertical_lines[i].data()[0]
    if (dragDirection == 'horizontally'){
        quantile_vertical_line_0 = {'x': coord, 'y': metadata.ymin}
        quantile_vertical_line_1 = {'x': coord, 'y': existing_vertical[1].y}

        quantile_vertical_lines[i] =
            d3.select(quantile_vertical_lines[i].node())
                .datum([quantile_vertical_line_0, quantile_vertical_line_1])
                .attr('d', line_generator)
                .attr('class', 'line quantile_line')

        quantile_horizontal_line_0 = existing_horizontal[0]
        quantile_horizontal_line_1 = {'x': coord, 'y': existing_horizontal[1].y}

        quantile_horizontal_lines[i] =
            d3.select(quantile_horizontal_lines[i].node())
                .datum([quantile_horizontal_line_0, quantile_horizontal_line_1])
                .attr('d', line_generator)
                .attr('class', 'line quantile_line')
    }

    if (dragDirection == 'vertically'){
        quantile_horizontal_line_0 = {'x': metadata.xmin, 'y': coord}
        quantile_horizontal_line_1 = {'x': existing_horizontal[1].x, 'y': coord}

        quantile_horizontal_lines[i] =
            d3.select(quantile_horizontal_lines[i].node())
                .datum([quantile_horizontal_line_0, quantile_horizontal_line_1])
                .attr('d', line_generator)
                .attr('class', 'line quantile_line')

        quantile_vertical_line_0 = existing_vertical[0]
        quantile_vertical_line_1 = {'x': existing_vertical[1].x, 'y': coord}

        quantile_vertical_lines[i] =
            d3.select(quantile_vertical_lines[i].node())
                .datum([quantile_vertical_line_0, quantile_vertical_line_1])
                .attr('d', line_generator)
                .attr('class', 'line quantile_line')

    }
}

drawQuantileLines()

function dragged_horizontally(event,d) {
        d3.select(this).style('stroke','black')
        i = parseInt(d3.select(this).attr('quantile_index'))
        x = xScale.invert(event.x)
        redrawQuantileLines(i,x,'horizontally')
        document.getElementById('pairs-'+i+'-Q').value = x
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
        y = yScale.invert(event.y)
        if (0<=y && y<=1) {
            redrawQuantileLines(i,y,'vertically')
            document.getElementById('pairs-'+i+'-P').value = y
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
    document.getElementById('plot_custom_domain_left').value = metadata.xmin
    document.getElementById('plot_custom_domain_right').value = metadata.xmax
    document.getElementById('dataInputForm').submit()

}