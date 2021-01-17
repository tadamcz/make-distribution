function makePlot(distributionIndex,nDistributions) {

    // Define plot sizes
    minHeighShowTitle = 200
    if (maxHeightPerPlot>minHeighShowTitle) {
        margin = {
            top: maxHeightPerPlot / 10,
            right: 70,
            bottom: maxHeightPerPlot / 10,
            left: 70
        }
    }
    else {
        margin = {
            top: 20,
            right: 70,
            bottom: 20,
            left: 70
        }
    }

    width = 700 - margin.left - margin.right
    height = Math.min(700 - margin.top - margin.bottom, maxHeightPerPlot - margin.top - margin.bottom)

    if (distributionIndex === 99) {
        cdf_data = mixturePlotData.cdf_data
        cdf_metadata = mixturePlotData.cdf_metadata
        pdf_data = mixturePlotData.pdf_data
        pdf_metadata = mixturePlotData.pdf_metadata
        quantiles = mixturePlotData.quantiles
        maximum_density_to_display = mixturePlotData.maximum_density_to_display

        cdf_plot_div = document.getElementById('mixture_cdf_plot')
        pdf_plot_div = document.getElementById('mixture_pdf_plot')

        nDistributions = parseInt($('#n_distributions_to_display').val())


    } else {
        cdf_data = plotData[distributionIndex].cdf_data
        cdf_metadata = plotData[distributionIndex].cdf_metadata
        pdf_data = plotData[distributionIndex].pdf_data
        pdf_metadata = plotData[distributionIndex].pdf_metadata
        quantiles = plotData[distributionIndex].quantiles
        maximum_density_to_display = plotData[distributionIndex].maximum_density_to_display
        // pairs_form_indices= plotData[distributionIndex].pairs_form_indices
        lbound = plotData[distributionIndex].lbound
        ubound = plotData[distributionIndex].ubound

        cdf_plot_div = document.getElementById('cdf_plot' + distributionIndex)
        pdf_plot_div = document.getElementById('pdf_plot' + distributionIndex)

        UIObjs[distributionIndex].quantile_vertical_lines = new Array()
        UIObjs[distributionIndex].quantile_horizontal_lines = new Array()
        UIObjs[distributionIndex].pdf_quantile_vertical_lines = new Array()
        UIObjs[distributionIndex].DataPointCrosses = new Array()
        UIObjs[distributionIndex].DataPointCircles = new Array()
        //
        // diFrag = "distributions-" + distributionIndex + "-" // fragment of WTForms-generated IDs under this distribution
        // diSelector = '#distribution' + distributionIndex // selector for the ID generated in Jinja using <div class="flexbox" id="distribution{{distribution_index}}">
    }


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
        .domain([0, 1]) // input
        .range([height, 0]); // output

    var pdf_yScale = d3.scaleLinear()
        .domain([pdf_metadata.ymin, maximum_density_to_display]) // input
        .range([height, 0]); // output

// d3's line generator
    var cdf_line_generator = d3.line()
        .x(function (d) {
            return xScale(d.x);
        }) // set the x values for the line generator
        .y(function (d) {
            return cdf_yScale(d.y);
        }) // set the y values for the line generator

    var pdf_line_generator = d3.line()
        .x(function (d) {
            return xScale(d.x);
        }) // set the x values for the line generator
        .y(function (d) {
            if (isFinite(d.y)) {
                return pdf_yScale(d.y)
            } else {
                return -100 * height
            }
        }) // set the y values for the line generator

// Add the SVG to the graph div and employ margin conventions
    var cdf_svg = d3.select(cdf_plot_div).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var pdf_svg = d3.select(pdf_plot_div).append("svg")
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
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Probability");

// CDF plot title
    if (maxHeightPerPlot>minHeighShowTitle) {
        cdf_svg.append("text")
            .attr("x", (width / 2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text("CDF (cumulative distribution function)");
    }

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
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Density");

// PDF plot title
    if (maxHeightPerPlot>minHeighShowTitle) {
        pdf_svg.append("text")
            .attr("x", (width / 2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text("PDF (probability density function)");
    }

// Append the path, bind the data, and call the line generator
    plane_cdf = cdf_svg.append("g").attr('class', 'plane')
    plane_pdf = pdf_svg.append("g").attr('class', 'plane')

    plane_cdf.append("path")
        .datum(cdf_data) // Binds data to the line
        .attr("class", "line") // Assign a class for styling
        .attr("d", cdf_line_generator); // Calls the line generator

    plane_pdf.append("path")
        .datum(pdf_data) // Binds data to the line
        .attr("class", "line") // Assign a class for styling
        .attr("d", pdf_line_generator); // Calls the line generator


    if (distributionIndex !== 99) {
        var cross = {
            draw: function draw(context, size) {
                context.moveTo(-size, 0)
                context.lineTo(size, 0)
                context.moveTo(0, -size)
                context.lineTo(0, size)
            }
        }


        function drawDataPoints(x, y, index) {
            UIObjs[distributionIndex].DataPointCrosses.push(
                plane_cdf.append("path")
                    .attr('d', d3.symbol().type(cross).size(10))
                    .attr('transform', 'translate(' + xScale(x) + ',' + cdf_yScale(y) + ')')
                    .attr('class', 'dataPointCross')
                    .attr('quantile_index', index)
            )

            UIObjs[distributionIndex].DataPointCircles.push(
                plane_cdf.append("path")
                    .attr('d', d3.symbol().type(d3.symbolCircle).size(6000))
                    .attr('transform', 'translate(' + xScale(x) + ',' + cdf_yScale(y) + ')')
                    .attr('class', 'dataPointCircle')
                    .attr('quantile_index', index)
                    .on("mouseover", dataPointCircleHovered)
                    .on("mouseout", dataPointCircleHoveredEnd)
            )
        }

        function dataPointCircleHovered() {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)
            pairs_form_indices = plotData[distributionIndex].pairs_form_indices

            i = d3.select(this).attr('quantile_index')
            i = pairs_form_indices[i]
            distributionDiv.find('.pair' + i).css('background', 'lightgray')
        }

        function dataPointCircleHoveredEnd() {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)
            pairs_form_indices = plotData[distributionIndex].pairs_form_indices

            i = d3.select(this).attr('quantile_index')
            i = pairs_form_indices[i]
            distributionDiv.find('.pair' + i).css('background', 'none')
        }

        for (let i = 0; i < quantiles.length; i++) {
            drawDataPoints(quantiles[i].x, quantiles[i].y, i)
            UIObjs[distributionIndex].DataPointCircles[i].call(
                d3.drag()
                    .on("start", dragPointStart)
                    .on("drag", draggedDataPoint)
                    .on("end", endDragDataPoint)
            )
            UIObjs[distributionIndex].DataPointCircles[i].on("click", removePointByClick) // todo: fix broken removePointByClick functionality
        }

        function dragPointStart() {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)

            i = parseInt(d3.select(this).attr('quantile_index'))
            UIObjs[distributionIndex].DataPointCrosses[i].raise()
            UIObjs[distributionIndex].DataPointCircles[i].raise()
        }

        function draggedDataPoint(event, d) {
            if (!event.sourceEvent.altKey) {
                distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
                distributionDiv = $('#distribution' + distributionIndex)
                pairs_form_indices = plotData[distributionIndex].pairs_form_indices


                i = parseInt(d3.select(this).attr('quantile_index'))
                y_drag = cdf_yScale.invert(event.y)
                x_drag = xScale.invert(event.x)

                UIObjs[distributionIndex].DataPointCircles[i].attr('transform', 'translate(' + event.x + ',' + event.y + ')')
                UIObjs[distributionIndex].DataPointCrosses[i].attr('transform', 'translate(' + event.x + ',' + event.y + ')')

                distributionDiv.find('.pair' + pairs_form_indices[i] + ' [fieldtype=Q]').val(x_drag.toPrecision(3))
                distributionDiv.find('.pair' + pairs_form_indices[i] + ' [fieldtype=P]').val(y_drag.toPrecision(3))
            }
        }

        function endDragDataPoint(event, d) {
            if (!event.sourceEvent.altKey) {
                document.getElementById('dataInputForm').submit()
            }
        }


        function drawQuantileLines() {
            for (let i = 0; i < quantiles.length; i++) {
                quantile = quantiles[i]

                // Draw on the CDF
                UIObjs[distributionIndex].quantile_vertical_lines.push(
                    plane_cdf.append("rect")
                        .attr('x', xScale(quantile.x) - 3 / 2)
                        .attr('y', cdf_yScale(quantile.y))
                        .attr('width', 3)
                        .attr('height', cdf_yScale(1 - quantile.y))
                        .attr('class', 'quantile_rect')
                        .attr('quantile_index', i).attr('quantile_line_direction', 'vertical')
                        .attr('x_data', quantile.x)
                        .lower() // to make sure it is below the UIObjs[distributionIndex].DataPointCircles

                )


                UIObjs[distributionIndex].quantile_horizontal_lines.push(
                    plane_cdf.append("rect")
                        .attr('x', xScale(cdf_metadata.xmin))
                        .attr('y', cdf_yScale(quantile.y) - 3 / 2)
                        .attr('width', xScale(quantile.x))
                        .attr('height', 3)
                        .attr('class', 'quantile_rect')
                        .attr('quantile_index', i).attr('quantile_line_direction', 'horizontal')
                        .attr('y_data', quantile.y)
                        .lower() // to make sure it is below the UIObjs[distributionIndex].DataPointCircles

                )

                // Draw on the PDF
                UIObjs[distributionIndex].pdf_quantile_vertical_lines.push(
                    plane_pdf.append("rect")
                        .attr('x', xScale(quantile.x) - 3 / 2)
                        .attr('y', pdf_yScale(maximum_density_to_display))
                        .attr('width', 3)
                        .attr('height', height)
                        .attr('class', 'quantile_rect')
                        .attr('quantile_index', i).attr('quantile_line_direction', 'vertical')
                        .attr('x_data', quantile.x)
                )
            }
        }

        drawQuantileLines()

        function moveQuantileLines(i, coord, dragDirection) {
            if (dragDirection == 'horizontally') {
                // Redraw on the CDF
                UIObjs[distributionIndex].quantile_vertical_lines[i].attr('x', xScale(coord) - 3 / 2)
                UIObjs[distributionIndex].quantile_horizontal_lines[i].attr('width', xScale(coord))

                // Redraw on the PDF
                UIObjs[distributionIndex].pdf_quantile_vertical_lines[i].attr('x', xScale(coord) - 3 / 2)
            }

            if (dragDirection == 'vertically') {
                // Redraw on the CDF
                UIObjs[distributionIndex].quantile_horizontal_lines[i].attr('y', cdf_yScale(coord) - 3 / 2)
                UIObjs[distributionIndex].quantile_vertical_lines[i].attr('height', cdf_yScale(1 - coord))
                UIObjs[distributionIndex].quantile_vertical_lines[i].attr('y', cdf_yScale(coord))
            }
        }

        function dragged_horizontally(event, d) {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)
            pairs_form_indices = plotData[distributionIndex].pairs_form_indices
            quantiles = plotData[distributionIndex].quantiles


            i_of_dragged = parseInt(d3.select(this).attr('quantile_index'))
            x_drag = xScale.invert(event.x)

            UIObjs[distributionIndex].quantile_vertical_lines_sorted = UIObjs[distributionIndex].quantile_vertical_lines.concat().sort((a, b) => parseFloat(a.attr('x_data')) - parseFloat(b.attr('x_data')))
            i_sorted_of_dragged = UIObjs[distributionIndex].quantile_vertical_lines_sorted.findIndex(element => element.attr('x_data') === d3.select(this).attr('x_data'))

            sorted_indices = indicesSortedByAttribute(UIObjs[distributionIndex].quantile_vertical_lines, 'x_data')

            if (i_sorted_of_dragged < quantiles.length - 1) {
                maxdrag = parseFloat(UIObjs[distributionIndex].quantile_vertical_lines_sorted[i_sorted_of_dragged + 1].attr('x_data'))
            } else {
                maxdrag = ubound
            }
            if (i_sorted_of_dragged > 0) {
                mindrag = parseFloat(UIObjs[distributionIndex].quantile_vertical_lines_sorted[i_sorted_of_dragged - 1].attr('x_data'))
            } else {
                mindrag = lbound
            }
            start_x_dragged = parseFloat(UIObjs[distributionIndex].quantile_vertical_lines[i_of_dragged].attr('x_data'))
            if (event.sourceEvent.shiftKey && !event.sourceEvent.altKey) {
                for (let j = 0; j < quantiles.length; j++) {
                    dragMultipleHorizontally(j, x_drag, start_x_dragged, distributionIndex)
                }
            } else if (!event.sourceEvent.shiftKey && event.sourceEvent.altKey) {
                indices_to_drag = sorted_indices.slice(sorted_indices.findIndex(element => element === i_of_dragged))
                for (const j of indices_to_drag) {
                    dragMultipleHorizontally(j, x_drag, start_x_dragged, distributionIndex)

                }
            } else if (event.sourceEvent.shiftKey && event.sourceEvent.altKey) {
                indices_to_drag = sorted_indices.slice(0, sorted_indices.findIndex(element => element === i_of_dragged) + 1)
                for (const j of indices_to_drag) {
                    dragMultipleHorizontally(j, x_drag, start_x_dragged, distributionIndex)

                }
            } else {
                if (mindrag < x_drag && x_drag < maxdrag) {
                    moveQuantileLines(i_of_dragged, x_drag, 'horizontally')
                    distributionDiv.find('.pair' + pairs_form_indices[i_of_dragged] + ' [fieldtype=Q]').val(x_drag.toPrecision(3))
                }
            }

        }

        function dragMultipleHorizontally(j, x_drag, start_x_dragged, distributionIndex) {
            distributionDiv = $('#distribution' + distributionIndex)
            pairs_form_indices = plotData[distributionIndex].pairs_form_indices


            current_x = parseFloat(UIObjs[distributionIndex].quantile_vertical_lines[j].attr('x_data'))
            new_x = current_x + (x_drag - start_x_dragged)
            moveQuantileLines(j, new_x, 'horizontally')
            distributionDiv.find('.pair' + pairs_form_indices[j] + ' [fieldtype=Q]').val(new_x.toPrecision(3))
        }

        for (line of UIObjs[distributionIndex].quantile_vertical_lines) {
            line.call(
                d3.drag()
                    .on("drag", dragged_horizontally)
                    .on("end", dragEnd)
            )
        }
        for (line of UIObjs[distributionIndex].pdf_quantile_vertical_lines) {
            line.call(
                d3.drag()
                    .on("drag", dragged_horizontally)
                    .on("end", dragEnd)
            )
        }

        function dragged_vertically(event, d) {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)

            pairs_form_indices = plotData[distributionIndex].pairs_form_indices
            quantiles = plotData[distributionIndex].quantiles

            d3.select(this).style('stroke', 'black')
            i_of_dragged = parseInt(d3.select(this).attr('quantile_index'))
            y_drag = cdf_yScale.invert(event.y)

            UIObjs[distributionIndex].quantile_horizontal_lines_sorted = UIObjs[distributionIndex].quantile_horizontal_lines.concat().sort((a, b) => parseFloat(a.attr('y_data')) - parseFloat(b.attr('y_data')))
            i_sorted_of_dragged = UIObjs[distributionIndex].quantile_horizontal_lines_sorted.findIndex(element => element.attr('y_data') === d3.select(this).attr('y_data'))

            sorted_indices = indicesSortedByAttribute(UIObjs[distributionIndex].quantile_horizontal_lines, 'y_data')

            if (i_sorted_of_dragged < quantiles.length - 1) {
                maxdrag = parseFloat(UIObjs[distributionIndex].quantile_horizontal_lines_sorted[i_sorted_of_dragged + 1].attr('y_data'))
            } else {
                maxdrag = 1
            }
            if (i_sorted_of_dragged > 0) {
                mindrag = parseFloat(UIObjs[distributionIndex].quantile_horizontal_lines_sorted[i_sorted_of_dragged - 1].attr('y_data'))
            } else {
                mindrag = 0
            }

            start_y_dragged = parseFloat(UIObjs[distributionIndex].quantile_horizontal_lines[i_of_dragged].attr('y_data'))
            if (event.sourceEvent.shiftKey && !event.sourceEvent.altKey) {
                for (let j = 0; j < quantiles.length; j++) {
                    dragMultipleVertically(j, y_drag, start_y_dragged, distributionIndex)
                }
            } else if (!event.sourceEvent.shiftKey && event.sourceEvent.altKey) {
                indices_to_drag = sorted_indices.slice(sorted_indices.findIndex(element => element === i_of_dragged))
                for (const j of indices_to_drag) {
                    dragMultipleVertically(j, y_drag, start_y_dragged, distributionIndex)
                }
            } else if (event.sourceEvent.shiftKey && event.sourceEvent.altKey) {
                indices_to_drag = sorted_indices.slice(0, sorted_indices.findIndex(element => element === i_of_dragged) + 1)
                for (const j of indices_to_drag) {
                    dragMultipleVertically(j, y_drag, start_y_dragged, distributionIndex)
                }
            } else {
                if (mindrag < y_drag && y_drag < maxdrag) {
                    moveQuantileLines(i_of_dragged, y_drag, 'vertically')
                    distributionDiv.find('.pair' + pairs_form_indices[i_of_dragged] + ' [fieldtype=P]').val(y_drag.toPrecision(3))
                }
            }
        }

        function dragMultipleVertically(j, y_drag, start_y_dragged, distributionIndex) {
            distributionDiv = $('#distribution' + distributionIndex)
            pairs_form_indices = plotData[distributionIndex].pairs_form_indices

            current_y = parseFloat(UIObjs[distributionIndex].quantile_horizontal_lines[j].attr('y_data'))
            if (current_y < .5) {
                ratio = y_drag / start_y_dragged
                new_y = current_y * ratio
            } else {
                ratio = (1 - y_drag) / (1 - start_y_dragged)
                new_y = 1 - (1 - current_y) * ratio
            }
            if (0 < new_y && new_y < 1) {
                moveQuantileLines(j, new_y, 'vertically')
                distributionDiv.find('.pair' + pairs_form_indices[j] + ' [fieldtype=P]').val(new_y.toPrecision(3))
            }
        }

        for (line of UIObjs[distributionIndex].quantile_horizontal_lines) {
            line.call(
                d3.drag()
                    .on("drag", dragged_vertically)
                    .on("end", dragEnd)
            )
        }


        d3.selectAll('.quantile_line').lower()

        function dragEnd() {
            distributionDiv.find('[fieldtype=plot_custom_domain_bool]').attr('checked',true)
            distributionDiv.find('[fieldtype=plot_custom_domain_FromTo] [fieldtype=From]').val(cdf_metadata.xmin.toPrecision(3))
            distributionDiv.find('[fieldtype=plot_custom_domain_FromTo] [fieldtype=To]').val(cdf_metadata.xmax.toPrecision(3))


            if (nDistributions>1) {
                $('#mixture_domain_for_plot_FromTo-From').val(mixturePlotData.cdf_metadata.xmin.toPrecision(3))
                $('#mixture_domain_for_plot_FromTo-To').val(mixturePlotData.cdf_metadata.xmax.toPrecision(3))
            }

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


        d3.select(cdf_plot_div).on("click", addPointByClick)

        function addPointByClick(event, d) {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)


            npairs = parseInt(distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val())
            if (event.shiftKey && npairs < 10) {
                x_click = xScale.invert(event.layerX - margin.left)
                y_click = cdf_yScale.invert(event.layerY - margin.top)
                drawDataPoints(x_click, y_click, null)

                distributionDiv.find('.pair' + npairs + ' [fieldtype=P]').val(y_click.toPrecision(3))
                distributionDiv.find('.pair' + npairs + ' [fieldtype=Q]').val(x_click.toPrecision(3))

                distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val(npairs + 1)
                displayNbPairs()
                document.getElementById("dataInputForm").submit()
            }
        }

        function removePointByClick(event, d) {
            distributionIndex = $(this).closest('[distributionindex]').attr('distributionindex')
            distributionDiv = $('#distribution' + distributionIndex)
            pairs_form_indices = plotData[distributionIndex].pairs_form_indices


            if (parseInt(distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val()) > 2) {
                if (event.altKey) {
                    i = parseInt(d3.select(this).attr('quantile_index'))
                    console.log(i)
                    d3.selectAll("path[quantile_index=  '" + i + "' ].dataPointCross").remove() // remove via JS for immediate visual feedback
                    d3.selectAll("path[quantile_index=  '" + i + "' ].dataPointCircle").remove()
                    removePair(pairs_form_indices[i], distributionIndex)
                }
            }
        }

        function indicesSortedByAttribute(array, attribute) {
            // make list with indices and values
            indexedArray = array.map(function (e, i) {
                return {ind: i, val: e}
            });
            // sort index/value couples, based on values
            indexedArray.sort(function (x, y) {
                return parseFloat(x.val.attr(attribute)) > parseFloat(y.val.attr(attribute)) ? 1 : parseFloat(x.val.attr(attribute)) === parseFloat(y.val.attr(attribute)) ? 0 : -1
            });
            // return list keeping only indices
            return indexedArray.map(function (e) {
                return e.ind
            });
        }
    }
}
